import re


PUNCTUATION = r"\s*[\.,\?!]\s*"


class Replacer():
    
    REPLACEMENTS = {
        "• ": [
            r"\s*bullet\s*point\s*[\.,]?\s*",
            r"\s*aufzählungs\s*punkt\s*[\.,]?\s*",
            r"\s*gliederungs\s*punkt\s*[\.,]?\s*",
        ],
        " ": [
            r"\s*leer\s*zeichen\s*[\.,]?\s*",
            r"\s*space\s*character\s*[\.,]?\s*",
        ],
        "! ": [
            rf"{PUNCTUATION}ausrufezeichen\s*[\.,]?\s*",
            rf"{PUNCTUATION}ausrufzeichen\s*[\.,]?\s*",
            rf"{PUNCTUATION}rufzeichen\s*[\.,]?\s*",
            rf"{PUNCTUATION}exclamation\s*mark\s*[\.,]?\s*",
        ],
        "? ": [
            rf"{PUNCTUATION}fragezeichen\s*[\.,]?\s*",
            rf"{PUNCTUATION}question\s*mark\s*[\.,]?\s*",
        ],
        "…": [
            rf"{PUNCTUATION}punkt\s*punkt\s*punkt\s*[\.,]?\s*",
            rf"{PUNCTUATION}dot\s*dot\s*dot\s*[\.,]?\s*",
            rf"{PUNCTUATION}ellipsis\s*[\.,]?\s*",
        ],
        ". ": [
            rf"{PUNCTUATION}period\s*[\.,]?\s*",
            rf"{PUNCTUATION}punkt\s*[\.,]?\s*",
            rf"{PUNCTUATION}full\s*stop\s*[\.,]?\s*",
        ],
        ", ": [
            rf"{PUNCTUATION}komma\s*[\.,]?\s*",
            rf"{PUNCTUATION}comma\s*[\.,]?\s*",
        ],
        " - ": [
            r"\s*bindestrich\s*[\.,]?\s*",
            r"\s*hyphen\s*[\.,]?\s*",
        ],
        "\n": [
            r"\s*new\s*line\s*[\.,]?\s*",
            r"\s*neue\s*zeile\s*[\.,]?\s*",
        ],
        "\t": [r"\s*tab\s*[\.,]?\s*",],
        "→": [
            r"\s*right\s*arrow\s*[\.,]?\s*",
            r"\s*pfeil\s*nach\s*rechts\s*[\.,]?\s*",
        ],
        "←": [
            r"\s*left\s*arrow\s*[\.,]?\s*",
            r"\s*pfeil\s*nach\s*links\s*[\.,]?\s*",
        ],
        "↑": [
            r"\s*up\s*arrow\s*[\.,]?\s*",
            r"\s*pfeil\s*nach\s*oben\s*[\.,]?\s*",
        ],
        "↓": [
            r"\s*down\s*arrow\s*[\.,]?\s*",
            r"\s*pfeil\s*nach\s*unten\s*[\.,]?\s*",
        ],
        "↔": [
            r"\s*double\s*arrow\s*[\.,]?\s*",
            r"\s*left\s*right\s*arrow\s*[\.,]?\s*",
            r"\s*pfeil\s*nach\s*links\s*rechts\s*[\.,]?\s*",
        ],
        "↕": [
            r"\s*up\s*down\s*arrow\s*[\.,]?\s*",
            r"\s*pfeil\s*nach\s*oben\s*unten\s*[\.,]?\s*",
        ],
        "|": [
            r"\s*pipe\s*[\.,]?\s*",
            r"\s*senkrechter\s*strich\s*[\.,]?\s*",
        ],
        "§": [
            r"\s*paragraph\s*[\.,]?\s*",
            r"\s*paragraph\s*symbol\s*[\.,]?\s*",
            r"\s*paragraphen\s*symbol\s*[\.,]?\s*",
        ],
        "#": [
            r"\s*hash\s*[\.,]?\s*",
            r"\s*raute\s*[\.,]?\s*",
        ],
        "°": [
            r"\s*degree\s*[\.,]?\s*",
            r"\s*grad\s*[\.,]?\s*",
        ],
        "€": [r"\s*euro\s*[\.,]?\s*",],
        "$": [r"\s*dollar\s*[\.,]?\s*",],
        "£": [r"\s*pound\s*[\.,]?\s*",],
        "¥": [r"\s*yen\s*[\.,]?\s*",],
        "%": [
            r"\s*percent\s*[\.,]?\s*",
            r"\s*prozent\s*[\.,]?\s*",
        ],
        "‰": [
            r"\s*per\s*mille\s*[\.,]?\s*",
            r"\s*promille\s*[\.,]?\s*",
        ],
        "&": [
            r"\s*ampersand\s*[\.,]?\s*",
            r"\s*und\s*zeichen\s*[\.,]?\s*",
        ],
        "\n\n": [
            r"\s*neuer\s*absatz\s*[\.,]?\s*",
            r"\s*absatz\s*[\.,]?\s*",
            r"\s*new\s*paragraph\s*[\.,]?\s*",
        ],
        "(": [
            r"\s*linke\s*klammer\s*[\.,]?\s*",
            r"\s*klammer\s*auf\s*[\.,]?\s*",
            r"\s*left\s*parenthesis\s*[\.,]?\s*",
        ],
        ")": [
            r"\s*rechte\s*klammer\s*[\.,]?\s*",
            r"\s*klammer\s*zu\s*[\.,]?\s*",
            r"\s*right\s*parenthesis\s*[\.,]?\s*",
        ],
        "[": [
            r"\s*linke\s*eckige\s*klammer\s*[\.,]?\s*",
            r"\s*eckige\s*klammer\s*auf\s*[\.,]?\s*",
            r"\s*left\s*bracket\s*[\.,]?\s*",
        ],
        "]": [
            r"\s*rechte\s*eckige\s*klammer\s*[\.,]?\s*",
            r"\s*eckige\s*klammer\s*zu\s*[\.,]?\s*",
            r"\s*right\s*bracket\s*[\.,]?\s*",
        ],
        "{": [
            r"\s*linke\s*geschweifte\s*klammer\s*[\.,]?\s*",
            r"\s*geschweifte\s*klammer\s*auf\s*[\.,]?\s*",
            r"\s*linke\s*geschwungene\s*klammer\s*[\.,]?\s*",
            r"\s*geschwungene\s*klammer\s*auf\s*[\.,]?\s*",
            r"\s*left\s*curly\s*bracket\s*[\.,]?\s*",
        ],
        "}": [
            r"\s*rechte\s*geschweifte\s*klammer\s*[\.,]?\s*",
            r"\s*geschweifte\s*klammer\s*zu\s*[\.,]?\s*",
            r"\s*rechte\s*geschwungene\s*klammer\s*[\.,]?\s*",
            r"\s*geschwungene\s*klammer\s*zu\s*[\.,]?\s*",
            r"\s*right\s*curly\s*bracket\s*[\.,]?\s*",
        ],
        "<": [
            r"\s*kleiner\s*als\s*zeichen\s*[\.,]?\s*",
            r"\s*kleiner\s*als\s*[\.,]?\s*",
            r"\s*less\s*than\s*sign\s*[\.,]?\s*",
            r"\s*less\s*than\s*[\.,]?\s*",
        ],
        ">": [
            r"\s*größer\s*als\s*zeichen\s*[\.,]?\s*",
            r"\s*größer\s*als\s*[\.,]?\s*",
            r"\s*greater\s*than\s*sign\s*[\.,]?\s*",
            r"\s*greater\s*than\s*[\.,]?\s*",
        ],
        "=": [
            r"\s*ist\s*gleich\s*zeichen\s*[\.,]?\s*",
            r"\s*ist\s*gleich\s*[\.,]?\s*",
            r"\s*gleich\s*zeichen\s*[\.,]?\s*",
            r"\s*equal\s*sign\s*[\.,]?\s*",
            r"\s*equals\s*sign\s*[\.,]?\s*",
        ],
        "+": [
            r"\s*plus\s*symbol\s*[\.,]?\s*",
            r"\s*plus\s*zeichen\s*[\.,]?\s*",
            r"\s*plus\s*sign\s*[\.,]?\s*",
        ],
        "-": [
            r"\s*minus\s*symbol\s*[\.,]?\s*",
            r"\s*minus\s*zeichen\s*[\.,]?\s*",
            r"\s*minus\s*sign\s*[\.,]?\s*",
        ],
        "*": [
            r"\s*mal\s*symbol\s*[\.,]?\s*",
            r"\s*mal\s*zeichen\s*[\.,]?\s*",
            r"\s*multiplication\s*sign\s*[\.,]?\s*",
            r"\s*multiplication\s*symbol\s*[\.,]?\s*",
            r"\s*asterisk\s*[\.,]?\s*",
        ],
        "/": [
            r"\s*durch\s*symbol\s*[\.,]?\s*",
            r"\s*durch\s*zeichen\s*[\.,]?\s*",
            r"\s*division\s*sign\s*[\.,]?\s*",
            r"\s*division\s*symbol\s*[\.,]?\s*",
            r"\s*slash\s*[\.,]?\s*",
        ],
        "`": [
            r"\s*back\s*tick\s*[\.,]?\s*",
            r"\s*back\s*quote\s*[\.,]?\s*",
        ],
        "´": [
            r"\s*acute\s*accent\s*[\.,]?\s*",
            r"\s*akzent\s*akut\s*[\.,]?\s*",
        ],
        "'": [
            r"\s*single\s*quote\s*[\.,]?\s*",
            r"\s*single\s*quotation\s*mark\s*[\.,]?\s*",
            r"\s*einfaches\s*anführungszeichen\s*[\.,]?\s*",
            r"\s*einfaches\s*anführungszeichen\s*oben\s*[\.,]?\s*",
            r"\s*apostroph\s*[\.,]?\s*",
        ],
        "\"": [
            r"\s*double\s*quote\s*[\.,]?\s*",
            r"\s*double\s*quotation\s*mark\s*[\.,]?\s*",
            r"\s*double\s*quotation\s*marks\s*[\.,]?\s*",
            r"\s*double\s*quotes\s*[\.,]?\s*",
            r"\s*anführungsstriche\s*[\.,]?\s*",
            r"\s*anführungszeichen\s*[\.,]?\s*",
            r"\s*anführungsstriche\s*oben\s*[\.,]?\s*",
            r"\s*anführungszeichen\s*oben\s*[\.,]?\s*",
        ],
    }
    
    def __init__(self):
        pass
    
    def replace(self, text, replacements=None):
        replacements = replacements or self.REPLACEMENTS
        for replacement, regexes in replacements.items():
            for regex in regexes:
                text = re.sub(regex, replacement, text, flags=re.IGNORECASE)
        return text