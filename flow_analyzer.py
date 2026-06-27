"""Classifica o tipo geral do atendimento a partir dos aplicativos usados."""

class FlowAnalyzer:
    """Agrupa eventos em fluxos conhecidos de suporte."""

    @staticmethod
    def classificar_fluxo(eventos):
        """Classifica a sessao por combinacao de aplicativos usados."""

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
