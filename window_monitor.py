from context_monitor import ContextMonitor


def obter_janela_ativa():

    try:

        contexto = ContextMonitor.obter_contexto_ativo()

        return {
            "janela": contexto["titulo"],
            "titulo_janela": contexto["titulo"],
            "aplicativo": contexto["aplicativo"],
            "pid": contexto["pid"]
        }

    except Exception as erro:

        print(
            f"Erro no WindowMonitor: {erro}"
        )

        return {
            "janela": "DESCONHECIDO",
            "titulo_janela": "DESCONHECIDO",
            "aplicativo": "DESCONHECIDO",
            "pid": None
        }