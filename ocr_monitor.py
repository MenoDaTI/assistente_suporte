"""Captura a janela ativa e extrai texto com EasyOCR quando fizer sentido."""

import mss
import easyocr
import numpy as np

import win32gui


class OCRMonitor:
    """Captura imagens da janela ativa e decide quando aplicar OCR."""

    def __init__(self):
        """Carrega o leitor EasyOCR em portugues e ingles."""

        self.reader = easyocr.Reader(
            ['pt', 'en'],
            gpu=False
        )

    def capturar_janela_ativa(self):
        """Tira screenshot somente da janela atualmente em foco."""

        hwnd = win32gui.GetForegroundWindow()

        left, top, right, bottom = win32gui.GetWindowRect(
            hwnd
        )

        largura = right - left
        altura = bottom - top

        monitor = {
            "left": left,
            "top": top,
            "width": largura,
            "height": altura
        }

        with mss.mss() as sct:

            screenshot = sct.grab(
                monitor
            )

            imagem = np.array(
                screenshot
            )

            return imagem

    def extrair_texto_janela_ativa(self):
        """Executa OCR na captura da janela e devolve texto plano."""

        try:

            imagem = self.capturar_janela_ativa()

            resultado = self.reader.readtext(
                imagem,
                detail=0
            )

            return "\n".join(resultado)

        except Exception as erro:

            print(
                f"Erro OCR: {erro}"
            )

            return ""

    def aplicativo_deve_executar_ocr(
            self,
            aplicativo):
        """Mantem compatibilidade com a regra antiga baseada em aplicativo."""

        return (
                aplicativo.lower()
                in APLICATIVOS_OCR
        )

    def contexto_deve_executar_ocr(
            self,
            aplicativo,
            titulo):
        """Decide OCR por aplicativo e, em navegadores, por titulo relevante."""

        aplicativo = (
            aplicativo
            or ""
        ).lower()

        titulo = (
            titulo
            or ""
        ).lower()

        if aplicativo in APLICATIVOS_OCR:
            return True

        if aplicativo not in NAVEGADORES_OCR:
            return False

        return any(
            termo in titulo
            for termo in TERMOS_OCR_WEB
        )

APLICATIVOS_OCR = [

    "putty.exe",

    "cmd.exe",

    "powershell.exe",

    "pwsh.exe",

    "anydesk.exe",

    "mstsc.exe",

    "microsip.exe"
]

NAVEGADORES_OCR = [

    "chrome.exe",

    "msedge.exe",

    "opera.exe",

    "opera_gx.exe",

    "firefox.exe"
]

TERMOS_OCR_WEB = [

    "glpi",

    "chamado",

    "ura",

    "audio",

    "Ã¡udio",

    "rota",

    "roteamento",

    "fila",

    "realtime",

    "vsphone",

    "zendesk",

    "vsomnia",

    "vs omnia"
]
