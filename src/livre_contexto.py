"""
livre_contexto.py - Reconhecedor de Linguagem Livre de Contexto (LLC)
=====================================================================

Linguagem: parenteses, colchetes e chaves balanceados dentro de uma
expressao simbolica. Simbolos que nao sao delimitadores (letras, digitos,
operadores como + - * /) sao IGNORADOS pelo balanceamento -- o que importa
e' que cada abertura tenha o fechamento correspondente, na ordem certa.

    Exemplos: ((x+y)*z)  aceito ;  ((a+b)  rejeitado ;  [a+(b]*c)  rejeitado

Definicao formal (linguagem de Dyck generalizada sobre 3 tipos de par,
                   com simbolos neutros permitidos):
    Seja P = { ( ) [ ] { } } o conjunto de delimitadores e
    N = qualquer outro simbolo (neutro).
    L = { w in (P U N)* | a projecao de w sobre P e' uma cadeia de
          Dyck (parenteses bem-formados de 3 tipos) }

Alfabeto:  Sigma = { ( ) [ ] { } } U { simbolos neutros }
    (neste reconhecedor aceitamos letras, digitos e operadores comuns
     como simbolos neutros)

Modelo computacional: Automato com Pilha (PDA) por ESVAZIAMENTO DE PILHA.
O PDA e' declarado explicitamente como dados. Aplicamos a funcao de
transicao simbolo a simbolo, manipulando a pilha. A cadeia e' aceita se,
ao terminar a leitura, a pilha estiver vazia (e nenhuma violacao ocorreu).

Definicao operacional de "passo" (conforme o enunciado):
    Para o PDA, cada transicao conta como passo, incluindo empilhamento
    e desempilhamento. Aqui contamos 1 passo por simbolo processado
    (cada leitura aciona a funcao de transicao), e tambem registramos
    explicitamente quantas operacoes de pilha (push/pop) ocorreram.
"""

# ---------------------------------------------------------------------------
# 1. DEFINICAO DO PDA COMO DADOS
# ---------------------------------------------------------------------------

# Pares de delimitadores: simbolo de abertura -> simbolo de fechamento
PARES = {
    "(": ")",
    "[": "]",
    "{": "}",
}

ABERTURA = set(PARES.keys())          # { ( [ { }
FECHAMENTO = set(PARES.values())      # { ) ] } }

# Conjunto de simbolos neutros aceitos (nao afetam a pilha).
# Letras, digitos e operadores comuns.
NEUTROS = set("abcdefghijklmnopqrstuvwxyz"
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              "0123456789"
              "+-*/^=., _")

ALFABETO = ABERTURA | FECHAMENTO | NEUTROS

# O PDA tem um unico estado de controle (q) -- toda a "memoria" esta na pilha.
# A funcao de transicao e' descrita pela tabela abaixo, indexada pela
# classe do simbolo lido. Declaramos como dados a acao de pilha de cada classe.
#
#   classe "abertura"  -> PUSH do fechamento esperado
#   classe "fechamento"-> POP e conferir se casa com o topo
#   classe "neutro"    -> nenhuma operacao de pilha
ACAO_PILHA = {
    "abertura": "push",
    "fechamento": "pop",
    "neutro": "nop",
}


def _classifica(simbolo):
    if simbolo in ABERTURA:
        return "abertura"
    if simbolo in FECHAMENTO:
        return "fechamento"
    if simbolo in NEUTROS:
        return "neutro"
    return "invalido"


# ---------------------------------------------------------------------------
# 2. SIMULADOR DO PDA
# ---------------------------------------------------------------------------

def reconhece(cadeia, verbose=False):
    """
    Simula o PDA sobre 'cadeia' por esvaziamento de pilha.

    Retorna (aceita: bool, passos: int).

    A pilha guarda os simbolos de FECHAMENTO esperados. Ao ler uma
    abertura, empilhamos o fechamento correspondente. Ao ler um
    fechamento, desempilhamos e conferimos se casa.
    """
    pilha = []
    passos = 0

    if verbose:
        print(f"  Pilha inicial: {pilha}")

    for simbolo in cadeia:
        classe = _classifica(simbolo)
        passos += 1  # cada leitura aciona a funcao de transicao = 1 passo

        if classe == "invalido":
            if verbose:
                print(f"  passo {passos:>2}: simbolo '{simbolo}' fora do alfabeto -> REJEITA")
            return False, passos

        acao = ACAO_PILHA[classe]

        if acao == "push":
            esperado = PARES[simbolo]
            pilha.append(esperado)
            if verbose:
                print(f"  passo {passos:>2}: le '{simbolo}'  PUSH '{esperado}'   pilha={pilha}")

        elif acao == "pop":
            if not pilha:
                # fechamento sem abertura correspondente
                if verbose:
                    print(f"  passo {passos:>2}: le '{simbolo}'  POP em pilha vazia -> REJEITA")
                return False, passos
            topo = pilha.pop()
            if topo != simbolo:
                # fechamento nao casa com a ultima abertura
                if verbose:
                    print(f"  passo {passos:>2}: le '{simbolo}'  POP '{topo}' (nao casa) -> REJEITA")
                return False, passos
            if verbose:
                print(f"  passo {passos:>2}: le '{simbolo}'  POP '{topo}' (casa)    pilha={pilha}")

        else:  # nop -- simbolo neutro
            if verbose:
                print(f"  passo {passos:>2}: le '{simbolo}'  (neutro)         pilha={pilha}")

    aceita = (len(pilha) == 0)
    if verbose:
        if aceita:
            print(f"  Fim da entrada, pilha vazia -> ACEITA")
        else:
            print(f"  Fim da entrada, pilha NAO vazia {pilha} -> REJEITA")
    return aceita, passos


# ---------------------------------------------------------------------------
# 3. EXECUCAO AUTONOMA:  python src/livre_contexto.py "((x+y)*z)"
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print('Uso: python livre_contexto.py "<cadeia>"')
        print('Exemplo: python livre_contexto.py "((x+y)*z)"')
        return
    cadeia = argv[1]
    print("Linguagem Livre de Contexto (LLC) -- delimitadores balanceados")
    print(f'Entrada: "{cadeia}"')
    print("-" * 50)
    aceita, passos = reconhece(cadeia, verbose=True)
    print("-" * 50)
    print(f"Resultado: {'ACEITA' if aceita else 'REJEITA'}  ({passos} passos)")


if __name__ == "__main__":
    import sys
    main(sys.argv)