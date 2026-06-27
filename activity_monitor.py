"""Monitora janelas, OCR e navegacao durante uma sessao ativa."""

import threading
import time
import hashlib

from window_monitor import obter_janela_ativa
from datetime import datetime
from database import atualizar_duracao_evento
from ocr_monitor import OCRMonitor
from browser_monitor import BrowserMonitor

class ActivityMonitor:
    """Coordena polling de janela, OCR e navegacao enquanto o app roda."""

    def __init__(self, manager):
        """Recebe o gerenciador da sessao e inicializa estado de deduplicacao."""

        self.manager = manager
        self.ultima_janela = None
        self.rodando = True
        self.evento_atual = None
        self.inicio_evento = None
        self.ocr = OCRMonitor()
        self.browser = BrowserMonitor()
        self.ultimo_ocr_hash = None
        self.ultima_navegacao = None

    def iniciar(self):
        """Inicia o loop de monitoramento em uma thread daemon."""

        thread = threading.Thread(
            target=self.monitorar,
            daemon=True
        )

        thread.start()

    def monitorar(self):
        """Loop principal: detecta mudancas, salva eventos e enriquece contexto."""

        while self.rodando:

            # Captura o contexto atual da janela em foco no Windows.
            info = obter_janela_ativa()

            janela_atual = (
                info["titulo_janela"],
                info["aplicativo"]
            )

            if janela_atual != self.ultima_janela:

                # Uma nova janela fecha o tempo de permanencia da anterior.
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

                # OCR e caro; por isso so roda em contextos com valor tecnico.
                if self.ocr.contexto_deve_executar_ocr(
                        info["aplicativo"],
                        info["titulo_janela"]):

                    texto = (
                        self.ocr.extrair_texto_janela_ativa()
                    )

                    texto_limpo = texto.strip()

                    if texto_limpo:
                        ocr_hash = hashlib.sha1(
                            texto_limpo.encode("utf-8")
                        ).hexdigest()

                    if (
                            texto_limpo
                            and ocr_hash != self.ultimo_ocr_hash
                    ):
                        # Hash impede duplicar a mesma evidencia visual.
                        self.ultimo_ocr_hash = ocr_hash

                        self.manager.registrar_ocr(
                            origem=info["aplicativo"],
                            texto=texto_limpo
                        )

                        print(
                            "[OCR] Evidência registrada."
                        )

            time.sleep(2)
            if self.browser.eh_navegador(
                    info["aplicativo"]):
                # Navegadores recebem uma captura extra de URL/DOM quando possivel.
                contexto = (
                    self.browser.extrair_contexto(
                        info
                    )
                )

                navegacao_atual = (
                    contexto["navegador"],
                    contexto["titulo"],
                    contexto["categoria"],
                    contexto.get("url")
                )

                if navegacao_atual != self.ultima_navegacao:
                    self.ultima_navegacao = navegacao_atual

                    # Registra uma linha resumida na tabela de navegacao.
                    self.manager.registrar_navegacao(
                        navegador=contexto["navegador"],
                        titulo=contexto["titulo"],
                        categoria=contexto["categoria"],
                        url=contexto.get("url")
                    )

                    # Registra texto visivel, URL e formularios em capturas_contexto.
                    self.manager.registrar_contexto_web(
                        navegador=contexto["navegador"],
                        conteudo_web=contexto.get("conteudo_web"),
                        evento_id=self.evento_atual
                    )

                    print(
                        "[BROWSER] "
                        f"{contexto['categoria']}"
                    )
