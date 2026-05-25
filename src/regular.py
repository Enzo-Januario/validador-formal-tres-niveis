"""
regular.py - Reconhecedor de Linguagem Regular (LR)
====================================================

Linguagem: CPF no formato textual  ddd.ddd.ddd-dd
    L = { d d d . d d d . d d d - d d  |  d in {0..9} }

onde cada 'd' e' exatamente um digito decimal. Validamos APENAS o formato
textual; nao os digitos verificadores nem qualquer faixa numerica (isso
exigiria aritmetica e descaracterizaria o DFA).

Alfabeto:  Sigma = {0,1,2,3,4,5,6,7,8,9, '.', '-'}

Modelo computacional: Automato Finito Deterministico (DFA).
O DFA e' declarado EXPLICITAMENTE como dados (dicionarios e conjuntos),
e a funcao de transicao e' aplicada simbolo a simbolo sobre a entrada.
Nao ha if/else decidindo a aceitacao: quem decide e' a tabela de transicao.

Definicao operacional de "passo" (conforme o enunciado):
    Um passo do DFA = cada leitura de um simbolo da entrada COM mudanca
    de estado (aplicacao da funcao de transicao delta).
"""

# ---------------------------------------------------------------------------
# 1. DEFINICAO DO DFA COMO DADOS
# ---------------------------------------------------------------------------

DIGITOS = set("0123456789")

# Alfabeto da linguagem
ALFABETO = DIGITOS | {".", "-"}

# Estados:
#   q0  inicio
#   q1,q2,q3   tres primeiros digitos
#   q4         ponto 1
#   q5,q6,q7   proximos tres digitos
#   q8         ponto 2
#   q9,q10,q11 proximos tres digitos
#   q12        hifen
#   q13,q14    dois digitos finais   (q14 = ACEITACAO)
#   qDEAD      estado de erro (sumidouro / dead state)
ESTADOS = {
    "q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7",
    "q8", "q9", "q10", "q11", "q12", "q13", "q14", "qDEAD",
}

ESTADO_INICIAL = "q0"
ESTADOS_FINAIS = {"q14"}


def _trans_digito(origem, destino):
    """Gera as 10 transicoes (uma por digito) de 'origem' para 'destino'."""
    return {(origem, d): destino for d in DIGITOS}


# Tabela de transicao delta: (estado, simbolo) -> estado
# Construida explicitamente como um dicionario (dados, nao codigo).
DELTA = {}
DELTA.update(_trans_digito("q0", "q1"))     # 1o digito
DELTA.update(_trans_digito("q1", "q2"))     # 2o digito
DELTA.update(_trans_digito("q2", "q3"))     # 3o digito
DELTA[("q3", ".")] = "q4"                    # primeiro ponto
DELTA.update(_trans_digito("q4", "q5"))     # 4o digito
DELTA.update(_trans_digito("q5", "q6"))     # 5o digito
DELTA.update(_trans_digito("q6", "q7"))     # 6o digito
DELTA[("q7", ".")] = "q8"                    # segundo ponto
DELTA.update(_trans_digito("q8", "q9"))     # 7o digito
DELTA.update(_trans_digito("q9", "q10"))    # 8o digito
DELTA.update(_trans_digito("q10", "q11"))   # 9o digito
DELTA[("q11", "-")] = "q12"                  # hifen
DELTA.update(_trans_digito("q12", "q13"))   # 10o digito
DELTA.update(_trans_digito("q13", "q14"))   # 11o digito -> ACEITA


# ---------------------------------------------------------------------------
# 2. SIMULADOR DO DFA
# ---------------------------------------------------------------------------

def reconhece(cadeia, verbose=False):
    """
    Simula o DFA sobre 'cadeia'.

    Retorna uma tupla (aceita: bool, passos: int).

    'passos' conta cada aplicacao da funcao de transicao delta (uma por
    simbolo lido). Simbolos fora do alfabeto, ou transicoes inexistentes,
    levam ao estado sumidouro qDEAD (a leitura ainda conta como 1 passo).
    """
    estado = ESTADO_INICIAL
    passos = 0

    if verbose:
        print(f"  Estado inicial: {estado}")

    for i, simbolo in enumerate(cadeia):
        # Simbolo fora do alfabeto -> automato morre (sumidouro)
        if simbolo not in ALFABETO:
            destino = "qDEAD"
        else:
            destino = DELTA.get((estado, simbolo), "qDEAD")

        passos += 1  # aplicacao da funcao de transicao = 1 passo

        if verbose:
            print(f"  passo {passos:>2}: delta({estado}, '{simbolo}') = {destino}")

        estado = destino

        # Otimizacao: uma vez no sumidouro, nunca mais sai dele.
        # (Ainda assim continuamos contando passos das leituras restantes
        #  para refletir o consumo real da entrada.)

    aceita = estado in ESTADOS_FINAIS
    if verbose:
        print(f"  Estado final: {estado}  ->  {'ACEITA' if aceita else 'REJEITA'}")
    return aceita, passos


# ---------------------------------------------------------------------------
# 3. BONUS: comparacao com o modulo re (APENAS comparacao, nao e' o engine)
# ---------------------------------------------------------------------------

def reconhece_regex(cadeia):
    """
    Bonus do enunciado: comparacao opcional com o modulo re do Python.
    Este NAO e' o reconhecedor principal -- serve so para conferir que o
    DFA manual aceita exatamente a mesma linguagem que a expressao regular.
    """
    import re
    padrao = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
    return padrao.match(cadeia) is not None


# ---------------------------------------------------------------------------
# 4. EXECUCAO AUTONOMA:  python src/regular.py "123.456.789-00"
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print('Uso: python regular.py "<cadeia>"')
        print('Exemplo: python regular.py "123.456.789-00"')
        return
    cadeia = argv[1]
    print(f'Linguagem Regular (LR) -- CPF formato ddd.ddd.ddd-dd')
    print(f'Entrada: "{cadeia}"')
    print("-" * 50)
    aceita, passos = reconhece(cadeia, verbose=True)
    print("-" * 50)
    print(f"Resultado: {'ACEITA' if aceita else 'REJEITA'}  ({passos} passos)")
    # Conferencia de sanidade com o regex (bonus)
    if aceita != reconhece_regex(cadeia):
        print("AVISO: divergencia entre DFA manual e regex!")


if __name__ == "__main__":
    import sys
    main(sys.argv)