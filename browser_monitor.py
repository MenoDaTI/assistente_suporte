NAVEGADORES = [

    "chrome.exe",
    "msedge.exe",
    "opera.exe",
    "opera_gx.exe",
    "firefox.exe"
]


class BrowserMonitor:

    @staticmethod
    def eh_navegador(aplicativo):

        if not aplicativo:
            return False

        return aplicativo.lower() in NAVEGADORES

    @staticmethod
    def classificar_pagina(titulo):

        titulo = titulo.lower()

        if "vs omnia" in titulo:
            return "OMNIA"

        if "vsomnia" in titulo:
            return "OMNIA"

        if "wiki" in titulo:
            return "WIKI"

        if "vsphone" in titulo:
            return "VSPHONE"

        if "chatgpt" in titulo:
            return "CHATGPT"

        if "openai" in titulo:
            return "CHATGPT"

        if "asterisk" in titulo:
            return "DOCUMENTACAO"

        return "OUTRO"

    @staticmethod
    def extrair_contexto(info):

        categoria = (
            BrowserMonitor.classificar_pagina(
                info["titulo_janela"]
            )
        )

        return {
            "navegador": info["aplicativo"],
            "titulo": info["titulo_janela"],
            "categoria": categoria
        }