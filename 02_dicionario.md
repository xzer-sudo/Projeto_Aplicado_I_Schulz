# 02_dicionario.md — Dicionário de Dados do Sistema

**Unidade Curricular:** Projeto Aplicado I
**Empresa Parceira:** Schulz S.A.
**Tema 02:** Modelagem e Implementação de Banco de Dados (SQLite)
**Professores:** Prof. MSc. Hugo Menezes Barra | Prof. Rodrigo Losina
**Equipe:** Marx Braga Camilo, Gladson Goulart, Carla Tayna, Yorman Hernandez

---

## 1. Mapeamento das Tabelas e Campos

### 1.1. Tabela: `tecnico` (Técnicos / Solicitantes)

| Nome do Campo | Tipo (SQLite) | Tipo Lógico | Restrições / Chaves | Descrição / Regra de Negócio |
| :--- | :--- | :--- | :--- | :--- |
| `id_tecnico` | INTEGER | Inteiro | PRIMARY KEY AUTOINCREMENT | Identificador único do técnico/solicitante. |
| `nome` | TEXT | Texto | NOT NULL | Nome completo do profissional. |
| `papel` | TEXT | Texto | NOT NULL, CHECK (TECNICO / SOLICITANTE) | Função da pessoa no processo de calibração. |
| `nome_setor` | TEXT | Texto | NOT NULL | Departamento de atuação (Ex: Metrologia). |

### 1.2. Tabela: `equipamento` (Instrumentos e Dispositivos)

| Nome do Campo | Tipo (SQLite) | Tipo Lógico | Restrições / Chaves | Descrição / Regra de Negócio |
| :--- | :--- | :--- | :--- | :--- |
| `id_equipamento` | INTEGER | Inteiro | PRIMARY KEY AUTOINCREMENT | Identificador único do equipamento. |
| `codigo` | TEXT | Texto | NOT NULL, UNIQUE | Código gravado no instrumento (código do calibrador). |
| `denominacao` | TEXT | Texto | NOT NULL | Descrição do equipamento (Ex: Paquímetro). |
| `fabricante` | TEXT | Texto | NOT NULL | Fabricante (Ex: Mitutoyo, Starrett). |
| `modelo` | TEXT | Texto | NOT NULL | Modelo do instrumento. |
| `categoria` | TEXT | Texto | — | Categoria do dispositivo de controle. |

### 1.3. Tabela: `medicao` (Registro das Calibrações / Ensaios)

| Nome do Campo | Tipo (SQLite) | Tipo Lógico | Restrições / Chaves | Descrição / Regra de Negócio |
| :--- | :--- | :--- | :--- | :--- |
| `id_medicao` | INTEGER | Inteiro | PRIMARY KEY AUTOINCREMENT | Identificador único do ensaio. |
| `id_equipamento` | INTEGER | Inteiro | FOREIGN KEY → equipamento, NOT NULL | Vínculo com o equipamento avaliado. |
| `id_tecnico` | INTEGER | Inteiro | FOREIGN KEY → tecnico, NOT NULL | Vínculo com o técnico responsável. |
| `data_medicao` | TEXT | Texto | NOT NULL, DEFAULT CURRENT_DATE | Data da calibração (AAAA-MM-DD). |
| `parametro` | TEXT | Texto | NOT NULL | Variável aferida (Ex: Comprimento, Diâmetro). |
| `valor_nominal` | REAL | Real | NOT NULL | Valor de referência esperado. |
| `tol_mais` | REAL | Real | NOT NULL | Tolerância superior (+). |
| `tol_menos` | REAL | Real | NOT NULL | Tolerância inferior (−). |
| `medida1` | REAL | Real | NOT NULL | Primeira leitura coletada no ensaio. |
| `medida2` | REAL | Real | NOT NULL | Segunda leitura coletada no ensaio. |
| `media` | REAL | Real | — | Média entre `medida1` e `medida2` (valor obtido). |
| `desvio_padrao` | REAL | Real | — | Desvio padrão das leituras. |
| `status` | TEXT | Texto | NOT NULL, CHECK (APROVADO / REPROVADO) | APROVADO se a média estiver dentro das tolerâncias. |

**Total:** 23 campos mapeados em 3 tabelas.

## 2. Observações

- O SQLite trabalha com as classes de armazenamento `INTEGER`, `REAL` e `TEXT`, que correspondem aos tipos lógicos Inteiro, Real e Texto pedidos no roteiro.
- Datas são gravadas como `TEXT` no padrão ISO (AAAA-MM-DD), que permite ordenação e comparação direta.
- As chaves estrangeiras de `medicao` garantem que não exista medição sem equipamento ou sem técnico cadastrado (o script ativa `PRAGMA foreign_keys = ON`).
- O campo `status` é calculado pela regra: `valor_nominal − tol_menos ≤ media ≤ valor_nominal + tol_mais` → APROVADO; caso contrário, REPROVADO.
