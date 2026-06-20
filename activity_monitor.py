import threading
import time

from window_monitor import obter_janela_ativa
from datetime import datetime
from database import atualizar_duracao_evento
from ocr_monitor import OCRMonitor
from browser_monitor import BrowserMonitor

class ActivityMonitor:

    def __init__(self, manager):

        self.manager = manager
        self.ultima_janela = None
        self.rodando = True
        self.evento_atual = None
        self.inicio_evento = None
        self.ocr = OCRMonitor()
        self.browser = BrowserMonitor()

    def iniciar(self):

        thread = threading.Thread(
            target=self.monitorar,
            daemon=True
        )

        thread.start()

    def monitorar(self):

        while self.rodando:

            info = obter_janela_ativa()

            janela_atual = (
                info["titulo_janela"],
                info["aplicativo"]
            )

            if janela_atual != self.ultima_janela:

                self.ultima_janela = janela_atual

                if self.evento_atual and self.inicio_evento:

                    duracao = int(
                        (
                                datetime.now()
                                - self.inicio_evento
                        ).total_seconds()
                    )

                    atualizar_duracao_evento(
                        self.evento_atual,
                        duracao
                    )

                self.evento_atual = (
                    self.manager.registrar_janela(
                        janela=info["janela"],
                        aplicativo=info["aplicativo"],
                        titulo_janela=info["titulo_janela"]
                    )
                )

                self.inicio_evento = datetime.now()

                print(
                    f"[EVENTO] "
                    f"{info['aplicativo']} | "
                    f"{info['titulo_janela']}"
                )

                # =========================
                # OCR INTELIGENTE
                # =========================

                if self.ocr.aplicativo_deve_executar_ocr(
                        info["aplicativo"]):

                    texto = (
                        self.ocr.extrair_texto_janela_ativa()
                    )

                    if texto.strip():
                        self.manager.registrar_ocr(
                            origem=info["aplicativo"],
                            texto=texto
                        )

                        print(
                            "[OCR] Evidência registrada."
                        )

            time.sleep(2)
            if self.browser.eh_navegador(
                    info["aplicativo"]):
                contexto = (
                    self.browser.extrair_contexto(
                        info
                    )
                )

                self.manager.registrar_navegacao(
                    navegador=contexto["navegador"],
                    titulo=contexto["titulo"],
                    categoria=contexto["categoria"]
                )

                print(
                    "[BROWSER] "
                    f"{contexto['categoria']}"
                )