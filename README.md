# Validador Formal em Três Níveis

Projeto da disciplina de **Modelagem Computacional** — construção de três
reconhecedores formais, um para cada nível da hierarquia de Chomsky:

| Nível | Linguagem | Modelo | Arquivo |
|-------|-----------|--------|---------|
| **Regular (LR)** | CPF no formato `ddd.ddd.ddd-dd` | Autômato Finito Determinístico (DFA) | `src/regular.py` |
| **Livre de Contexto (LLC)** | Parênteses, colchetes e chaves balanceados | Autômato com Pilha (PDA) | `src/livre_contexto.py` |
| **Recursiva (R)** | Cópia de cadeia `L = {w#w \| w ∈ {0,1}*}` | Máquina de Turing (MT) | `src/recursiva.py` |

A meta é comparar, em código próprio, a hierarquia **LR ⊊ LLC ⊊ R** e a
diferença de poder computacional entre os três modelos.

> Cada reconhecedor é um **simulador do autômato** correspondente: estados,
> alfabeto, transições, estado inicial e estados finais são declarados
> explicitamente **como dados** (dicionários e conjuntos), e a função de
> transição é aplicada símbolo a símbolo sobre a entrada. O módulo `re` do
> Python **não** é usado como reconhecedor (apenas como comparação opcional
> no nível LR).

---

## Requisitos

- **Python 3.8+** — apenas a biblioteca padrão. Nenhuma instalação é
  necessária para rodar o projeto obrigatório.

---

## Como rodar a bateria completa (um único comando)

A partir da raiz do projeto:

```bash
python src/testes.py
```

Isso lê os arquivos de `testes/*.txt`, roda as 18 cadeias (3 aceitas + 3
rejeitadas por linguagem) contra os três reconhecedores e imprime, para
cada uma, a tabela **esperado vs obtido** junto com o **número de passos**
executados pelo autômato.

---

## Rodando cada reconhecedor isoladamente

Cada reconhecedor também executa de forma autônoma, recebendo a cadeia
como argumento, e mostra a execução **passo a passo**:

```bash
python src/regular.py "123.456.789-00"      # Regular  -> ACEITA
python src/regular.py "12.34.56-78"          # Regular  -> REJEITA

python src/livre_contexto.py "((x+y)*z)"     # LLC      -> ACEITA
python src/livre_contexto.py "((a+b)"        # LLC      -> REJEITA

python src/recursiva.py "101#101"            # Recursiva-> ACEITA
python src/recursiva.py "101#100"            # Recursiva-> REJEITA
```

> No Windows (PowerShell), use a barra invertida no caminho:
> `python src\regular.py "123.456.789-00"`

---

## O que é um "passo"

Conforme a definição do projeto, **um passo é uma aplicação da função de
transição** do modelo:

- **DFA**: cada leitura de um símbolo da entrada com mudança de estado;
- **PDA**: cada transição, contando empilhamento e desempilhamento;
- **MT**: cada movimento da cabeça (leitura, escrita, deslocamento) sobre a fita.

O número de passos **não** é o número de iterações do laço Python. Cada
reconhecedor incrementa o contador exclusivamente nesses eventos.

---

## Estrutura do repositório

```
projeto/
├── README.md
├── requirements.txt
├── src/
│   ├── regular.py            # reconhecedor LR (DFA), executável sozinho
│   ├── livre_contexto.py     # reconhecedor LLC (PDA), executável sozinho
│   ├── recursiva.py          # reconhecedor R (MT), executável sozinho
│   └── testes.py             # roda os testes/*.txt contra os 3 reconhecedores
├── testes/
│   ├── testes_regular.txt
│   ├── testes_livre_contexto.txt
│   └── testes_recursiva.txt
├── diagramas/
│   ├── dfa_regular.(png|svg|pdf)
│   ├── pda_livre_contexto.(png|svg|pdf)
│   └── mt_recursiva.(png|svg|pdf)
└── relatorio/
    └── relatorio.pdf
```

---

## Linguagens reconhecidas (resumo formal)

**Regular (LR) — formato de CPF**
`L = { ddd.ddd.ddd-dd | d ∈ {0,...,9} }`
Validação apenas do formato textual (não dos dígitos verificadores nem de
faixas numéricas, que exigiriam aritmética e descaracterizariam o DFA).

**Livre de Contexto (LLC) — delimitadores balanceados**
Linguagem de Dyck sobre três tipos de par `( ) [ ] { }`, com símbolos
neutros (letras, dígitos, operadores) permitidos. Uma cadeia é aceita
quando toda abertura tem o fechamento correspondente, na ordem correta.

**Recursiva (R) — cópia de cadeia**
`L = { w#w | w ∈ {0,1}* }`
Não é livre de contexto; exige uma Máquina de Turing que casa os dígitos
das duas metades, símbolo a símbolo.