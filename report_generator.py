"""Gera um relatorio tecnico estruturado a partir dos dados da sessao."""

from session_summary import SessionSummary


class ReportGenerator:
    """Monta uma versao textual estruturada da sessao."""

    def __init__(self, sessao_id):
        """Guarda a sessao que sera transformada em relatorio."""

        self.sessao_id = sessao_id

    def gerar_relatorio(self):
        """Organiza cabecalho, apps, entidades e cronologia em texto."""

        resumo = SessionSummary(
            self.sessao_id
        ).gerar()

        if not resumo:

            return "Sessão não encontrada."

        linhas = []

        # =================================
        # CABEÇALHO
        # =================================

        linhas.append(
            f"PROTOCOLO: {resumo['protocolo']}"
        )

        linhas.append(
            f"CLIENTE: {resumo['cliente']}"
        )

        linhas.append(
            f"DESCRIÇÃO: {resumo['descricao']}"
        )

        linhas.append("")

        # =================================
        # APLICATIVOS UTILIZADOS
        # =================================

        linhas.append(
            "APLICATIVOS UTILIZADOS:"
        )

        for app in resumo["aplicativos"]:

            linhas.append(
                f" - {app}"
            )

        linhas.append("")

        # =================================
        # NAVEGAÇÃO
        # =================================

        if resumo["categorias_navegacao"]:

            linhas.append(
                "FONTES CONSULTADAS:"
            )

            for categoria in resumo[
                "categorias_navegacao"
            ]:

                linhas.append(
                    f" - {categoria}"
                )

            linhas.append("")

        # =================================
        # ENTIDADES
        # =================================

        ips = []
        comandos = []
        ramais = []

        for entidade in resumo["entidades"]:
            # Separa entidades por tipo para montar secoes legiveis.

            tipo = entidade["tipo"]
            valor = entidade["valor"]

            if tipo == "IP":
                ips.append(valor)

            elif tipo == "COMANDO":
                comandos.append(valor)

            elif tipo == "RAMAL":
                ramais.append(valor)

        if ips:

            linhas.append(
                "SERVIDORES ACESSADOS:"
            )

            for ip in set(ips):

                linhas.append(
                    f" - {ip}"
                )

            linhas.append("")

        if ramais:

            linhas.append(
                "RAMAIS IDENTIFICADOS:"
            )

            for ramal in set(ramais):

                linhas.append(
                    f" - {ramal}"
                )

            linhas.append("")

        if comandos:

            linhas.append(
                "COMANDOS EXECUTADOS:"
            )

            for comando in set(comandos):

                linhas.append(
                    f" - {comando}"
                )

            linhas.append("")

        # =================================
        # TIMELINE
        # =================================

        linhas.append(
            "CRONOLOGIA:"
        )

        for evento in resumo["eventos"]:

            linhas.append(
                f"[{evento['data_hora']}] "
                f"{evento['aplicativo']} "
                f"-> "
                f"{evento['janela']}"
            )

        linhas.append("")

        # =================================
        # RESUMO FINAL
        # =================================

        linhas.append(
            "RESUMO:"
        )

        linhas.append(
            "Atendimento registrado automaticamente "
            "pelo Assistente de Suporte."
        )

        return "\n".join(linhas)
