"""Transforma eventos brutos da sessao em uma timeline semantica."""

from session_summary import SessionSummary


class TimelineGenerator:
    """Gera etapas humanas a partir de eventos tecnicos capturados."""

    def __init__(self, sessao_id):
        """Guarda a sessao que sera resumida em timeline."""

        self.sessao_id = sessao_id

    def gerar(self):
        """Percorre eventos e transforma padroes conhecidos em etapas."""

        resumo = SessionSummary(
            self.sessao_id
        ).gerar()

        if not resumo:
            return []

        timeline = []

        for evento in resumo["eventos"]:

            app = (
                evento.get("aplicativo")
                or ""
            ).lower()

            titulo = (
                evento.get("titulo_janela")
                or evento.get("janela")
                or ""
            )

            titulo_lower = titulo.lower()

            if self._eh_navegador(app):
                etapa = self._classificar_titulo_web(
                    titulo_lower
                )

                if etapa:
                    timeline.append(etapa)

            if "putty" in app:
                timeline.append("Acesso SSH")

            elif "microsip" in app:
                timeline.append("Teste via MicroSIP")

            elif "powershell" in app or "pwsh" in app:
                timeline.append("Uso do PowerShell")

            elif "cmd" in app:
                timeline.append("Uso do Prompt de Comando")

            elif "anydesk" in app or "mstsc" in app:
                timeline.append("Acesso remoto")

        return list(
            dict.fromkeys(
                timeline
            )
        )

    @staticmethod
    def _eh_navegador(app):
        """Reconhece nomes de processos de navegadores."""

        return any(
            navegador in app
            for navegador in [
                "chrome",
                "edge",
                "msedge",
                "opera",
                "firefox"
            ]
        )

    @staticmethod
    def _classificar_titulo_web(titulo):
        """Mapeia titulos/URLs de paginas para etapas de atendimento."""

        regras = [
            (
                ["glpi", "chamado"],
                "Consulta ao chamado"
            ),
            (
                ["vs omnia", "vsomnia"],
                "Consulta ao VS Omnia"
            ),
            (
                ["wiki"],
                "Consulta a Wiki"
            ),
            (
                ["lista de uras", "/ura/listar"],
                "Acesso a lista de URAs"
            ),
            (
                ["cadastro de ura", "/ura/cadastro"],
                "Cadastro ou edicao de URA"
            ),
            (
                ["criar audio por texto", "elevenlabs", "text to speech"],
                "Criacao de audio por texto"
            ),
            (
                ["converter ogg", "converter wav", "convertio", "converter:"],
                "Conversao de arquivo de audio"
            ),
            (
                ["lista de audios", "lista de audios", "/audio/listar"],
                "Consulta a lista de audios"
            ),
            (
                ["cadastro de audio", "/audio/cadastro"],
                "Cadastro de audio"
            ),
            (
                ["lista de rotas"],
                "Consulta a lista de rotas"
            ),
            (
                ["roteamento"],
                "Ajuste de roteamento"
            ),
            (
                ["lista de filas"],
                "Consulta a lista de filas"
            ),
            (
                ["cadastro de fila"],
                "Cadastro ou edicao de fila"
            ),
            (
                ["realtime"],
                "Validacao em tempo real"
            ),
            (
                ["vsphone", "zendesk.vsphone"],
                "Operacao no VsPhone"
            )
        ]

        for padroes, etapa in regras:
            if any(padrao in titulo for padrao in padroes):
                return etapa

        return None
