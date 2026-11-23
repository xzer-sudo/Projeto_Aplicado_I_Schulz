# 01_estrutura.md — Organização dos Dados (Modelo Conceitual Simplificado)

**Unidade Curricular:** Projeto Aplicado I
**Empresa Parceira:** Schulz S.A.
**Equipe:** Marx Braga Camilo, Gladson Goulart, Carla Tayna, Yorman Hernandez

---

Para resolver o problema da primeira entrega, que mostrava os dados transcritos repetidas vezes, gerando retrabalho, erros de digitação e perda de rastreabilidade das informações, propõe-se a estruturação de um Banco de Dados Relacional (SQLite) que armazenará as informações dos técnicos/solicitantes, dos equipamentos e das medições.

## 1. As três entidades principais

### 1.1 Técnico/Solicitante

Armazena os dados das pessoas e setores envolvidos no processo: os metrologistas que executam as medições e os solicitantes (clientes internos) que pedem a calibração dos dispositivos.

- Campos principais: identificador (chave primária), nome, papel (técnico ou solicitante) e setor.

### 1.2 Equipamento

Representa os dispositivos de controle que passam pela calibração.

- Campos principais: identificador (chave primária), código do calibrador, denominação, fabricante, modelo e categoria.

### 1.3 Medição

Registra cada sessão de calibração realizada, conectando um equipamento a um técnico.

- Campos principais: identificador (chave primária), data de medição, parâmetro avaliado, valor nominal, tolerâncias ("+" e "−"), medida 1, medida 2, média, desvio padrão e status.

## 2. Relacionamentos

- Cada medição é realizada por exatamente 1 técnico (1,1) e pertence a exatamente 1 equipamento (1,1).
- Cada técnico pode realizar 0 ou n medições (0,n).
- Cada equipamento pode ter 0 ou n medições (0,n).

## 3. A importância de evitar dados duplicados

No processo atual, a mesma informação (nome do técnico, setor, código e dados do equipamento) repetia-se em várias abas e arquivos. No modelo relacional, cada dado existe em um único lugar e as demais tabelas apenas referenciam seu identificador por chaves. Uma correção feita em um registro vale para todo o sistema, eliminando divergências e preservando o histórico das calibrações de forma íntegra e rastreável.

## 4. Diagrama Entidade-Relacionamento Conceitual

O diagrama conceitual (Figura 1 do PDF da entrega) representa o nível de abstração inicial do domínio, identificando as entidades, os relacionamentos ("realiza" e "pode ter") e suas cardinalidades mínimas e máximas: (1,1) do lado da medição e (0,n) do lado do técnico e do equipamento.

## 5. Conclusão

O modelo conceitual proposto traduz o processo manual da Schulz S.A. em três entidades relacionais, eliminando as transcrições repetidas identificadas no Desafio 1. Com cada dado armazenado uma única vez e referenciado por chaves, o banco garante consistência, rastreabilidade e a base necessária para a emissão automatizada dos certificados de calibração.
