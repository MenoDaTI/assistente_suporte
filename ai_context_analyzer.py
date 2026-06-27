"""Monta prompts, chama Ollama e normaliza o contexto retornado pela IA."""

import json
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"


class AIContextAnalyzer:
    """Cliente do Ollama responsavel por transformar contexto em JSON tecnico."""

    def __init__(self):
        """Define o modelo local usado nas chamadas."""
        self.model = MODEL

    def analisar(
            self,
            janela,
            aplicativo,
            texto_ocr="",
            protocolo=None,
            cliente=None,
            descricao=None,
            timeline=None,
            categorias_navegacao=None):
        """Monta prompt, chama Ollama e devolve contexto normalizado."""

        prompt = self._montar_prompt(
            janela=janela,
            aplicativo=aplicativo,
            texto_ocr=texto_ocr,
            protocolo=protocolo,
            cliente=cliente,
            descricao=descricao,
            timeline=timeline,
            categorias_navegacao=categorias_navegacao
        )

        try:
            resposta = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=240
            )

            resposta.raise_for_status()

            dados = resposta.json()

            texto_resposta = dados.get(
                "response",
                ""
            )

            contexto = self._extrair_json(
                texto_resposta
            )

            return self._normalizar_contexto(
                contexto
            )

        except Exception as erro:
            return self._contexto_erro(
                str(erro)
            )

    def _montar_prompt(
            self,
            janela,
            aplicativo,
            texto_ocr,
            protocolo,
            cliente,
            descricao,
            timeline,
            categorias_navegacao):
        """Cria o prompt com regras de classificacao e dados da sessao."""

        timeline = timeline or []
        categorias_navegacao = categorias_navegacao or []

        return f"""
Você é um Analista Sênior de Suporte Técnico da Virtual Sistemas.

Sua função é analisar o contexto capturado do computador de um analista de suporte e identificar o que provavelmente está acontecendo no atendimento.

Ambiente comum:
- VS Omnia
- VsPhone
- Wiki Virtual Sistemas
- MicroSIP
- PuTTY
- AnyDesk
- Prompt de Comando
- PowerShell
- Asterisk
- Linux
- Windows
- Telefonia VoIP
- SIP
- PJSIP
- Ramais
- Troncos

Responda SOMENTE com JSON válido.
Não escreva explicações fora do JSON.
Não use markdown.
Não use ```json.

Campos obrigatórios:

{{
  "categoria": "",
  "subcategoria": "",
  "sistema": "",
  "aplicativo": "",
  "tipo_atendimento": "",
  "objetivo_detectado": "",
  "acoes_detectadas": [],
  "tecnologias": [],
  "entidades": {{
    "ips": [],
    "ramais": [],
    "comandos": [],
    "protocolos": []
  }},
  "proximo_passo_sugerido": "",
  "nivel_complexidade": "",
  "confianca": 0.0
}}

Regras obrigatórias de classificação:

- Se o OCR ou a timeline contiver "asterisk", "sip", "pjsip", "ramal", "peer", "endpoint", "core reload", "sip show peers" ou "MicroSIP", a categoria DEVE ser "VOIP".
- Se o aplicativo for "putty.exe" e houver comandos SIP/Asterisk no OCR, a categoria DEVE ser "VOIP".
- Se houver "sip show peers", "pjsip show endpoints", "core reload" ou "asterisk -rvvv", a subcategoria DEVE ser "ASTERISK".
- O campo sistema deve ser "Asterisk" quando houver comandos Asterisk.
- O campo tipo_atendimento deve ser uma frase técnica curta, por exemplo: "Diagnóstico de ramal SIP", "Validação de tronco SIP", "Análise de registro VoIP".
- Nunca use termos estranhos como "DESLIGNAMENTO DE SERVIÇO".
- Protocolos devem ser apenas números/códigos de atendimento, nunca "SSH" ou "SIP".
- Se detectar comandos Asterisk, inclua-os em entidades.comandos.
- Se detectar IPs, inclua-os em entidades.ips.
- Se detectar ramais, inclua-os em entidades.ramais.
- confianca deve ser entre 0 e 1.

DADOS DA SESSÃO:
Protocolo: {protocolo}
Cliente: {cliente}
Descrição: {descricao}

JANELA ATIVA:
{janela}

APLICATIVO:
{aplicativo}

CATEGORIAS DE NAVEGAÇÃO:
{categorias_navegacao}

TIMELINE:
{timeline}

OCR:
{texto_ocr}
"""

    def _extrair_json(self, texto):
        """Extrai JSON puro mesmo quando o modelo responde com texto extra."""

        if not texto:
            return {}

        texto = texto.strip()

        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            pass

        match = re.search(
            r"\{.*\}",
            texto,
            re.DOTALL
        )

        if match:
            try:
                return json.loads(
                    match.group(0)
                )
            except json.JSONDecodeError:
                return {}

        return {}

    def _normalizar_contexto(self, contexto):
        """Garante chaves obrigatorias, tipos esperados e valores padrao."""

        contexto_padrao = {
            "categoria": "GERAL",
            "subcategoria": "",
            "sistema": "",
            "aplicativo": "",
            "tipo_atendimento": "",
            "objetivo_detectado": "",
            "acoes_detectadas": [],
            "tecnologias": [],
            "entidades": {
                "ips": [],
                "ramais": [],
                "comandos": [],
                "protocolos": []
            },
            "proximo_passo_sugerido": "",
            "nivel_complexidade": "BAIXA",
            "confianca": 0.0
        }

        if not isinstance(contexto, dict):
            return contexto_padrao

        for chave, valor in contexto.items():
            if chave in contexto_padrao:
                contexto_padrao[chave] = valor

        if not isinstance(
                contexto_padrao["acoes_detectadas"],
                list):
            contexto_padrao["acoes_detectadas"] = []

        if not isinstance(
                contexto_padrao["tecnologias"],
                list):
            contexto_padrao["tecnologias"] = []

        if not isinstance(
                contexto_padrao["entidades"],
                dict):
            contexto_padrao["entidades"] = {
                "ips": [],
                "ramais": [],
                "comandos": [],
                "protocolos": []
            }

        try:
            contexto_padrao["confianca"] = float(
                contexto_padrao["confianca"]
            )
        except Exception:
            contexto_padrao["confianca"] = 0.0
        # Normaliza nível de complexidade
        nivel = str(
            contexto_padrao["nivel_complexidade"]
        ).upper()

        if nivel in ["MÉDIO", "MEDIO"]:
            nivel = "MEDIA"

        if nivel not in ["BAIXA", "MEDIA", "ALTA"]:
            nivel = "BAIXA"

        contexto_padrao["nivel_complexidade"] = nivel

        # Remove protocolos inválidos
        protocolos = contexto_padrao["entidades"].get(
            "protocolos",
            []
        )

        contexto_padrao["entidades"]["protocolos"] = [
            str(protocolo)
            for protocolo in protocolos
            if str(protocolo).isdigit()
               and len(str(protocolo)) >= 6
        ]

        # Preenche campos vazios com base no contexto detectado
        if (
                contexto_padrao["categoria"] == "VOIP"
                and contexto_padrao["subcategoria"] == "ASTERISK"
        ):

            if not contexto_padrao["objetivo_detectado"]:
                contexto_padrao["objetivo_detectado"] = (
                    "Diagnóstico de ramal SIP em ambiente Asterisk"
                )

            if not contexto_padrao["acoes_detectadas"]:
                contexto_padrao["acoes_detectadas"] = [
                    "Acesso ao console Asterisk",
                    "Consulta de registros SIP",
                    "Reload de configuração"
                ]

            if not contexto_padrao["tecnologias"]:
                contexto_padrao["tecnologias"] = [
                    "Asterisk",
                    "SIP",
                    "SSH",
                    "MicroSIP"
                ]

        return contexto_padrao

    def _contexto_erro(self, erro):
        """Converte falhas de Ollama/rede em resposta padronizada."""

        return {
            "categoria": "ERRO",
            "subcategoria": "",
            "sistema": "",
            "aplicativo": "",
            "tipo_atendimento": "",
            "objetivo_detectado": f"Erro ao analisar contexto: {erro}",
            "acoes_detectadas": [],
            "tecnologias": [],
            "entidades": {
                "ips": [],
                "ramais": [],
                "comandos": [],
                "protocolos": []
            },
            "proximo_passo_sugerido": "",
            "nivel_complexidade": "BAIXA",
            "confianca": 0.0
        }
