class FlowAnalyzer:

    @staticmethod
    def classificar_fluxo(eventos):

        apps = [
            evento["aplicativo"].lower()
            for evento in eventos
        ]

        if (
            "putty.exe" in apps
            and "microsip.exe" in apps
        ):

            return "SUPORTE_VOIP"

        if (
            "anydesk.exe" in apps
        ):

            return "SUPORTE_REMOTO"

        return "GERAL"