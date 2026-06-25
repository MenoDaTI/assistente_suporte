from session_summary import SessionSummary


class TimelineGenerator:

    def __init__(self, sessao_id):

        self.sessao_id = sessao_id

    def gerar(self):

        resumo = SessionSummary(
            self.sessao_id
        ).gerar()

        timeline = []

        eventos = resumo["eventos"]

        for evento in eventos:

            app = (
                evento["aplicativo"]
                or ""
            ).lower()

            titulo = (
                evento["janela"]
                or ""
            )

            if "chrome" in app:

                if "vs omnia" in titulo.lower():
                    timeline.append(
                        "Consulta ao VS Omnia"
                    )

                elif "wiki" in titulo.lower():
                    timeline.append(
                        "Consulta à Wiki"
                    )

            elif "putty" in app:

                timeline.append(
                    "Acesso SSH"
                )

            elif "microsip" in app:

                timeline.append(
                    "Teste via MicroSIP"
                )

            elif "powershell" in app:

                timeline.append(
                    "Uso do PowerShell"
                )

            elif "cmd" in app:

                timeline.append(
                    "Uso do Prompt de Comando"
                )

        return list(
            dict.fromkeys(
                timeline
            )
        )