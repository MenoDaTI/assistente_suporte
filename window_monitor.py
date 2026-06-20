import win32gui
import win32process
import psutil


def obter_janela_ativa():

    try:

        hwnd = win32gui.GetForegroundWindow()

        titulo = win32gui.GetWindowText(hwnd)

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        processo = psutil.Process(pid)

        aplicativo = processo.name()

        return {
            "janela": titulo,
            "aplicativo": aplicativo
        }

    except Exception as e:

        return {
            "janela": "DESCONHECIDO",
            "aplicativo": "DESCONHECIDO"
        }