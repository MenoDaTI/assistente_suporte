import win32gui
import win32process
import psutil


class ContextMonitor:

    @staticmethod
    def obter_contexto_ativo():

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