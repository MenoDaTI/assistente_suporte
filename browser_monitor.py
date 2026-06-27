"""Classifica navegacao e combina titulo da janela com conteudo web."""

from browser_content_monitor import BrowserContentMonitor


NAVEGADORES = [
    "chrome.exe",
    "msedge.exe",
    "opera.exe",
    "opera_gx.exe",
    "firefox.exe"
]


class BrowserMonitor:
    """Identifica navegadores, classifica paginas e enriquece contexto web."""

    def __init__(self):
        """Inicializa o capturador de conteudo web usado pelo monitor."""

        self.content_monitor = BrowserContentMonitor()

    @staticmethod
    def eh_navegador(aplicativo):
        """Verifica se o processo ativo e um navegador suportado."""

        if not aplicativo:
            return False

        return aplicativo.lower() in NAVEGADORES

    @staticmethod
    def classificar_pagina(titulo, url=None):
        """Converte titulo/URL em uma categoria de negocio conhecida."""

        texto = " ".join([
            titulo or "",
            url or ""
        ]).lower()

        if "glpi" in texto or "chamado" in texto:
            return "GLPI"

        if "vs omnia" in texto or "vsomnia" in texto:
            return "OMNIA"

        if "wiki" in texto:
            return "WIKI"

        if "vsphone" in texto or "zendesk.vsphone" in texto:
            return "VSPHONE"

        if "ura" in texto or "uras" in texto:
            return "URA"

        if "audio" in texto:
            return "AUDIO"

        if "rota" in texto or "roteamento" in texto:
            return "ROTEAMENTO"

        if "fila" in texto:
            return "FILA"

        if "realtime" in texto:
            return "VALIDACAO"

        if "elevenlabs" in texto:
            return "TTS"

        if "convertio" in texto or "converter" in texto:
            return "CONVERSAO_AUDIO"

        if "chatgpt" in texto or "openai" in texto:
            return "CHATGPT"

        if "asterisk" in texto:
            return "DOCUMENTACAO"

        return "OUTRO"

    def extrair_contexto(self, info):
        """Monta o contexto de navegacao usado por banco, timeline e IA."""

        conteudo_web = self.content_monitor.extrair(
            info["titulo_janela"],
            info["aplicativo"]
        )

        categoria = BrowserMonitor.classificar_pagina(
            info["titulo_janela"],
            conteudo_web.get("url")
        )

        return {
            "navegador": info["aplicativo"],
            "titulo": info["titulo_janela"],
            "categoria": categoria,
            "url": conteudo_web.get("url"),
            "conteudo_web": conteudo_web
        }
