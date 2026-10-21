# Formulação (versão do fim da Aula 3)

Priorizar, na fila mensal de visitas, as ligações com **queda de consumo**, para as 12 equipes (8 visitas por dia, limite de condomínios, regiões com dupla), medindo **taxa de acerto** contra a linha de base de 1 em 5 e **volume recuperado por visita**, a partir do sistema comercial, da telemetria e do app de campo.

**Prioridade = chance de irregularidade × volume recuperável.**

## Teste barato: a arquitetura cai da formulação?

| Trecho da formulação | Componente |
|---|---|
| chance de irregularidade | `src/model.py` |
| volume recuperável (fator por categoria no `config.yaml`) | `src/model.py` |
| restrições de campo | `config.yaml` + fila |
| dados dos três sistemas | `src/contracts/` |

## Teste caro: A/B de 6 equipes contra 6

Metade segue a regra atual (`src/regra_antiga.py`), metade a fila da PoC, no mesmo período. Valor do ponto: R$ 3 milhões por ano (`config.yaml`). Critério combinado antes de construir.
