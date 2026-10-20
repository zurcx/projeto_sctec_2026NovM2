"""
Módulo de funções de limpeza e sanitização de dados.
Usado em src/montar_tabelas.py e testado via: python -m src.limpeza
"""

import datetime
import re

# Conjunto de strings que representam valores nulos/vazios
NULOS_PADRAO = {
    "N/A",
    "NA",
    "NULL",
    "-",
    "SEM INFORMACAO",
    "SEM INFORMAÇÃO",
    "NAO SE APLICA",
    "NÃO SE APLICA",
    "NONE",
    "NAN",
    "",
}


def tirar_espacos(texto):
    """
    Remove espaços normais e invisíveis (\xa0), além de múltiplos espaços internos.
    """
    if texto is None:
        return None
    # Substitui espaços especiais (\xa0, etc) por espaço comum
    s = re.sub(r"[\xa0\s]+", " ", str(texto)).strip()
    return s if s else None


def eh_nulo(valor, considerar_zero=False):
    """
    Verifica se um valor textual representa um nulo disfarçado.
    O '0' só é nulo se considerar_zero for True (em textos).
    """
    if valor is None:
        return True

    limpo = tirar_espacos(valor)
    if limpo is None:
        return True

    limpo_upper = limpo.upper()
    if limpo_upper in NULOS_PADRAO:
        return True

    if considerar_zero and limpo_upper == "0":
        return True

    return False


def limpar_texto(texto):
    """
    Remove espaços desnecessários, trata caracteres corrompidos (mojibake)
    e retorna None se for nulo disfarçado (incluindo '0').
    """
    if eh_nulo(texto, considerar_zero=True):
        return None

    s = tirar_espacos(texto)
    if not s or eh_nulo(s, considerar_zero=True):
        return None

    # Correção de caracteres corrompidos comuns (Latin-1 lido como UTF-8)
    correcoes = {
        "Ã§": "ç",
        "Ã£": "ã",
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã¢": "â",
        "Ãª": "ê",
        "Ã´": "ô",
        "Ã": "Á",
        "Ã‰": "É",
        "Ã“": "Ó",
        "Ãš": "Ú",
        "Ã‡": "Ç",
        "Ã•": "Õ",
        "Â": "",
    }
    for errado, certo in correcoes.items():
        s = s.replace(errado, certo)

    return s


def padronizar_nome(texto):
    """
    Limpa texto, ajusta hífens e deixa em caixa alta.
    """
    txt = limpar_texto(texto)
    if txt is None:
        return None
    # Padroniza espaçamento ao redor de hífens: 'Pregão-Eletrônico' -> 'PREGÃO - ELETRÔNICO'
    txt = re.sub(r"\s*-\s*", " - ", txt)
    return txt.upper()


def limpar_documento(doc, tipo_pessoa=None):
    """
    Limpa identificadores (CNPJ, CPF ou PE - estrangeiro).
    Trata perda de zeros à esquerda.
    """
    if eh_nulo(doc, considerar_zero=True):
        return None

    limpo = tirar_espacos(doc)
    if not limpo:
        return None

    # Se for pessoa estrangeira (PE), preserva caracteres alfanuméricos
    if tipo_pessoa == "PE":
        return limpo

    # Apenas dígitos para CPF e CNPJ
    apenas_digitos = re.sub(r"\D", "", limpo)
    if not apenas_digitos:
        return None

    tam = len(apenas_digitos)

    # CPF
    if tipo_pessoa == "PF":
        if tam <= 11:
            return apenas_digitos.zfill(11)
        return None

    # CNPJ
    if tipo_pessoa == "PJ":
        if tam <= 14:
            return apenas_digitos.zfill(14)
        return None

    # Quando tipo_pessoa não for fornecido (inferência automática)
    if tam <= 11:
        return apenas_digitos.zfill(11)
    elif tam <= 14:
        return apenas_digitos.zfill(14)

    return None


def converter_numero(valor):
    """
    Converte padrões monetários e decimais para float.
    Regra 12: Um ponto ou vírgula solitário é sempre o decimal (ex: 0,754 ou 746.815).
    Separador repetido é milhar. Quando aparecem os dois, o último é o decimal.
    Trata R$, espaços invisíveis, negativos entre parênteses ou no final.
    """
    if eh_nulo(valor, considerar_zero=False):
        return None

    s = tirar_espacos(valor)
    if not s:
        return None

    # Remove R$ e espaços
    s = s.replace("R$", "").strip()

    # Trata valores negativos
    is_negativo = False
    if s.startswith("(") and s.endswith(")"):
        is_negativo = True
        s = s[1:-1].strip()
    elif s.endswith("-"):
        is_negativo = True
        s = s[:-1].strip()
    elif s.startswith("-"):
        is_negativo = True
        s = s[1:].strip()

    if not s:
        return None

    tem_ponto = "." in s
    tem_virgula = "," in s

    if tem_ponto and tem_virgula:
        pos_ponto = s.rfind(".")
        pos_virgula = s.rfind(",")
        if pos_virgula > pos_ponto:
            # Padrão brasileiro: 1.234.567,89
            s = s.replace(".", "").replace(",", ".")
        else:
            # Padrão internacional: 1,234,567.89
            s = s.replace(",", "")
    elif tem_virgula:
        # Se tem mais de uma vírgula, é milhar
        if s.count(",") > 1:
            s = s.replace(",", "")
        else:
            # Vírgula única é sempre decimal
            s = s.replace(",", ".")
    elif tem_ponto:
        # Se tem mais de um ponto, é milhar (ex: 1.234.567)
        if s.count(".") > 1:
            s = s.replace(".", "")
        # Ponto único permanece como decimal (ex: 746.815 -> 746.815 ou 493231.6000)

    try:
        num = float(s)
        return -num if is_negativo else num
    except ValueError:
        return None


