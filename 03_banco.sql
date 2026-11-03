-- =====================================================================
-- 03_banco.sql — Script DDL de criação do banco de calibrações (SQLite)
-- Projeto Aplicado I — Entrega 02 | Empresa parceira: Schulz S.A.
-- Equipe: Marx Braga Camilo, Gladson Goulart, Carla Tayna, Yorman Hernandez
-- =====================================================================

-- O SQLite só verifica chaves estrangeiras com esta opção ligada
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS medicao;
DROP TABLE IF EXISTS equipamento;
DROP TABLE IF EXISTS tecnico;

-- ---------------------------------------------------------------------
-- Tabela 1: tecnico (Técnicos / Solicitantes)
-- ---------------------------------------------------------------------
CREATE TABLE tecnico (
    id_tecnico   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL,
    papel        TEXT    NOT NULL CHECK (papel IN ('TECNICO', 'SOLICITANTE')),
    nome_setor   TEXT    NOT NULL
);

-- ---------------------------------------------------------------------
-- Tabela 2: equipamento (Instrumentos e dispositivos de controle)
-- ---------------------------------------------------------------------
CREATE TABLE equipamento (
    id_equipamento  INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT    NOT NULL UNIQUE,
    denominacao     TEXT    NOT NULL,
    fabricante      TEXT    NOT NULL,
    modelo          TEXT    NOT NULL,
    categoria       TEXT
);

-- ---------------------------------------------------------------------
-- Tabela 3: medicao (Registro das calibrações / ensaios)
-- Cada medição pertence a 1 equipamento e é feita por 1 técnico (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE medicao (
    id_medicao      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipamento  INTEGER NOT NULL,
    id_tecnico      INTEGER NOT NULL,
    data_medicao    TEXT    NOT NULL DEFAULT CURRENT_DATE,
    parametro       TEXT    NOT NULL,
    valor_nominal   REAL    NOT NULL,
    tol_mais        REAL    NOT NULL,
    tol_menos       REAL    NOT NULL,
    medida1         REAL    NOT NULL,
    medida2         REAL    NOT NULL,
    media           REAL,
    desvio_padrao   REAL,
    status          TEXT    NOT NULL CHECK (status IN ('APROVADO', 'REPROVADO')),
    FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento),
    FOREIGN KEY (id_tecnico)     REFERENCES tecnico (id_tecnico)
);
