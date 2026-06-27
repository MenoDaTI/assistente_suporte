"""Le o titulo, processo e PID da janela atualmente em foco no Windows."""

import win32gui
import win32process
import psutil


class ContextMonitor:
    """Consulta APIs do Windows para identificar a janela em primeiro plano."""

    @staticmethod
    def obter_contexto_ativo():
        """Retorna titulo, processo e PID da janela ativa."""

        try:

            hwnd = win32gui.GetForegroundWindow()

            titulo = win32gui.GetWindowText(hwnd)

            _, pid = win32process.GetWindowThreadProcessId(
                hwnd
            )

            processo = psutil.Process(pid)

            aplicativo = processo.name()

            return {
                "titulo": titulo,
                "aplicativo": aplicativo,
                "pid": pid
            }

        except Exception as erro:

            print(
                f"Erro ao obter contexto: {erro}"
            )

            return {
                "titulo": None,
                "aplicativo": None,
                "pid": None
            }
