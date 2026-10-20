"""
limpeza.py  -  FUNCOES DE LIMPEZA   (voce completa os trechos marcados com ____)
============================================================================
Cada funcao resolve UM problema dos dados brutos (CNPJ com mascara, "R$ 1.234,56", datas em varios formatos...).
Leia o texto da funcao, olhe os exemplos e troque cada  ____  pelo codigo certo.
O que vem depois de "COMPLETE:" explica, em uma frase, o que fazer.

COMO SABER SE ACERTOU:   python -m src.limpeza
O arquivo testa as suas funcoes com os exemplos do casos_de_teste.docx e mostra  ✔ (acertou)  ou  ✘ (confira de novo).
Faca uma funcao por vez, na ordem em que aparecem: as ultimas usam as primeiras.
Dica de ouro: se travar, volte ao guia_de_referencias.docx: ele diz em qual trabalho antigo voce ja viu algo parecido.
"""

from datetime import datetime

# Textos que significam "sem valor" num campo de TEXTO (sempre comparados em MAIUSCULAS)
NULOS = {"N/A", "NULL", "NONE", "NAN", "-", "0", "SEM INFORMAÇÃO", "SEM INFORMACAO",
         "NÃO INFORMADO", "NAO INFORMADO", "NÃO SE APLICA", "NAO SE APLICA"}

# Formatos de data que aparecem nos arquivos (a letra %d e dia, %m e mes, %Y e ano com 4 digitos)
FORMATOS_DATA = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d", "%Y%m%d"]


# ---------------------------------------------------------------------------------------------
# 1) TEXTO  (nulos disfarcados, espacos, acento quebrado)
# ---------------------------------------------------------------------------------------------
def remover_invisiveis(texto):
    """PRONTA (so leia). Apaga caracteres invisiveis de largura zero que vem de sistemas antigos."""
    for c in ["​", "‌", "‍", "﻿"]:
        texto = texto.replace(c, "")
    return texto


def consertar_acento(texto):
    """PRONTA (so leia). 'AquisiÃ§Ã£o' -> 'Aquisição': texto UTF-8 que foi lido como Latin-1.
    Se o texto nao tem esse problema, o try falha e devolvemos o texto como estava."""
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def tirar_espacos(texto):
    """Tira espacos das pontas e espacos repetidos.   '  Ana   Maria ' -> 'Ana Maria'  (  e o espaco 'sem quebra')."""
    # DICA: texto.split() separa o texto em palavras, em QUALQUER espaco (inclusive o 'sem quebra')
    # COMPLETE: junte as palavras de volta com UM unico espaco entre elas (" ".join(...))
    return ____


def eh_nulo(texto, zero_eh_nulo=True):
    """True se o texto significa 'sem valor': vazio, N/A, NULL, -, SEM INFORMACAO...
    O "0" so e nulo em campo de TEXTO. Em campo de numero, 0 e um valor de verdade (zero_eh_nulo=False)."""
    chave = texto.upper()
    if chave == "":
        return True
    if chave == "0":
        # COMPLETE: devolva o que diz se o zero conta como nulo neste campo (o parametro da funcao)
        return ____
    # COMPLETE: o texto e nulo se a chave estiver no conjunto NULOS
    return ____


def limpar_texto(texto, zero_eh_nulo=True):
    """Limpa um texto: tira invisiveis e espacos, conserta o acento e devolve None se for 'nulo disfarcado'."""
    if texto is None:
        return None
    texto = remover_invisiveis(texto)
    texto = consertar_acento(texto.strip(" "))
    # COMPLETE: chame tirar_espacos(texto)
    texto = ____
    # COMPLETE: se o texto for nulo (use eh_nulo, passando o zero_eh_nulo), devolva None
    if ____:
        return None
    return texto


def padronizar_nome(texto):
    """Nome de orgao / fornecedor / item: limpo e em MAIUSCULAS, para 'Ministerio da Saude' e 'MINISTERIO  DA SAUDE '
    virarem o MESMO texto.   'Pregão-Eletrônico' -> 'PREGÃO - ELETRÔNICO'  (hifen com espaco dos dois lados)."""
    texto = limpar_texto(texto)
    if texto is None:
        return None
    # COMPLETE: coloque em maiusculas (metodo .upper())
    texto = texto.____
    # COMPLETE: troque cada "-" por " - " (o tirar_espacos abaixo arruma os espacos repetidos)
    texto = ____
    return tirar_espacos(texto)


