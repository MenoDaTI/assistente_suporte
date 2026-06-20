import threading
import time

from window_monitor import obter_janela_ativa
from datetime import datetime
from database import atualizar_duracao_evento

class ActivityMonitor:

    def __init__(self, manager):

        self.manager = manager
        self.ultima_janela = None
        self.rodando = True
        self.evento_atual = None
        self.inicio_evento = None

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
                info["janela"],
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
                        info["janela"],
                        info["aplicativo"]
                    )
                )

                self.inicio_evento = datetime.now()

                print(
                    f"[EVENTO] "
                    f"{info['aplicativo']} | "
                    f"{info['janela']}"
                )

            time.sleep(2)