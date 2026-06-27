"""Ponto de entrada que inicializa banco, monitores, atalhos e GUI."""

import keyboard
from activity_monitor import ActivityMonitor
from database import criar_tabelas
from session_manager import SessionManager
from gui import AssistenteGUI

manager = SessionManager()
monitor = ActivityMonitor(manager)

def iniciar():
    """Solicita dados basicos e abre uma nova sessao de atendimento."""

    protocolo = input(
        "\nDigite o protocolo: "
    )

    descricao = input(
        "Descrição rápida: "
    )

    manager.iniciar_sessao(
        protocolo,
        descricao
    )


def finalizar():
    """Encerra a sessao ativa pelo atalho global."""
    manager.finalizar_sessao()


def main():
    """Prepara infraestrutura local e inicia a interface grafica."""

    criar_tabelas()
    monitor.iniciar()

    print()
    print("Assistente de Suporte iniciado")
    print()
    print("CTRL + ALT + F9  -> Iniciar")
    print("CTRL + ALT + F10 -> Finalizar")
    print()

    keyboard.add_hotkey(
        "ctrl+alt+f9",
        iniciar
    )

    keyboard.add_hotkey(
        "ctrl+alt+f10",
        finalizar
    )

    gui = AssistenteGUI(manager)

    gui.executar()


if __name__ == "__main__":
    main()
