"""
05_main.py
Projeto Aplicado I — AV03 (MVP Parte 1) | Schulz S.A.
Equipe: Marx Braga Camilo, Gladson Goulart,Carla Tayna, Yorman Hernandez
Classe principal de demonstração: instanciação dos objetos, INSERT,
UPDATE, DELETE, SELECT com JOIN e exibição do relatório de calibração.
"""

import importlib.util
import sys
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("classes_04", PASTA / "04_classes.py")
_classes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_classes)

ConexaoSQLite = _classes.ConexaoSQLite
Tecnico = _classes.Tecnico
Equipamento = _classes.Equipamento
Medicao = _classes.Medicao
TecnicoDAO = _classes.TecnicoDAO
EquipamentoDAO = _classes.EquipamentoDAO
MedicaoDAO = _classes.MedicaoDAO
ErroValidacao = _classes.ErroValidacao
ErroPersistencia = _classes.ErroPersistencia
garantir_coluna_matricula = _classes.garantir_coluna_matricula

DB = str(PASTA / "schulz_calibracao.db")
SQL_DDL = PASTA / "03_banco.sql"


def data_br(data_iso: str) -> str:
    return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def linha(char: str = "-", largura: int = 132) -> str:
    return char * largura


def imprimir_relatorio(linhas: list) -> None:
    cabecalho = (
        f"{'ID':>4} {'CÓDIGO':<11} {'EQUIPAMENTO':<20} {'TÉCNICO':<16} "
        f"{'SETOR':<13} {'NOMINAL':>8} {'TOL(±)':>7} {'MED1':>8} {'MED2':>8} "
        f"{'MÉDIA':>8} {'DESVIO':>7} {'STATUS':<10} {'DATA':<10}"
    )
    print(linha("="))
    print("RELATÓRIO DE CALIBRAÇÃO — SCHULZ S.A. / LABORATÓRIO DE METROLOGIA")
    print(linha("="))
    print(cabecalho)
    print(linha())

    for r in linhas:
        print(
            f"{r['id_medicao']:>4} {r['codigo']:<11} {r['denominacao'][:20]:<20} "
            f"{r['tecnico'][:16]:<16} {r['setor'][:13]:<13} "
            f"{r['valor_nominal']:>8.3f} {r['tol_mais']:>7.3f} "
            f"{r['medida1']:>8.3f} {r['medida2']:>8.3f} "
            f"{r['media']:>8.3f} {r['desvio_padrao']:>7.4f} "
            f"{r['status']:<10} {data_br(r['data_medicao']):<10}"
        )

    print(linha())
    total = len(linhas)
    aprovadas = sum(1 for r in linhas if r["status"] == "APROVADO")
    taxa = (aprovadas / total * 100) if total else 0.0
    print(
        f"Total de medições: {total}   |   Aprovadas: {aprovadas}   |   "
        f"Reprovadas: {total - aprovadas}   |   Taxa de aprovação: {taxa:.1f}%"
    )
    print(linha("="))


