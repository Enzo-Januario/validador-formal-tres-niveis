"""
testes.py - Executor da bateria de testes
==========================================

Le os arquivos testes/*.txt e roda cada cadeia contra o reconhecedor
correspondente (regular, livre_contexto, recursiva). Para cada linguagem
imprime uma tabela:

    esperado | obtido | passos | OK? | cadeia

E ao final um resumo geral (quantos testes passaram).

Formato dos arquivos de teste (uma cadeia por linha):
    <esperado><TAB><cadeia>
onde <esperado> e' "aceita" ou "rejeita".
Linhas vazias ou iniciadas por '#' sao ignoradas (comentarios).
A cadeia pode ser vazia (linha "aceita<TAB>" sem nada depois do tab).

Uso:
    python src/testes.py
"""

import os
import sys

# Permite importar os reconhecedores estando em src/ (execucao a partir
# da raiz do projeto OU de dentro de src/).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import regular
import livre_contexto
import recursiva


# Mapeia cada linguagem ao seu modulo reconhecedor e ao arquivo de testes.
# (rotulo, modulo, caminho_relativo_do_arquivo_de_testes)
LINGUAGENS = [
    ("Regular (LR) - CPF",            regular,         "testes_regular.txt"),
    ("Livre de Contexto (LLC)",       livre_contexto,  "testes_livre_contexto.txt"),
    ("Recursiva (R) - w#w",           recursiva,       "testes_recursiva.txt"),
]


def _pasta_testes():
    """
    Localiza a pasta 'testes/'. O arquivo testes.py vive em src/, entao
    a pasta de testes esta um nivel acima: ../testes
    """
    aqui = os.path.dirname(os.path.abspath(__file__))   # .../projeto/src
    raiz = os.path.dirname(aqui)                          # .../projeto
    return os.path.join(raiz, "testes")


def carrega_casos(caminho):
    """
    Le um arquivo de testes e devolve uma lista de (esperado, cadeia),
    onde 'esperado' e' True (aceita) ou False (rejeita).
    """
    casos = []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            # Remove apenas a quebra de linha do final (NAO faz strip geral,
            # para nao perder espacos que possam fazer parte da cadeia).
            linha = linha.rstrip("\n").rstrip("\r")
            if not linha or linha.lstrip().startswith("#"):
                continue  # linha vazia ou comentario
            if "\t" not in linha:
                continue  # linha mal formatada, ignora
            rotulo, cadeia = linha.split("\t", 1)
            rotulo = rotulo.strip().lower()
            esperado = (rotulo == "aceita")
            casos.append((esperado, cadeia))
    return casos


def roda_linguagem(rotulo, modulo, arquivo):
    """Roda todos os casos de uma linguagem e imprime a tabela de resultados."""
    caminho = os.path.join(_pasta_testes(), arquivo)
    casos = carrega_casos(caminho)

    print("=" * 70)
    print(f"  {rotulo}")
    print("=" * 70)
    # Cabecalho da tabela
    print(f"{'esperado':<9} {'obtido':<9} {'passos':>7}  {'OK?':<4} cadeia")
    print("-" * 70)

    passaram = 0
    for esperado, cadeia in casos:
        obtido, passos = modulo.reconhece(cadeia)  # roda o reconhecedor
        ok = (obtido == esperado)
        if ok:
            passaram += 1

        esperado_txt = "aceita" if esperado else "rejeita"
        obtido_txt   = "aceita" if obtido else "rejeita"
        ok_txt       = "OK" if ok else "FALHOU"
        # Mostra a cadeia entre aspas; cadeia vazia aparece como ""
        cadeia_txt   = f'"{cadeia}"'

        print(f"{esperado_txt:<9} {obtido_txt:<9} {passos:>7}  {ok_txt:<4} {cadeia_txt}")

    print("-" * 70)
    print(f"  {passaram}/{len(casos)} testes corretos nesta linguagem")
    print()
    return passaram, len(casos)


def main():
    print()
    print("#" * 70)
    print("#  BATERIA DE TESTES - VALIDADOR FORMAL EM TRES NIVEIS")
    print("#" * 70)
    print()

    total_ok = 0
    total = 0
    for rotulo, modulo, arquivo in LINGUAGENS:
        ok, n = roda_linguagem(rotulo, modulo, arquivo)
        total_ok += ok
        total += n

    print("#" * 70)
    print(f"#  RESUMO GERAL: {total_ok}/{total} testes corretos")
    print("#" * 70)

    # Codigo de saida 0 se tudo passou, 1 caso contrario (util em CI).
    return 0 if total_ok == total else 1


if __name__ == "__main__":
    sys.exit(main())