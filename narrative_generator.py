"""Gera uma narrativa textual do atendimento com base no resumo da sessao."""

from session_summary import SessionSummary
from timeline_generator import TimelineGenerator


class NarrativeGenerator:
    """Converte dados capturados em uma narrativa de atendimento."""

    def __init__(self, sessao_id):
        """Guarda a sessao que sera narrada."""

        self.sessao_id = sessao_id

    def gerar(self):
        """Combina resumo, timeline e entidades em texto corrido."""

        resumo = SessionSummary(
            self.sessao_id
        ).gerar()

        if not resumo:
            return "Sessão não encontrada."

        timeline = TimelineGenerator(
            self.sessao_id
        ).gerar()

        texto = []

        # =====================
        # CABEÇALHO
        # =====================

        protocolo = resumo.get(
            "protocolo"
        )

        cliente = resumo.get(
            "cliente"
        )

        descricao = resumo.get(
            "descricao"
        )

        texto.append(
            f"Atendimento referente ao protocolo "
            f"{protocolo}."
        )

        if cliente:

            texto.append(
                f"Cliente: {cliente}."
            )

        if descricao:

            texto.append(
                f"Descrição inicial: {descricao}."
            )

        texto.append("")

        # =====================
        # TIMELINE
        # =====================

        if timeline:

            texto.append(
                "Fluxo identificado:"
            )

            for indice, etapa in enumerate(
                    timeline,
                    start=1
            ):

                texto.append(
                    f"{indice}. {etapa}"
                )

            texto.append("")

        # =====================
        # NAVEGAÇÃO
        # =====================

        categorias = resumo.get(
            "categorias_navegacao",
            []
        )

        if "WIKI" in categorias:

            texto.append(
                "Durante a análise foi consultada "
                "a documentação da Wiki "
                "Virtual Sistemas."
            )

        if "OMNIA" in categorias:

            texto.append(
                "Foi realizada consulta "
                "ao histórico do atendimento "
                "no VS Omnia."
            )

        texto.append("")

        # =====================
        # IPS
        # =====================

        ips = []

        for entidade in resumo[
            "entidades"
        ]:
            # IPs costumam indicar servidores ou sistemas acessados.

            if entidade["tipo"] == "IP":

                ips.append(
                    entidade["valor"]
                )

        if ips:

            texto.append(
                "Foram identificados "
                "acessos aos seguintes "
                "servidores:"
            )

            for ip in set(ips):

                texto.append(
                    f"- {ip}"
                )

            texto.append("")

        # =====================
        # COMANDOS
        # =====================

        comandos = []

        for entidade in resumo[
            "entidades"
        ]:
            # Comandos ajudam a documentar intervencoes tecnicas.

            if entidade["tipo"] == "COMANDO":

                comandos.append(
                    entidade["valor"]
                )

        if comandos:

            texto.append(
                "Durante a intervenção "
                "foram executados os "
                "seguintes comandos:"
            )

            for comando in set(
                    comandos
            ):

                texto.append(
                    f"- {comando}"
                )

            texto.append("")

        # =====================
        # RAMAIS
        # =====================

        ramais = []

        for entidade in resumo[
            "entidades"
        ]:
            # Ramais ajudam a explicar o escopo do atendimento VoIP.

            if entidade["tipo"] == "RAMAL":

                ramais.append(
                    entidade["valor"]
                )

        if ramais:

            texto.append(
                "Foram identificados os "
                "seguintes ramais durante "
                "a análise:"
            )

            for ramal in set(
                    ramais
            ):

                texto.append(
                    f"- {ramal}"
                )

            texto.append("")

        # =====================
        # APLICATIVOS
        # =====================

        aplicativos = [
            app.lower()
            for app in resumo[
                "aplicativos"
            ]
        ]

        if "putty.exe" in aplicativos:

            texto.append(
                "Foi realizado acesso "
                "SSH para análise do "
                "ambiente."
            )

        if "microsip.exe" in aplicativos:

            texto.append(
                "Foram realizados testes "
                "de telefonia utilizando "
                "o MicroSIP."
            )

        if "anydesk.exe" in aplicativos:

            texto.append(
                "Foi realizado acesso "
                "remoto para validação "
                "junto ao usuário."
            )

        if "powershell.exe" in aplicativos:

            texto.append(
                "Foram realizadas análises "
                "e procedimentos através "
                "do PowerShell."
            )

        if "cmd.exe" in aplicativos:

            texto.append(
                "Foram executados comandos "
                "utilizando o Prompt de "
                "Comando do Windows."
            )

        texto.append("")

        # =====================
        # ENCERRAMENTO
        # =====================

        texto.append(
            "Atendimento registrado "
            "automaticamente pelo "
            "Assistente de Suporte."
        )

        return "\n".join(texto)