# ---------------------------------------------------------------------------------------------
# 2) DOCUMENTOS  (CNPJ = 14 digitos, CPF = 11)
# ---------------------------------------------------------------------------------------------
def limpar_documento(texto, tipo_pessoa=None):
    """Deixa so os digitos do CNPJ/CPF, com os zeros da esquerda de volta.
       '11.222.333/0001-81' (PJ) -> '11222333000181'     '1222333000181' (PJ, perdeu o zero) -> '01222333000181'
       '1234567890' (PF)         -> '01234567890'        'ABC123' (PE, estrangeiro) -> 'ABC123' (nao mexa)
       Se vier lixo ('N/A', '-') ou digitos demais, devolva None.   tipo_pessoa: 'PJ', 'PF', 'PE' ou None."""
    texto = limpar_texto(texto)
    if texto is None:
        return None
    if tipo_pessoa == "PE":
        return texto.upper()
    # COMPLETE: fique so com os caracteres que sao digitos:  "".join(c for c in texto if c.isdigit())
    digitos = ____
    if digitos == "":
        return None
    if tipo_pessoa == "PJ":
        tamanho = 14
    elif tipo_pessoa == "PF":
        tamanho = 11
    else:                                    # sem o tipo: mais de 11 digitos e CNPJ, senao CPF
        tamanho = 14 if len(digitos) > 11 else 11
    if len(digitos) > tamanho:               # digitos demais: documento impossivel
        return None
    # COMPLETE: complete com zeros a esquerda ate o tamanho certo (metodo .zfill(tamanho))
    return digitos.____


# ---------------------------------------------------------------------------------------------
# 3) DINHEIRO E NUMEROS EM TEXTO
# ---------------------------------------------------------------------------------------------
def converter_numero(texto):
    """'R$ 1.234,56' -> 1234.56      '1,234.56' -> 1234.56      '0,754' -> 0.754      '(1.500,00)' -> -1500.0
    REGRA DESTA BASE: ponto OU virgula SOZINHO e sempre o DECIMAL ('1.234' -> 1.234; '746.815' -> 746.815).
    So o simbolo REPETIDO e milhar ('1.234.567' -> 1234567). Quando aparecem os dois, o ULTIMO e o decimal.
    Devolve None se nao der para converter ('N/A', vazio). O zero e um numero valido (0 -> 0.0)."""
    texto = limpar_texto(texto, zero_eh_nulo=False)     # False: aqui o 0 e valor, nao nulo
    if texto is None:
        return None
    texto = texto.replace("R$", "").replace(" ", "")
    # COMPLETE: e negativo se comecar com "(" ou com "-", ou se terminar com "-":  (1.500,00)  -12,50  1.500,00-
    negativo = ____
    texto = texto.strip("()-")
    if "." in texto and "," in texto:
        if texto.rfind(",") > texto.rfind("."):
            # formato 1.234,56 (a virgula vem por ultimo). COMPLETE: tire os pontos e troque a virgula por ponto
            texto = ____
        else:
            # formato 1,234.56 (o ponto vem por ultimo). COMPLETE: tire as virgulas
            texto = ____
    elif "," in texto:
        if texto.count(",") > 1:
            # 1,234,567 (virgula repetida = milhar). COMPLETE: tire as virgulas
            texto = ____
        else:
            # 12,5 (virgula sozinha = decimal). COMPLETE: troque a virgula por ponto
            texto = ____
    elif texto.count(".") > 1:
        # 1.234.567 (ponto repetido = milhar). COMPLETE: tire os pontos
        texto = ____
    # (ponto sozinho, como em 1234.56 ou 746.815, ja e decimal: nao precisa mexer)
    try:
        numero = float(texto)
    except ValueError:
        return None
    # COMPLETE: se for negativo, devolva o numero com sinal de menos; senao, o proprio numero
    return ____


# ---------------------------------------------------------------------------------------------
# 4) DATAS  (varios formatos no mesmo campo)
# ---------------------------------------------------------------------------------------------
def converter_data(texto):
    """'2025-03-10T08:30:00', '10/03/2025 14:20', '10.03.2025', '20250310' -> a data 2025-03-10 (sem hora).
    Devolve None para vazio, data impossivel ('31/02/2025') ou ano absurdo ('0001-01-01': so valem 2000 a 2030)."""
    texto = limpar_texto(texto)
    if texto is None:
        return None
    # COMPLETE: fique so com os 10 primeiros caracteres (o texto[:10] descarta a hora)
    texto = texto[:____]
    for formato in FORMATOS_DATA:
        try:
            # COMPLETE: strptime le o texto no formato; .date() tira a hora. Use datetime.strptime(texto, formato).date()
            data = ____
        except ValueError:
            continue                          # nao era esse formato: tente o proximo
        # COMPLETE: so vale se o ano estiver entre 2000 e 2030 (use data.year)
        if ____:
            return data
        return None
    return None