def converter_data(valor):
    """
    Converte múltiplas máscaras de data para objeto datetime.date.
    Retorna None para formatos ou calendários inválidos (ex: 31/02/2025 ou ano 0001).
    """
    if eh_nulo(valor, considerar_zero=True):
        return None

    s = tirar_espacos(valor)
    if not s:
        return None

    # Se vier com hora (ISO com T ou separada por espaço), corta para pegar só a data
    if "T" in s:
        s = s.split("T")[0]
    elif " " in s:
        s = s.split(" ")[0]

    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y%m%d", "%d.%m.%Y"]

    for fmt in formatos:
        try:
            dt = datetime.datetime.strptime(s, fmt).date()
            # Validação cronológica mínima (evita anos zumbis como 0001)
            if dt.year < 1900:
                return None
            return dt
        except ValueError:
            continue

    return None


if __name__ == "__main__":
    # Bloco de testes executado por: python -m src.limpeza
    testes = [
        (tirar_espacos, ("  Ana\xa0  Maria ",), "Ana Maria"),
        (eh_nulo, ("N/A",), True),
        (eh_nulo, ("SEM INFORMAÇÃO",), True),
        (eh_nulo, ("Ana",), False),
        (eh_nulo, ("0", True), True),
        (eh_nulo, ("0", False), False),
        (limpar_texto, ("AquisiÃ§Ã£o de mÃ³veis",), "Aquisição de móveis"),
        (limpar_texto, ("Aquisição",), "Aquisição"),
        (limpar_texto, ("  Ministério  da   Saúde  ",), "Ministério da Saúde"),
        (limpar_texto, ("n/a",), None),
        (limpar_texto, ("\xa0",), None),
        (limpar_texto, ("0",), None),
        (padronizar_nome, ("  Ministério  da   Saúde  ",), "MINISTÉRIO DA SAÚDE"),
        (padronizar_nome, ("Pregão-Eletrônico",), "PREGÃO - ELETRÔNICO"),
        (limpar_documento, ("11.222.333/0001-81", "PJ"), "11222333000181"),
        (limpar_documento, ("11222333000181", None), "11222333000181"),
        (limpar_documento, ("1222333000181", "PJ"), "01222333000181"),
        (limpar_documento, ("360305000104", "PJ"), "00360305000104"),
        (limpar_documento, ("111.444.777-35", "PF"), "11144477735"),
        (limpar_documento, ("1234567890", "PF"), "01234567890"),
        (limpar_documento, ("\xa011222333000181 ", "PJ"), "11222333000181"),
        (limpar_documento, ("N/A", "PJ"), None),
        (limpar_documento, ("-", "PJ"), None),
        (limpar_documento, ("ABC123", "PE"), "ABC123"),
        (limpar_documento, ("123456789012345", "PJ"), None),
        (converter_numero, ("R$ 1.234,56",), 1234.56),
        (converter_numero, ("1,234.56",), 1234.56),
        (converter_numero, ("1234.56",), 1234.56),
        (converter_numero, ("1.234",), 1.234),
        (converter_numero, ("0,754",), 0.754),
        (converter_numero, ("746.815",), 746.815),
        (converter_numero, ("1.234.567",), 1234567.0),
        (converter_numero, ("12,5",), 12.5),
        (converter_numero, ("1.234.567,89",), 1234567.89),
        (converter_numero, ("R$ -12,50",), -12.5),
        (converter_numero, ("(1.500,00)",), -1500.0),
        (converter_numero, ("1.500,00-",), -1500.0),
        (converter_numero, ("R$\xa02.000,00",), 2000.0),
        (converter_numero, ("493231.6000",), 493231.6),
        (converter_numero, ("0",), 0.0),
        (converter_numero, ("N/A",), None),
        (converter_numero, ("",), None),
        (converter_data, ("2025-03-10T08:30:00",), datetime.date(2025, 3, 10)),
        (converter_data, ("10/03/2025",), datetime.date(2025, 3, 10)),
        (converter_data, ("10-03-2025",), datetime.date(2025, 3, 10)),
        (converter_data, ("2025/03/10",), datetime.date(2025, 3, 10)),
        (converter_data, ("20250310",), datetime.date(2025, 3, 10)),
        (converter_data, ("10/03/2025 14:20",), datetime.date(2025, 3, 10)),
        (converter_data, ("10.03.2025",), datetime.date(2025, 3, 10)),
        (converter_data, ("31/02/2025",), None),
        (converter_data, ("0001-01-01",), None),
        (converter_data, ("-",), None),
        (converter_data, ("",), None),
    ]

    certos = 0
    total = len(testes)

    for fn, args, esperado in testes:
        try:
            obtido = fn(*args)
            if obtido == esperado:
                certos += 1
            else:
                print(
                    f"✘ {fn.__name__}{args}  esperado {esperado!r}  obtido {obtido!r}"
                )
        except Exception as e:
            print(
                f"✘ {fn.__name__}{args}  esperado {esperado!r}  obtido 'erro: {type(e).__name__}'"
            )

    if certos == total:
        print(f"\n✔ Todos os {total} exemplos passaram!")
    else:
        print(f"\n{certos} de {total} exemplos certos  -> continue completando")
