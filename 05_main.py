"""
05_main.py
Projeto Aplicado I — AV03 (MVP Parte 1) | Schulz S.A.
Classe principal de demonstração: instanciação dos objetos, INSERT,
UPDATE, SELECT com JOIN e exibição do relatório de calibração.

Execução: python 05_main.py
"""

import importlib.util
import os
import sqlite3
from datetime import datetime

# ---------------------------------------------------------------------
# Python não permite `import` de módulo cujo nome começa com número.
# Carregamos o 04_classes.py dinamicamente para cumprir a nomenclatura
# exigida pelo roteiro sem renomear o arquivo.
# ---------------------------------------------------------------------
_spec = importlib.util.spec_from_file_location("classes_04", "04_classes.py")
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

DB = "schulz_calibracao.db"
SQL_DDL = "03_banco.sql"


def inicializar_banco() -> str:
    """Cria o banco a partir do 03_banco.sql somente se ainda não existir."""
    if os.path.exists(DB):
        with ConexaoSQLite(DB) as conn:
            existe = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='medicao';"
            ).fetchone()
        if existe:
            return "banco existente reaproveitado"

    if not os.path.exists(SQL_DDL):
        raise ErroPersistencia(f"Script DDL não encontrado: {SQL_DDL}")

    with open(SQL_DDL, encoding="utf-8") as arquivo:
        script = arquivo.read()

    with ConexaoSQLite(DB) as conn:
        conn.executescript(script)

    return "banco criado a partir do 03_banco.sql"


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
        data_br = datetime.strptime(r["data_medicao"], "%Y-%m-%d").strftime("%d/%m/%Y")
        print(
            f"{r['id_medicao']:>4} {r['codigo']:<11} {r['denominacao'][:20]:<20} "
            f"{r['tecnico'][:16]:<16} {r['setor'][:13]:<13} "
            f"{r['valor_nominal']:>8.3f} {r['tol_mais']:>7.3f} "
            f"{r['medida1']:>8.3f} {r['medida2']:>8.3f} "
            f"{r['media']:>8.3f} {r['desvio_padrao']:>7.4f} "
            f"{r['status']:<10} {data_br:<10}"
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


def main() -> None:
    print(f"[1] Inicialização do banco: {inicializar_banco()}\n")

    tecnico_dao = TecnicoDAO(DB)
    equipamento_dao = EquipamentoDAO(DB)
    medicao_dao = MedicaoDAO(DB)

    # -------------------------------------------------------------
    # [2] Instanciação dos objetos de domínio
    # -------------------------------------------------------------
    print("[2] Instanciando objetos de domínio")

    metrologista = Tecnico(
        nome="José A. Rosa Jr.", papel="TECNICO", nome_setor="Metrologia",
        matricula="MT-0042",
    )
    solicitante = Tecnico(
        nome="Cleocir de Souza", papel="SOLICITANTE", nome_setor="Usinagem I",
    )
    tecnico_dao.inserir(metrologista)
    tecnico_dao.inserir(solicitante)
    print(f"    {metrologista}")
    print(f"    {solicitante}")

    paquimetro = Equipamento(
        codigo="703.1208", denominacao="Paquímetro digital",
        fabricante="Mitutoyo", modelo="500-196-30", categoria="Dimensional",
    )
    relogio = Equipamento(
        codigo="703.2210", denominacao="Relógio comparador",
        fabricante="Starrett", modelo="25-131J", categoria="Dimensional",
    )
    equipamento_dao.inserir(paquimetro)
    equipamento_dao.inserir(relogio)
    print(f"    {paquimetro}")
    print(f"    {relogio}\n")

    # -------------------------------------------------------------
    # [3] Medições: aprovada, reprovada e no limite exato
    # -------------------------------------------------------------
    print("[3] Registrando medições (INSERT com classificação automática)")

    casos = [
        (paquimetro, 50.000, 50.020, 50.030, "dentro da faixa"),
        (paquimetro, 50.000, 50.090, 50.100, "acima do limite superior"),
        (relogio,    25.000, 25.050, 25.050, "exatamente no limite superior"),
    ]

    inseridas = []
    for equipamento, nominal, m1, m2, observacao in casos:
        medicao = Medicao(
            id_equipamento=equipamento.id_equipamento,
            id_tecnico=metrologista.id_tecnico,
            parametro="Comprimento",
            valor_nominal=nominal,
            tol_mais=0.050,
            tol_menos=-0.050,
            medida1=m1,
            medida2=m2,
        )
        medicao_dao.inserir(medicao)
        inseridas.append(medicao)
        print(
            f"    id={medicao.id_medicao} | {equipamento.codigo} | "
            f"média={medicao.media:.3f} | desvio={medicao.desvio_padrao:.4f} | "
            f"status={medicao.status} ({observacao})"
        )
    print()

    # -------------------------------------------------------------
    # [4] Bloqueio de regra de negócio (antes de qualquer SQL)
    # -------------------------------------------------------------
    print("[4] Testando bloqueio de medição incompleta (RN01)")
    try:
        Medicao(
            id_equipamento=paquimetro.id_equipamento,
            id_tecnico=metrologista.id_tecnico,
            parametro="Diâmetro",
            valor_nominal=50.0, tol_mais=0.05, tol_menos=-0.05,
            medida1=50.02, medida2=" ",
        )
    except ErroValidacao as exc:
        print(f"    Bloqueado corretamente: {exc}\n")

    # -------------------------------------------------------------
    # [5] Rejeição de chave estrangeira inexistente
    # -------------------------------------------------------------
    print("[5] Testando rejeição de FK inexistente (PRAGMA foreign_keys = ON)")
    try:
        medicao_dao.inserir(
            Medicao(
                id_equipamento=9999,   # não existe
                id_tecnico=metrologista.id_tecnico,
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
    print("[6] Atualizando as leituras da medição reprovada (UPDATE)")
    reprovada = inseridas[1]
    recalculada = medicao_dao.atualizar_medidas(
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
    print("[7] Consulta relacional com JOIN\n")
    imprimir_relatorio(medicao_dao.relatorio_calibracoes())

    # -------------------------------------------------------------
    # [8] Histórico por equipamento (RF07)
    # -------------------------------------------------------------
    print("\n[8] Histórico do paquímetro 703.1208 (RF07)")
    for r in medicao_dao.historico_por_equipamento(paquimetro.id_equipamento):
        data_br = datetime.strptime(r["data_medicao"], "%Y-%m-%d").strftime("%d/%m/%Y")
        print(
            f"    {data_br} | {r['parametro']:<12} | "
            f"média={r['media']:.3f} | {r['status']}"
        )


if __name__ == "__main__":
    main()