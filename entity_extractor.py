"""Extrai entidades tecnicas a partir de titulos, URLs, OCR e formularios."""

import re
from urllib.parse import urlparse


class EntityExtractor:
    """Conjunto de regras simples para achar entidades relevantes em texto."""

    @staticmethod
    def extrair(texto):
        """Extrai entidades conhecidas e remove duplicidades."""

        entidades = []

        if not texto:
            return entidades

        ips = re.findall(
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            texto
        )

        for ip in ips:

            entidades.append(
                ("IP", ip)
            )

        ramais = re.findall(
            r"(?<![a-z0-9:-])\b[1-9][0-9]{3}\b(?![a-z0-9-])",
            texto,
            flags=re.IGNORECASE
        )

        for ramal in ramais:

            entidades.append(
                ("RAMAL", ramal)
            )

        comandos = [

            "sip show peers",
            "core reload",
            "pjsip show endpoints",
            "reload"
        ]

        for comando in comandos:

            if comando.lower() in texto.lower():

                entidades.append(
                ("COMANDO", comando)
                )

        protocolos = re.findall(
            r"\b(?:ID|protocolo|chamado)\s*#?:?\s*([0-9]{5,})\b",
            texto,
            flags=re.IGNORECASE
        )

        for protocolo in protocolos:
            entidades.append(
                ("PROTOCOLO", protocolo)
            )

        urls = re.findall(
            r"\b(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?::[0-9]+)?(?:/[^\s]*)?",
            texto,
            flags=re.IGNORECASE
        )

        for url in urls:
            dominio = EntityExtractor._extrair_dominio(url)

            if dominio:
                entidades.append(
                    ("DOMINIO", dominio)
                )

        sistemas = {
            "GLPI": ["glpi", "chamado"],
            "VSPHONE": ["vsphone", "zendesk.vsphone"],
            "VSOMNIA": ["vsomnia", "vs omnia"],
            "ELEVENLABS": ["elevenlabs"],
            "CONVERTIO": ["convertio"],
            "ASTERISK": ["asterisk"],
            "WIKI": ["wiki"]
        }

        texto_lower = texto.lower()

        for sistema, padroes in sistemas.items():
            if any(padrao in texto_lower for padrao in padroes):
                entidades.append(
                    ("SISTEMA", sistema)
                )

        modulos = {
            "URA": ["ura", "uras"],
            "AUDIO": ["audio", "áudio", "audios", "áudios"],
            "ROTA": ["rota", "rotas", "roteamento"],
            "FILA": ["fila", "filas"],
            "REALTIME": ["realtime"],
            "CHAMADO": ["chamado", "glpi"]
        }

        for modulo, padroes in modulos.items():
            if any(padrao in texto_lower for padrao in padroes):
                entidades.append(
                    ("MODULO", modulo)
                )

        acoes = {
            "CADASTRO": ["cadastro", "cadastrar", "criar"],
            "LISTAGEM": ["lista", "listar"],
            "INCLUSAO": ["inclusão", "inclusao", "incluir"],
            "CONVERSAO": ["converter", "conversão", "conversao"],
            "VALIDACAO": ["validar", "validação", "validacao", "realtime"],
            "ROTEAMENTO": ["roteamento", "rota"]
        }

        for acao, padroes in acoes.items():
            if any(padrao in texto_lower for padrao in padroes):
                entidades.append(
                    ("ACAO", acao)
                )

        return EntityExtractor._deduplicar(entidades)

    @staticmethod
    def _extrair_dominio(url):
        """Normaliza uma URL e devolve apenas seu dominio."""

        if not url:
            return None

        valor = url

        if not valor.startswith(("http://", "https://")):
            valor = f"http://{valor}"

        try:
            dominio = urlparse(valor).netloc.lower()

            if dominio.endswith(".py"):
                return None

            return dominio
        except Exception:
            return None

    @staticmethod
    def _deduplicar(entidades):
        """Mantem a primeira ocorrencia de cada par tipo/valor."""

        vistas = set()
        resultado = []

        for tipo, valor in entidades:
            chave = (
                tipo,
                str(valor).strip()
            )

            if chave[1] and chave not in vistas:
                vistas.add(chave)
                resultado.append(chave)

        return resultado