# =============================================================================================
# AUTOTESTE: python -m src.limpeza     (nao precisa mexer daqui para baixo)
# =============================================================================================
from datetime import date  # noqa: E402

CASOS = [
    # (funcao, argumentos, resultado esperado)   -> os mesmos exemplos do casos_de_teste.docx
    ("tirar_espacos", ("  Ana   Maria ",), "Ana Maria"),
    ("eh_nulo", ("N/A",), True), ("eh_nulo", ("SEM INFORMAÇÃO",), True), ("eh_nulo", ("",), True),
    ("eh_nulo", ("Ana",), False), ("eh_nulo", ("0", True), True), ("eh_nulo", ("0", False), False),
    ("limpar_texto", ("AquisiÃ§Ã£o de mÃ³veis",), "Aquisição de móveis"),
    ("limpar_texto", ("Aquisição",), "Aquisição"),
    ("limpar_texto", ("  Ministério  da   Saúde  ",), "Ministério da Saúde"),
    ("limpar_texto", ("n/a",), None), ("limpar_texto", (" ",), None), ("limpar_texto", ("0",), None),
    ("padronizar_nome", ("  Ministério  da   Saúde  ",), "MINISTÉRIO DA SAÚDE"),
    ("padronizar_nome", ("Pregão-Eletrônico",), "PREGÃO - ELETRÔNICO"),
    ("limpar_documento", ("11.222.333/0001-81", "PJ"), "11222333000181"),
    ("limpar_documento", ("11222333000181", None), "11222333000181"),
    ("limpar_documento", ("1222333000181", "PJ"), "01222333000181"),
    ("limpar_documento", ("360305000104", "PJ"), "00360305000104"),
    ("limpar_documento", ("111.444.777-35", "PF"), "11144477735"),
    ("limpar_documento", ("1234567890", "PF"), "01234567890"),
    ("limpar_documento", (" 11222333000181 ", "PJ"), "11222333000181"),
    ("limpar_documento", ("N/A", "PJ"), None), ("limpar_documento", ("-", "PJ"), None),
    ("limpar_documento", ("ABC123", "PE"), "ABC123"),
    ("limpar_documento", ("123456789012345", "PJ"), None),
    ("converter_numero", ("R$ 1.234,56",), 1234.56), ("converter_numero", ("1,234.56",), 1234.56),
    ("converter_numero", ("1234.56",), 1234.56), ("converter_numero", ("1.234",), 1.234),
    ("converter_numero", ("0,754",), 0.754), ("converter_numero", ("746.815",), 746.815),
    ("converter_numero", ("1.234.567",), 1234567.0), ("converter_numero", ("12,5",), 12.5),
    ("converter_numero", ("1.234.567,89",), 1234567.89), ("converter_numero", ("R$ -12,50",), -12.5),
    ("converter_numero", ("(1.500,00)",), -1500.0), ("converter_numero", ("1.500,00-",), -1500.0),
    ("converter_numero", ("R$ 2.000,00",), 2000.0), ("converter_numero", ("493231.6000",), 493231.6),
    ("converter_numero", ("0",), 0.0), ("converter_numero", ("N/A",), None), ("converter_numero", ("",), None),
    ("converter_data", ("2025-03-10T08:30:00",), date(2025, 3, 10)), ("converter_data", ("10/03/2025",), date(2025, 3, 10)),
    ("converter_data", ("10-03-2025",), date(2025, 3, 10)), ("converter_data", ("2025/03/10",), date(2025, 3, 10)),
    ("converter_data", ("20250310",), date(2025, 3, 10)), ("converter_data", ("10/03/2025 14:20",), date(2025, 3, 10)),
    ("converter_data", ("10.03.2025",), date(2025, 3, 10)), ("converter_data", ("31/02/2025",), None),
    ("converter_data", ("0001-01-01",), None), ("converter_data", ("-",), None), ("converter_data", ("",), None),
]


def testar():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")        # para o ✔ e o ✘ aparecerem em qualquer terminal
    except (AttributeError, ValueError):
        pass
    acertos = 0
    for nome, args, esperado in CASOS:
        try:
            obtido = globals()[nome](*args)
            ok = obtido == esperado
        except Exception as erro:                       # funcao ainda com ____ (NameError) ou com erro
            obtido, ok = f"erro: {type(erro).__name__}", False
        acertos += ok
        if not ok:
            print(f"✘ {nome}{args}  esperado {esperado!r}  obtido {obtido!r}")
    print(f"\n{acertos} de {len(CASOS)} exemplos certos" + ("  ✔ tudo certo, pode ir para a proxima etapa!" if acertos == len(CASOS) else "  -> continue completando"))
    return acertos == len(CASOS)


if __name__ == "__main__":
    raise SystemExit(0 if testar() else 1)
