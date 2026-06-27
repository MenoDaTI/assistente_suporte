"""Interface Tkinter para iniciar, acompanhar e finalizar atendimentos."""

import tkinter as tk
from tkinter import simpledialog
from datetime import datetime
from support_brain import SupportBrain
from database import (
    contar_sessoes_hoje,
    contar_eventos_sessao,
    contar_aplicativos_sessao
)


class AssistenteGUI:
    """Painel simples para controlar sessao e disparar analise final."""
    """Painel simples para controlar sessao e disparar analise final."""
    """Painel simples para controlar sessao e disparar analise final."""

    def __init__(self, manager):
        """Monta todos os elementos visuais e inicia atualizacao de status."""
        """Monta todos os elementos visuais e inicia atualizacao de status."""
        """Monta todos os elementos visuais e inicia atualizacao de status."""

        self.manager = manager

        self.root = tk.Tk()

        self.root.title("Assistente de Suporte")
        self.root.geometry("340x380")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.inicio_sessao = None

        # =========================
        # TÍTULO
        # =========================

        titulo = tk.Label(
            self.root,
            text="Assistente de Suporte",
            font=("Arial", 12, "bold")
        )

        titulo.pack(pady=10)

        # =========================
        # PROTOCOLO
        # =========================

        self.lbl_protocolo = tk.Label(
            self.root,
            text="Protocolo: Nenhum"
        )

        self.lbl_protocolo.pack()

        # =========================
        # CLIENTE
        # =========================

        self.lbl_cliente = tk.Label(
            self.root,
            text="Cliente: Nenhum"
        )

        self.lbl_cliente.pack()

        # =========================
        # STATUS
        # =========================

        self.lbl_status = tk.Label(
            self.root,
            text="Status: Aguardando"
        )

        self.lbl_status.pack()

        # =========================
        # TEMPO
        # =========================

        self.lbl_tempo = tk.Label(
            self.root,
            text="Tempo: 00:00:00"
        )

        self.lbl_tempo.pack(pady=10)

        # =========================
        # SESSÕES HOJE
        # =========================

        self.lbl_sessoes = tk.Label(
            self.root,
            text="Sessões Hoje: 0"
        )

        self.lbl_sessoes.pack(pady=5)

        # =========================
        # Eventos Capturados
        # =========================

        self.lbl_eventos = tk.Label(
            self.root,
            text="Eventos Capturados: 0"
        )

        self.lbl_eventos.pack()

        # =========================
        # APLICATIVOS UTILIZADOS
        # =========================

        self.lbl_aplicativos = tk.Label(
            self.root,
            text="Aplicativos Utilizados: 0"
        )

        self.lbl_aplicativos.pack(pady=5)

        # =========================
        # BOTÃO INICIAR
        # =========================

        btn_iniciar = tk.Button(
            self.root,
            text="Iniciar Resolução",
            width=20,
            command=self.iniciar_sessao
        )

        btn_iniciar.pack(pady=(15, 5))

        # =========================
        # BOTÃO FINALIZAR
        # =========================

        btn_finalizar = tk.Button(
            self.root,
            text="Finalizar Resolução",
            width=20,
            command=self.finalizar_sessao
        )

        btn_finalizar.pack(pady=5)

        self.atualizar_tempo()

    def iniciar_sessao(self):
        """Coleta protocolo, cliente e descricao antes de abrir sessao."""
        """Coleta protocolo, cliente e descricao antes de abrir sessao."""
        """Coleta protocolo/cliente/descricao e abre uma nova sessao."""

        protocolo = simpledialog.askstring(
            "Protocolo",
            "Digite o protocolo:"
        )

        if not protocolo:
            return

        cliente = simpledialog.askstring(
            "Cliente",
            "Nome do cliente:"
        )

        descricao = simpledialog.askstring(
            "Descrição",
            "Descrição rápida:"
        )

        if descricao is None:
            descricao = ""

        self.manager.iniciar_sessao(
            protocolo,
            descricao,
            cliente
        )

        self.lbl_status.config(
            text="Status: EM ANDAMENTO"
        )

        self.inicio_sessao = datetime.now()

    def finalizar_sessao(self):
        """Finaliza a sessao e executa o SupportBrain quando ha id valido."""
        """Finaliza a sessao e executa o SupportBrain quando ha id valido."""
        """Finaliza a sessao e executa o SupportBrain para gerar analise."""

        sessao_id = self.manager.finalizar_sessao()

        self.lbl_status.config(
            text="Status: Analisando IA..."
        )

        self.lbl_tempo.config(
            text="Tempo: 00:00:00"
        )

        self.inicio_sessao = None

        if sessao_id:

            try:

                brain = SupportBrain(sessao_id)

                resultado = brain.analisar_sessao()

                print()
                print("================================")
                print("ANÁLISE IA CONCLUÍDA")
                print(resultado)
                print("================================")
                print()

                self.lbl_status.config(
                    text="Status: FINALIZADA + IA"
                )

            except Exception as erro:

                print(f"Erro ao executar SupportBrain: {erro}")

                self.lbl_status.config(
                    text="Status: FINALIZADA"
                )

    def atualizar_tempo(self):
        """Atualiza status, cronometro e contadores exibidos na GUI."""
        """Atualiza status, cronometro e contadores exibidos na GUI."""
        """Atualiza labels de status, tempo, eventos e aplicativos usados."""

        # Protocolo

        if self.manager.protocolo_ativo:
            self.lbl_protocolo.config(
                text=f"Protocolo: {self.manager.protocolo_ativo}"
            )
        else:
            self.lbl_protocolo.config(
                text="Protocolo: Nenhum"
            )

        # Cliente

        if self.manager.cliente_ativo:
            self.lbl_cliente.config(
                text=f"Cliente: {self.manager.cliente_ativo}"
            )
        else:
            self.lbl_cliente.config(
                text="Cliente: Nenhum"
            )

        # Sessões do dia

        total_sessoes = contar_sessoes_hoje()

        self.lbl_sessoes.config(
            text=f"Sessões Hoje: {total_sessoes}"
        )

        # Tempo da sessão

        if self.inicio_sessao:

            tempo = (
                datetime.now()
                - self.inicio_sessao
            )

            total = int(
                tempo.total_seconds()
            )

            horas = total // 3600
            minutos = (total % 3600) // 60
            segundos = total % 60

            self.lbl_tempo.config(
                text=f"Tempo: {horas:02}:{minutos:02}:{segundos:02}"
            )

            self.root.after(
                1000,
                self.atualizar_tempo
            )
        if self.manager.sessao_ativa:

            total_eventos = contar_eventos_sessao(
                self.manager.sessao_ativa
            )

            total_apps = contar_aplicativos_sessao(
                self.manager.sessao_ativa
            )

            self.lbl_eventos.config(
                text=f"Eventos Capturados: {total_eventos}"
            )

            self.lbl_aplicativos.config(
                text=f"Aplicativos Utilizados: {total_apps}"
            )

        else:

            self.lbl_eventos.config(
                text="Eventos Capturados: 0"
            )

            self.lbl_aplicativos.config(
                text="Aplicativos Utilizados: 0"
            )

    def executar(self):
        """Inicia o loop principal do Tkinter."""
        """Inicia o loop principal do Tkinter."""
        """Entrega o controle para o loop principal do Tkinter."""
        self.root.mainloop()