class DemonstracaoMVP:
   
    def __init__(self, caminho_db: str = DB):
        self.caminho_db = caminho_db
        self.tecnico_dao = TecnicoDAO(caminho_db)
        self.equipamento_dao = EquipamentoDAO(caminho_db)
        self.medicao_dao = MedicaoDAO(caminho_db)
        # estado compartilhado entre as etapas
        self.metrologista = None
        self.solicitante = None
        self.paquimetro = None
        self.relogio = None
        self.medicoes = []

    # -------------------------------------------------------------
    # [1] Banco de dados
    # -------------------------------------------------------------
    def inicializar_banco(self) -> str:
        """Recria o banco a partir do 03_banco.sql e garante a coluna matricula."""
        if not SQL_DDL.exists():
            raise ErroPersistencia(f"Script DDL não encontrado: {SQL_DDL}")

        Path(self.caminho_db).unlink(missing_ok=True)
        script = SQL_DDL.read_text(encoding="utf-8")
        with ConexaoSQLite(self.caminho_db) as conn:
            conn.executescript(script)

        criada = garantir_coluna_matricula(self.caminho_db)
        extra = " (coluna 'matricula' adicionada por migração)" if criada else ""
        return f"banco recriado a partir do 03_banco.sql{extra}"

    # -------------------------------------------------------------
    # [2] Técnicos e equipamentos
    # -------------------------------------------------------------
    def etapa_cadastros(self) -> None:
        print("[2] Instanciando objetos de domínio e inserindo (INSERT)")

        self.metrologista = Tecnico(
            nome="José A. Rosa Jr.", papel="TECNICO", nome_setor="Metrologia",
            matricula="MT-0042",
        )
        self.solicitante = Tecnico(
            nome="Cleocir de Souza", papel="SOLICITANTE", nome_setor="Usinagem I",
        )
        self.tecnico_dao.inserir(self.metrologista)
        self.tecnico_dao.inserir(self.solicitante)

        self.paquimetro = Equipamento(
            codigo="703.1208", denominacao="Paquímetro digital",
            fabricante="Mitutoyo", modelo="500-196-30", categoria="Dimensional",
        )
        self.relogio = Equipamento(
            codigo="703.2210", denominacao="Relógio comparador",
            fabricante="Starrett", modelo="25-131J", categoria="Dimensional",
        )
        self.equipamento_dao.inserir(self.paquimetro)
        self.equipamento_dao.inserir(self.relogio)

        for objeto in (self.metrologista, self.solicitante,
                       self.paquimetro, self.relogio):
            print(f"    {objeto}")

        # Prova de que a matrícula foi persistida (SELECT por id)
        do_banco = self.tecnico_dao.buscar_por_id(self.metrologista.id_tecnico)
        print(f"    SELECT por id -> matrícula gravada no banco: {do_banco.matricula}\n")

    # -------------------------------------------------------------
    # [3] Medições: aprovada, reprovada e no limite exato
    # -------------------------------------------------------------
    def etapa_medicoes(self) -> None:
        print("[3] Registrando medições (INSERT com classificação automática)")

        casos = [
            (self.paquimetro, 50.000, 50.020, 50.030, "dentro da faixa"),
            (self.paquimetro, 50.000, 50.090, 50.100, "acima do limite superior"),
            (self.relogio,    25.000, 25.050, 25.050, "exatamente no limite superior"),
        ]

        for equipamento, nominal, m1, m2, observacao in casos:
            medicao = Medicao(
                id_equipamento=equipamento.id_equipamento,
                id_tecnico=self.metrologista.id_tecnico,
                parametro="Comprimento",
                valor_nominal=nominal,
                tol_mais=0.050,
                tol_menos=-0.050,
                medida1=m1,
                medida2=m2,
            )
            self.medicao_dao.inserir(medicao)
            self.medicoes.append(medicao)
            print(
                f"    id={medicao.id_medicao} | {equipamento.codigo} | "
                f"média={medicao.media:.3f} | erro={medicao.erro:+.3f} | "
                f"desvio={medicao.desvio_padrao:.4f} | "
                f"status={medicao.status} ({observacao})"
            )
        print()

    # -------------------------------------------------------------
    # [4] Bloqueio de regra de negócio (antes de qualquer SQL)
    # -------------------------------------------------------------
    def etapa_bloqueio_regra(self) -> None:
        print("[4] Testando bloqueio de medição incompleta (RN01)")
        try:
            Medicao(
                id_equipamento=self.paquimetro.id_equipamento,
                id_tecnico=self.metrologista.id_tecnico,
                parametro="Diâmetro",
                valor_nominal=50.0, tol_mais=0.05, tol_menos=-0.05,
                medida1=50.02, medida2=" ",
            )
        except ErroValidacao as exc:
            print(f"    Bloqueado corretamente: {exc}\n")

    # -------------------------------------------------------------
    # [5] Rejeição de chave estrangeira inexistente
    # -------------------------------------------------------------
    def etapa_fk_inexistente(self) -> None:
        print("[5] Testando rejeição de FK inexistente (PRAGMA foreign_keys = ON)")
        try:
            self.medicao_dao.inserir(
                Medicao(
                    id_equipamento=9999,   # não existe
                    id_tecnico=self.metrologista.id_tecnico,
                    parametro="Comprimento",
                    valor_nominal=50.0, tol_mais=0.05, tol_menos=-0.05,
                    medida1=50.01, medida2=50.02,
                )
            )
        except ErroPersistencia as exc:
            print(f"    Rejeitado pelo banco: {exc}\n")

    # -------------------------------------------------------------
    # [6] UPDATE com recálculo automático
    # -------------------------------------------------------------
    def etapa_update(self) -> None:
        print("[6] Atualizando as leituras da medição reprovada (UPDATE)")
        reprovada = self.medicoes[1]
        recalculada = self.medicao_dao.atualizar_medidas(
            reprovada.id_medicao, medida1=50.010, medida2=50.020
        )
        print(
            f"    id={recalculada.id_medicao} | antes: {reprovada.status} "
            f"(média {reprovada.media:.3f}) -> depois: {recalculada.status} "
            f"(média {recalculada.media:.3f})\n"
        )

    # -------------------------------------------------------------
    # [7] Relatório com JOIN triplo
    # -------------------------------------------------------------
    def etapa_relatorio(self) -> None:
        print("[7] Consulta relacional com JOIN\n")
        imprimir_relatorio(self.medicao_dao.relatorio_calibracoes())

    # -------------------------------------------------------------
    # [8] Histórico por equipamento (RF07)
    # -------------------------------------------------------------
    def etapa_historico(self) -> None:
        print("\n[8] Histórico do paquímetro 703.1208 (RF07)")
        for r in self.medicao_dao.historico_por_equipamento(
            self.paquimetro.id_equipamento
        ):
            print(
                f"    {data_br(r['data_medicao'])} | {r['parametro']:<12} | "
                f"média={r['media']:.3f} | {r['status']}"
            )

    # -------------------------------------------------------------
    # [9] DELETE e proteção por chave estrangeira
    # -------------------------------------------------------------
    def etapa_exclusao(self) -> None:
        print("\n[9] Testando exclusão (DELETE)")
        try:
            self.equipamento_dao.excluir(self.paquimetro.id_equipamento)
        except ErroPersistencia as exc:
            print(f"    Equipamento com medições não pode ser excluído: {exc}")

        removidas = self.medicao_dao.excluir(self.medicoes[2].id_medicao)
        restantes = len(self.medicao_dao.listar())
        print(
            f"    Medição id={self.medicoes[2].id_medicao} excluída "
            f"({removidas} linha). Medições restantes: {restantes}"
        )

    # -------------------------------------------------------------
    def executar(self) -> None:
        print(f"[1] Inicialização do banco: {self.inicializar_banco()}\n")
        self.etapa_cadastros()
        self.etapa_medicoes()
        self.etapa_bloqueio_regra()
        self.etapa_fk_inexistente()
        self.etapa_update()
        self.etapa_relatorio()
        self.etapa_historico()
        self.etapa_exclusao()


def main() -> None:
    try:
        DemonstracaoMVP().executar()
    except ErroPersistencia as exc:
        print(f"\n[ERRO DE PERSISTÊNCIA] {exc}")
        sys.exit(1)
    except ErroValidacao as exc:
        print(f"\n[ERRO DE VALIDAÇÃO] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
