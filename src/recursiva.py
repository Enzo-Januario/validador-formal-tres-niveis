"""
recursiva.py - Reconhecedor de Linguagem Recursiva (R)
======================================================

Linguagem: copia de cadeia
    L = { w # w  |  w in {0,1}* }

Exemplos: 101#101 aceito ; 101#100 rejeitado ; #  aceito (w vazio)

Esta linguagem NAO e' livre de contexto (prova classica pelo Lema do
Bombeamento para LLC), exigindo uma Maquina de Turing, que pode mover
a cabeca em ambas as direcoes e reescrever a fita.

Alfabeto de entrada:  Sigma = {0, 1, #}
Alfabeto de fita:     Gamma = {0, 1, #, X, Y, _}
    X marca digitos ja casados do lado ESQUERDO
    Y marca digitos ja casados do lado DIREITO
    _ (underscore) e' o simbolo BRANCO (blank)

Estrategia da MT (casamento simbolo a simbolo):
    1. Le o primeiro digito nao marcado a esquerda do '#', marca com X,
       lembra qual era (estado), atravessa o '#' e procura o primeiro
       digito nao marcado a direita.
    2. Confere se casa; se casar, marca com Y e volta ao inicio.
    3. Repete ate nao haver mais digitos a esquerda do '#'.
    4. Verifica que tambem nao sobrou digito a direita. Se tudo casou,
       ACEITA; caso contrario REJEITA.

Modelo computacional: Maquina de Turing deterministica de fita unica.
A funcao de transicao DELTA e' declarada EXPLICITAMENTE como dados:
    (estado, simbolo_lido) -> (novo_estado, simbolo_escrito, direcao)
O simulador aplica delta movimento a movimento sobre a fita.

Definicao operacional de "passo" (conforme o enunciado):
    Para a MT, cada movimento da cabeca (leitura + escrita + deslocamento),
    ou seja, cada aplicacao de delta, conta como 1 passo.
"""

# ---------------------------------------------------------------------------
# 1. DEFINICAO DA MAQUINA DE TURING COMO DADOS
# ---------------------------------------------------------------------------

BRANCO = "_"  # simbolo branco da fita

ALFABETO_ENTRADA = {"0", "1", "#"}
ALFABETO_FITA = {"0", "1", "#", "X", "Y", BRANCO}

ESTADO_INICIAL = "q0"
ESTADO_ACEITA = "qACEITA"
ESTADO_REJEITA = "qREJEITA"

# Estados de controle:
#   q0         varre da esquerda procurando proximo digito nao marcado (X/Y)
#   q1_0       leu um '0' a esquerda; vai ate o '#' e depois ao 1o digito direito
#   q1_1       leu um '1' a esquerda; idem
#   q2_0       passou do '#'; procura 1o digito direito nao marcado, espera '0'
#   q2_1       idem, espera '1'
#   q3         casou um par; volta (esquerda) ate antes do inicio para reiniciar
#   q4         todos da esquerda marcados; confere que nao sobrou digito a direita
#
# DELTA: (estado, lido) -> (novo_estado, escrito, direcao)  direcao in {L, R, S}
DELTA = {
    # --- q0: achar proximo digito nao marcado a esquerda do '#' -----------
    ("q0", "X"): ("q0", "X", "R"),       # pula marcas ja feitas
    ("q0", "Y"): ("q0", "Y", "R"),
    ("q0", "0"): ("q1_0", "X", "R"),     # marca '0' como X e lembra que era 0
    ("q0", "1"): ("q1_1", "X", "R"),     # marca '1' como X e lembra que era 1
    ("q0", "#"): ("q4", "#", "R"),       # nao ha mais digito a esquerda -> verifica direita

    # --- q1_0 / q1_1: andar para a direita ate cruzar o '#' ---------------
    ("q1_0", "0"): ("q1_0", "0", "R"),
    ("q1_0", "1"): ("q1_0", "1", "R"),
    ("q1_0", "#"): ("q2_0", "#", "R"),   # cruzou o separador; agora procura digito direito
    ("q1_1", "0"): ("q1_1", "0", "R"),
    ("q1_1", "1"): ("q1_1", "1", "R"),
    ("q1_1", "#"): ("q2_1", "#", "R"),

    # --- q2_0: procurar 1o digito direito nao marcado; deve ser '0' -------
    ("q2_0", "Y"): ("q2_0", "Y", "R"),   # pula marcas Y ja feitas
    ("q2_0", "0"): ("q3", "Y", "L"),     # casa! marca Y e comeca a voltar
    ("q2_0", "1"): (ESTADO_REJEITA, "1", "S"),  # esperava 0, achou 1 -> rejeita
    ("q2_0", BRANCO): (ESTADO_REJEITA, BRANCO, "S"),  # lado direito curto demais

    # --- q2_1: procurar 1o digito direito nao marcado; deve ser '1' -------
    ("q2_1", "Y"): ("q2_1", "Y", "R"),
    ("q2_1", "1"): ("q3", "Y", "L"),
    ("q2_1", "0"): (ESTADO_REJEITA, "0", "S"),
    ("q2_1", BRANCO): (ESTADO_REJEITA, BRANCO, "S"),

    # --- q3: voltar para a esquerda ate o branco inicial, depois reiniciar -
    ("q3", "0"): ("q3", "0", "L"),
    ("q3", "1"): ("q3", "1", "L"),
    ("q3", "X"): ("q3", "X", "L"),
    ("q3", "Y"): ("q3", "Y", "L"),
    ("q3", "#"): ("q3", "#", "L"),
    ("q3", BRANCO): ("q0", BRANCO, "R"),  # chegou antes do inicio -> volta a q0

    # --- q4: lado esquerdo todo marcado; conferir que nao sobrou digito ---
    ("q4", "Y"): ("q4", "Y", "R"),       # pula marcas Y
    ("q4", BRANCO): (ESTADO_ACEITA, BRANCO, "S"),  # nada sobrou -> ACEITA
    ("q4", "0"): (ESTADO_REJEITA, "0", "S"),       # sobrou digito a direita
    ("q4", "1"): (ESTADO_REJEITA, "1", "S"),
}


