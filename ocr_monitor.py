import mss
import easyocr
import numpy as np

import win32gui


class OCRMonitor:

    def __init__(self):

        self.reader = easyocr.Reader(
            ['pt', 'en'],
            gpu=False
        )

    def capturar_janela_ativa(self):

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

        return (
                aplicativo.lower()
                in APLICATIVOS_OCR
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