"""
04_classes.py
Projeto Aplicado I — AV03 (MVP Parte 1) | Empresa parceira: Schulz S.A.
Equipe: Marx Braga Camilo, Gladson Goulart, Carla Tayna, Yorman Hernandez 
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from statistics import stdev
from typing import Optional

# Espelham as restrições CHECK do 03_banco.sql
PAPEIS_VALIDOS = ("TECNICO", "SOLICITANTE")
STATUS_VALIDOS = ("APROVADO", "REPROVADO")


# =====================================================================
# Exceções de domínio
# =====================================================================
class ErroValidacao(Exception):
    """Regra de negócio violada na camada de domínio."""


class ErroPersistencia(Exception):
    """Falha na comunicação com o banco SQLite."""


# =====================================================================
# 1. CLASSE TECNICO
# =====================================================================
class Tecnico:
    """
    Representa a tabela `tecnico`: metrologistas executantes e
    solicitantes (clientes internos dos 30 setores da Schulz).

    Encapsulamento: todos os atributos são privados e acessados por
    propriedades. A validação ocorre no construtor, de modo que um
    objeto nunca existe em estado inválido.
    """

    def __init__(
        self,
        nome: str,
        papel: str,
        nome_setor: str,
        id_tecnico: Optional[int] = None,
        matricula: Optional[str] = None,
    ):
        self._id_tecnico = id_tecnico
        self._nome = self._validar_texto(nome, "nome")
        self._papel = self._validar_papel(papel)
        self._nome_setor = self._validar_texto(nome_setor, "nome_setor")
        self._matricula = matricula

    # ------------------------- validações -------------------------
  
    def _validar_texto(valor, campo: str) -> str:
        if valor is None or not str(valor).strip():
            raise ErroValidacao(f"O campo '{campo}' é obrigatório.")
        return str(valor).strip()

  
    def _validar_papel(papel) -> str:
        papel = str(papel or "").strip().upper()
        if papel not in PAPEIS_VALIDOS:
            raise ErroValidacao(
                f"O papel deve ser um de {PAPEIS_VALIDOS}. Recebido: '{papel}'."
            )
        return papel

    # ------------------------- encapsulamento -------------------------
  
    def id_tecnico(self) -> Optional[int]:
        return self._id_tecnico

    @id_tecnico.setter
    def id_tecnico(self, valor):
        if self._id_tecnico is not None:
            raise ErroValidacao("id_tecnico já definido e não pode ser alterado.")
        self._id_tecnico = int(valor)

   
    def nome(self) -> str:
        return self._nome

    def nome(self, valor):
        self._nome = self._validar_texto(valor, "nome")

    def papel(self) -> str:
        return self._papel

    def nome_setor(self) -> str:
        return self._nome_setor

    def nome_setor(self, valor):
        self._nome_setor = self._validar_texto(valor, "nome_setor")

    # ---- propriedades de compatibilidade com o roteiro da AV03 ----
    
    def setor(self) -> str:
        """Alias de nome_setor (o roteiro da AV03 cita 'setor')."""
        return self._nome_setor

    def matricula(self) -> Optional[str]:
        return self._matricula

    def __repr__(self) -> str:
        return (
            f"Tecnico(id={self._id_tecnico}, nome='{self._nome}', "
            f"papel='{self._papel}', setor='{self._nome_setor}')"
        )


# =====================================================================
# 2. CLASSE EQUIPAMENTO
# =====================================================================
class Equipamento:
    """Representa a tabela `equipamento`: dispositivos de controle."""

    def __init__(
        self,
        codigo: str,
        denominacao: str,
        fabricante: str,
        modelo: str,
        categoria: Optional[str] = None,
        id_equipamento: Optional[int] = None,
    ):
        self._id_equipamento = id_equipamento
        self._codigo = self._validar_texto(codigo, "codigo")
        self._denominacao = self._validar_texto(denominacao, "denominacao")
        self._fabricante = self._validar_texto(fabricante, "fabricante")
        self._modelo = self._validar_texto(modelo, "modelo")
        # categoria é nullable no DDL: None é aceito
        self._categoria = categoria.strip() if categoria else None

    def _validar_texto(valor, campo: str) -> str:
        if valor is None or not str(valor).strip():
            raise ErroValidacao(f"O campo '{campo}' é obrigatório.")
        return str(valor).strip()

    def id_equipamento(self) -> Optional[int]:
        return self._id_equipamento

    def id_equipamento(self, valor):
        if self._id_equipamento is not None:
            raise ErroValidacao("id_equipamento já definido e não pode ser alterado.")
        self._id_equipamento = int(valor)

    def codigo(self) -> str:
        return self._codigo

    def codigo(self, valor):
        self._codigo = self._validar_texto(valor, "codigo")

    def denominacao(self) -> str:
        return self._denominacao

    def denominacao(self, valor):
        self._denominacao = self._validar_texto(valor, "denominacao")

    def fabricante(self) -> str:
        return self._fabricante

    def modelo(self) -> str:
        return self._modelo

    def categoria(self) -> Optional[str]:
        return self._categoria

    # ---- propriedades de compatibilidade com o roteiro da AV03 ----
  
    def codigo_tag(self) -> str:

        return self._codigo

    def descricao(self) -> str:
       
        return self._denominacao

    def __repr__(self) -> str:
        return (
            f"Equipamento(id={self._id_equipamento}, codigo='{self._codigo}', "
            f"denominacao='{self._denominacao}')"
        )


# =====================================================================
# 3. CLASSE MEDICAO — coração das regras metrológicas
# =====================================================================
class Medicao:
    """
    Encapsula o ensaio de calibração.
    """

    def __init__(
        self,
        id_equipamento: int,
        id_tecnico: int,
        parametro: str,
        valor_nominal: float,
        tol_mais: float,
        tol_menos: float,
        medida1: float,
        medida2: float,
        data_medicao=None,
        id_medicao: Optional[int] = None,
    ):
        self._id_medicao = id_medicao
        self._id_equipamento = int(id_equipamento)
        self._id_tecnico = int(id_tecnico)
        self._parametro = self._validar_texto(parametro, "parametro")
        self._valor_nominal = float(valor_nominal)
        # Normalização do sinal: a AV01 registra que tol_menos pode vir
        # como negativo, zero ou positivo dependendo da planilha de origem.
        self._tol_mais = abs(float(tol_mais))
        self._tol_menos = abs(float(tol_menos))
        self._medida1 = self._validar_medida(medida1, "medida1")
        self._medida2 = self._validar_medida(medida2, "medida2")
        self._data_medicao = self._validar_data(data_medicao)

        # -------- campos derivados (calculados, nunca informados) --------
        self._media = (self._medida1 + self._medida2) / 2
        # stdev = desvio padrão AMOSTRAL (divisor n-1), mesma convenção
        # das fórmulas da planilha manual descrita na AV01.
        self._desvio_padrao = stdev([self._medida1, self._medida2])
        self._status = self.classificar()

    # ------------------------- validações -------------------------
  
    def _validar_texto(valor, campo: str) -> str:
        if valor is None or not str(valor).strip():
            raise ErroValidacao(f"O campo '{campo}' é obrigatório.")
        return str(valor).strip()

    def _validar_medida(valor, campo: str) -> float:
        if valor is None or str(valor).strip() in ("", " "):
            raise ErroValidacao(
                f"Medição pendente: '{campo}' é obrigatória e não pode ser vazia."
            )
        try:
            return float(str(valor).replace(",", "."))
        except ValueError as exc:
            raise ErroValidacao(
                f"'{campo}' deve ser numérico. Recebido: {valor!r}."
            ) from exc

    def _validar_data(valor) -> str:
        if valor is None or str(valor).strip() == "":
            return date.today().isoformat()
        if isinstance(valor, (date, datetime)):
            return valor.strftime("%Y-%m-%d")
        texto = str(valor).strip()
        if texto in ("00/00/0000", "???"):
            raise ErroValidacao(f"Data inválida recebida: {texto!r}.")
        try:
            return datetime.strptime(texto, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError as exc:
            raise ErroValidacao(
                f"Data deve estar no formato ISO (AAAA-MM-DD). Recebido: {texto!r}."
            ) from exc

    # ------------------------- regra de negócio -------------------------
    def classificar(self) -> str:
        limite_inferior = self._valor_nominal - self._tol_menos
        limite_superior = self._valor_nominal + self._tol_mais
        return (
            "APROVADO"
            if limite_inferior <= self._media <= limite_superior
            else "REPROVADO"
        )

    # ------------------------- encapsulamento -------------------------

    def id_medicao(self) -> Optional[int]:
        return self._id_medicao

    def id_medicao(self, valor):
        if self._id_medicao is not None:
            raise ErroValidacao("id_medicao já definido e não pode ser alterado.")
        self._id_medicao = int(valor)

    def id_equipamento(self) -> int:
        return self._id_equipamento

    def id_tecnico(self) -> int:
        return self._id_tecnico

    def parametro(self) -> str:
        return self._parametro

    def valor_nominal(self) -> float:
        return self._valor_nominal

    def tol_mais(self) -> float:
        return self._tol_mais

    def tol_menos(self) -> float:
        return self._tol_menos

    def medida1(self) -> float:
        return self._medida1

    def medida2(self) -> float:
        return self._medida2

    def media(self) -> float:
        """Valor obtido do ensaio."""
        return self._media

    def valor_obtido(self) -> float:
        """Alias de media, conforme redação do roteiro da AV03."""
        return self._media

    def desvio_padrao(self) -> float:
        return self._desvio_padrao

    def status(self) -> str:
        return self._status

    def data_medicao(self) -> str:
        return self._data_medicao

    def data_medicao_br(self) -> str:
        return datetime.strptime(self._data_medicao, "%Y-%m-%d").strftime("%d/%m/%Y")

    def __repr__(self) -> str:
        return (
            f"Medicao(id={self._id_medicao}, parametro='{self._parametro}', "
            f"media={self._media:.3f}, status='{self._status}')"
        )


# =====================================================================
# 4. CLASSE DE CONEXÃO E PERSISTÊNCIA
# =====================================================================
class ConexaoSQLite:

    def __init__(self, caminho_db: str = "schulz_calibracao.db"):
        self.caminho_db = caminho_db

    def __enter__(self) -> sqlite3.Connection:
        try:
            self._conn = sqlite3.connect(self.caminho_db)
        except sqlite3.Error as exc:
            raise ErroPersistencia(
                f"Não foi possível abrir o banco '{self.caminho_db}': {exc}"
            ) from exc
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.row_factory = sqlite3.Row
        return self._conn

    def __exit__(self, tipo_exc, valor_exc, traceback):
        try:
            if tipo_exc is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            self._conn.close()
        return False  # não suprime a exceção


class _DAOBase:
    
    def __init__(self, caminho_db: str = "schulz_calibracao.db"):
        self.caminho_db = caminho_db

    def _conectar(self) -> ConexaoSQLite:
        return ConexaoSQLite(self.caminho_db)

    def _erro(exc: sqlite3.Error, contexto: str) -> ErroPersistencia:
        return ErroPersistencia(f"Erro SQL em {contexto}: {exc}")


# ---------------------------------------------------------------------
# DAO de Tecnico
# ---------------------------------------------------------------------
class TecnicoDAO(_DAOBase):

    def inserir(self, tecnico: Tecnico) -> Tecnico:
        sql = "INSERT INTO tecnico (nome, papel, nome_setor) VALUES (?, ?, ?);"
        try:
            with self._conectar() as conn:
                cur = conn.execute(
                    sql, (tecnico.nome, tecnico.papel, tecnico.nome_setor)
                )
                novo_id = cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise self._erro(exc, "INSERT tecnico") from exc
        tecnico.id_tecnico = novo_id
        return tecnico

    def buscar_por_id(self, id_tecnico: int) -> Optional[Tecnico]:
        sql = "SELECT * FROM tecnico WHERE id_tecnico = ?;"
        with self._conectar() as conn:
            linha = conn.execute(sql, (id_tecnico,)).fetchone()
        if linha is None:
            return None
        return Tecnico(
            nome=linha["nome"],
            papel=linha["papel"],
            nome_setor=linha["nome_setor"],
            id_tecnico=linha["id_tecnico"],
        )

    def listar(self) -> list[Tecnico]:
        sql = "SELECT * FROM tecnico ORDER BY nome;"
        with self._conectar() as conn:
            linhas = conn.execute(sql).fetchall()
        return [
            Tecnico(
                nome=l["nome"],
                papel=l["papel"],
                nome_setor=l["nome_setor"],
                id_tecnico=l["id_tecnico"],
            )
            for l in linhas
        ]

    def atualizar(self, tecnico: Tecnico) -> int:
        if tecnico.id_tecnico is None:
            raise ErroValidacao("Não é possível atualizar um técnico sem id.")
        sql = (
            "UPDATE tecnico SET nome = ?, papel = ?, nome_setor = ? "
            "WHERE id_tecnico = ?;"
        )
        try:
            with self._conectar() as conn:
                cur = conn.execute(
                    sql,
                    (tecnico.nome, tecnico.papel, tecnico.nome_setor,
                     tecnico.id_tecnico),
                )
                return cur.rowcount
        except sqlite3.IntegrityError as exc:
            raise self._erro(exc, "UPDATE tecnico") from exc


# ---------------------------------------------------------------------
# DAO de Equipamento
# ---------------------------------------------------------------------
class EquipamentoDAO(_DAOBase):

    def inserir(self, equipamento: Equipamento) -> Equipamento:
        sql = (
            "INSERT INTO equipamento (codigo, denominacao, fabricante, modelo, "
            "categoria) VALUES (?, ?, ?, ?, ?);"
        )
        try:
            with self._conectar() as conn:
                cur = conn.execute(
                    sql,
                    (equipamento.codigo, equipamento.denominacao,
                     equipamento.fabricante, equipamento.modelo,
                     equipamento.categoria),
                )
                novo_id = cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise self._erro(exc, "INSERT equipamento") from exc
        equipamento.id_equipamento = novo_id
        return equipamento

    def buscar_por_id(self, id_equipamento: int) -> Optional[Equipamento]:
        sql = "SELECT * FROM equipamento WHERE id_equipamento = ?;"
        with self._conectar() as conn:
            linha = conn.execute(sql, (id_equipamento,)).fetchone()
        if linha is None:
            return None
        return Equipamento(
            codigo=linha["codigo"],
            denominacao=linha["denominacao"],
            fabricante=linha["fabricante"],
            modelo=linha["modelo"],
            categoria=linha["categoria"],
            id_equipamento=linha["id_equipamento"],
        )

    def listar(self) -> list[Equipamento]:
        sql = "SELECT * FROM equipamento ORDER BY codigo;"
        with self._conectar() as conn:
            linhas = conn.execute(sql).fetchall()
        return [
            Equipamento(
                codigo=l["codigo"],
                denominacao=l["denominacao"],
                fabricante=l["fabricante"],
                modelo=l["modelo"],
                categoria=l["categoria"],
                id_equipamento=l["id_equipamento"],
            )
            for l in linhas
        ]

    def atualizar(self, equipamento: Equipamento) -> int:
        if equipamento.id_equipamento is None:
            raise ErroValidacao("Não é possível atualizar um equipamento sem id.")
        sql = (
            "UPDATE equipamento SET codigo = ?, denominacao = ?, fabricante = ?, "
            "modelo = ?, categoria = ? WHERE id_equipamento = ?;"
        )
        try:
            with self._conectar() as conn:
                cur = conn.execute(
                    sql,
                    (equipamento.codigo, equipamento.denominacao,
                     equipamento.fabricante, equipamento.modelo,
                     equipamento.categoria, equipamento.id_equipamento),
                )
                return cur.rowcount
        except sqlite3.IntegrityError as exc:
            raise self._erro(exc, "UPDATE equipamento") from exc


# ---------------------------------------------------------------------
# DAO de Medicao
# ---------------------------------------------------------------------
class MedicaoDAO(_DAOBase):

    def inserir(self, medicao: Medicao) -> Medicao:
        sql = (
            "INSERT INTO medicao (id_equipamento, id_tecnico, data_medicao, "
            "parametro, valor_nominal, tol_mais, tol_menos, medida1, medida2, "
            "media, desvio_padrao, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        )
        try:
            with self._conectar() as conn:
                cur = conn.execute(
                    sql,
                    (
                        medicao.id_equipamento,
                        medicao.id_tecnico,
                        medicao.data_medicao,
                        medicao.parametro,
                        medicao.valor_nominal,
                        medicao.tol_mais,
                        medicao.tol_menos,
                        medicao.medida1,
                        medicao.medida2,
                        medicao.media,
                        medicao.desvio_padrao,
                        medicao.status,
                    ),
                )
                novo_id = cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise self._erro(exc, "INSERT medicao") from exc
        medicao.id_medicao = novo_id
        return medicao

    def buscar_por_id(self, id_medicao: int) -> Optional[Medicao]:
        sql = "SELECT * FROM medicao WHERE id_medicao = ?;"
        with self._conectar() as conn:
            linha = conn.execute(sql, (id_medicao,)).fetchone()
        return self._linha_para_objeto(linha) if linha else None

    def _linha_para_objeto(linha: sqlite3.Row) -> Medicao:
        return Medicao(
            id_equipamento=linha["id_equipamento"],
            id_tecnico=linha["id_tecnico"],
            parametro=linha["parametro"],
            valor_nominal=linha["valor_nominal"],
            tol_mais=linha["tol_mais"],
            tol_menos=linha["tol_menos"],
            medida1=linha["medida1"],
            medida2=linha["medida2"],
            data_medicao=linha["data_medicao"],
            id_medicao=linha["id_medicao"],
        )

    def atualizar_medidas(self, id_medicao: int, medida1: float,
                          medida2: float) -> Medicao:
        """
        Reescreve as leituras e RECALCULA média, desvio padrão e status.
        Demonstra o UPDATE exigido pelo roteiro mantendo a regra de
        negócio dentro da classe de domínio.
        """
        original = self.buscar_por_id(id_medicao)
        if original is None:
            raise ErroValidacao(f"Medição {id_medicao} não encontrada.")

        recalculada = Medicao(
            id_equipamento=original.id_equipamento,
            id_tecnico=original.id_tecnico,
            parametro=original.parametro,
            valor_nominal=original.valor_nominal,
            tol_mais=original.tol_mais,
            tol_menos=original.tol_menos,
            medida1=medida1,
            medida2=medida2,
            data_medicao=original.data_medicao,
            id_medicao=original.id_medicao,
        )

        sql = (
            "UPDATE medicao SET medida1 = ?, medida2 = ?, media = ?, "
            "desvio_padrao = ?, status = ? WHERE id_medicao = ?;"
        )
        try:
            with self._conectar() as conn:
                conn.execute(
                    sql,
                    (
                        recalculada.medida1,
                        recalculada.medida2,
                        recalculada.media,
                        recalculada.desvio_padrao,
                        recalculada.status,
                        recalculada.id_medicao,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise self._erro(exc, "UPDATE medicao") from exc
        return recalculada

    def relatorio_calibracoes(self) -> list[sqlite3.Row]:
        """JOIN triplo exigido pelo roteiro: medicao + equipamento + tecnico."""
        sql = """
            SELECT
                m.id_medicao,
                e.codigo             AS codigo,
                e.denominacao        AS denominacao,
                t.nome               AS tecnico,
                t.nome_setor         AS setor,
                m.parametro          AS parametro,
                m.valor_nominal      AS valor_nominal,
                m.tol_mais           AS tol_mais,
                m.tol_menos          AS tol_menos,
                m.medida1            AS medida1,
                m.medida2            AS medida2,
                m.media              AS media,
                m.desvio_padrao      AS desvio_padrao,
                m.status             AS status,
                m.data_medicao       AS data_medicao
            FROM medicao AS m
            INNER JOIN equipamento AS e ON e.id_equipamento = m.id_equipamento
            INNER JOIN tecnico     AS t ON t.id_tecnico     = m.id_tecnico
            ORDER BY m.data_medicao DESC, e.codigo, m.id_medicao;
        """
        with self._conectar() as conn:
            return conn.execute(sql).fetchall()

    def historico_por_equipamento(self, id_equipamento: int) -> list[sqlite3.Row]:
        """Atende ao RF07/RF12 da AV01: histórico pesquisável por instrumento."""
        sql = """
            SELECT m.id_medicao, m.parametro, m.media, m.status, m.data_medicao,
                   t.nome AS tecnico
            FROM medicao AS m
            INNER JOIN tecnico AS t ON t.id_tecnico = m.id_tecnico
            WHERE m.id_equipamento = ?
            ORDER BY m.data_medicao DESC;
        """
        with self._conectar() as conn:
            return conn.execute(sql, (id_equipamento,)).fetchall()