# ---------------------------------------------------------------------------
# 2. SIMULADOR DA MAQUINA DE TURING
# ---------------------------------------------------------------------------

class Fita:
    """Fita infinita (sob demanda) com cabeca de leitura/escrita."""
    def __init__(self, cadeia):
        # dicionario posicao -> simbolo; posicoes ausentes sao BRANCO
        self.celulas = {i: c for i, c in enumerate(cadeia)}
        self.cabeca = 0

    def ler(self):
        return self.celulas.get(self.cabeca, BRANCO)

    def escrever(self, simbolo):
        if simbolo == BRANCO:
            self.celulas.pop(self.cabeca, None)
        else:
            self.celulas[self.cabeca] = simbolo

    def mover(self, direcao):
        if direcao == "R":
            self.cabeca += 1
        elif direcao == "L":
            self.cabeca -= 1
        # "S" = stay, nao move

    def snapshot(self):
        """Representacao textual da fita com a posicao da cabeca em [colchetes]."""
        if not self.celulas:
            indices = [0]
        else:
            indices = range(min(self.celulas) - 0, max(self.celulas) + 1)
            indices = range(min(min(self.celulas), self.cabeca),
                            max(max(self.celulas), self.cabeca) + 1)
        partes = []
        for i in indices:
            s = self.celulas.get(i, BRANCO)
            partes.append(f"[{s}]" if i == self.cabeca else s)
        return "".join(partes)


def reconhece(cadeia, verbose=False, limite_passos=100000):
    """
    Simula a MT sobre 'cadeia'. Retorna (aceita: bool, passos: int).

    'limite_passos' e' uma salvaguarda contra loops; para esta MT ele
    nunca e' atingido porque a maquina sempre para (a linguagem e'
    recursiva / decidivel).
    """
    # Simbolo fora do alfabeto de entrada -> rejeita imediatamente.
    for c in cadeia:
        if c not in ALFABETO_ENTRADA:
            if verbose:
                print(f"  simbolo '{c}' fora do alfabeto de entrada -> REJEITA")
            return False, 0

    fita = Fita(cadeia)
    estado = ESTADO_INICIAL
    passos = 0

    if verbose:
        print(f"  inicio  estado={estado:<9} fita={fita.snapshot()}")

    while estado not in (ESTADO_ACEITA, ESTADO_REJEITA):
        lido = fita.ler()
        chave = (estado, lido)
        if chave not in DELTA:
            # transicao indefinida = rejeicao implicita
            if verbose:
                print(f"  passo {passos+1:>3}: delta({estado},'{lido}') indefinida -> REJEITA")
            return False, passos

        novo_estado, escrito, direcao = DELTA[chave]
        fita.escrever(escrito)
        fita.mover(direcao)
        passos += 1
        estado = novo_estado

        if verbose:
            print(f"  passo {passos:>3}: ({chave[0]},'{chave[1]}')->"
                  f"({novo_estado},'{escrito}',{direcao})  fita={fita.snapshot()}")

        if passos >= limite_passos:
            if verbose:
                print("  LIMITE de passos atingido (possivel loop) -> REJEITA")
            return False, passos

    aceita = (estado == ESTADO_ACEITA)
    if verbose:
        print(f"  parada  estado={estado}  ->  {'ACEITA' if aceita else 'REJEITA'}")
    return aceita, passos


# ---------------------------------------------------------------------------
# 3. EXECUCAO AUTONOMA:  python src/recursiva.py "101#101"
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print('Uso: python recursiva.py "<cadeia>"')
        print('Exemplo: python recursiva.py "101#101"')
        return
    cadeia = argv[1]
    print("Linguagem Recursiva (R) -- copia de cadeia  L = {w#w | w in {0,1}*}")
    print(f'Entrada: "{cadeia}"')
    print("-" * 50)
    aceita, passos = reconhece(cadeia, verbose=True)
    print("-" * 50)
    print(f"Resultado: {'ACEITA' if aceita else 'REJEITA'}  ({passos} passos)")


if __name__ == "__main__":
    import sys
    main(sys.argv)