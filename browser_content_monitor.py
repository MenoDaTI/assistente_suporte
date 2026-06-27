"""Captura URL, texto visivel e formularios de abas web quando possivel."""

import base64
import json
import os
import re
import socket
from urllib.parse import urlparse

import requests


CDP_PORTS = [
    9222,
    9223,
    9224,
    9225
]


class BrowserContentMonitor:
    """Obtem dados da aba ativa via CDP ou por inferencia do titulo."""

    def extrair(self, titulo_janela, aplicativo):
        """Retorna URL, titulo, texto e formularios conhecidos da pagina."""

        # Prioriza CDP porque ele entrega URL real e dados do DOM.
        contexto = self._extrair_por_cdp(
            titulo_janela
        )

        if contexto:
            return contexto

        # Sem CDP, usa o titulo da janela como fonte parcial de URL.
        url = self.inferir_url(
            titulo_janela
        )

        if url:
            return {
                "url": url,
                "titulo_pagina": titulo_janela,
                "texto": "",
                "formularios": [],
                "origem_url": "TITULO_JANELA"
            }

        return {
            "url": None,
            "titulo_pagina": titulo_janela,
            "texto": "",
            "formularios": [],
            "origem_url": None
        }

    def _extrair_por_cdp(self, titulo_janela):
        """Tenta localizar a aba ativa nas portas de remote debugging."""

        abas = self._listar_abas_cdp()

        if not abas:
            return None

        aba = self._selecionar_aba(
            abas,
            titulo_janela
        )

        if not aba:
            return None

        # A lista de abas ja fornece URL/titulo mesmo antes de ler o DOM.
        contexto = {
            "url": aba.get("url"),
            "titulo_pagina": aba.get("title") or titulo_janela,
            "texto": "",
            "formularios": [],
            "origem_url": "CDP"
        }

        ws_url = aba.get("webSocketDebuggerUrl")

        if not ws_url:
            return contexto

        # O websocket permite executar JavaScript dentro da pagina.
        dados_dom = self._avaliar_dom(
            ws_url
        )

        if dados_dom:
            contexto.update(dados_dom)

        return contexto

    def _listar_abas_cdp(self):
        """Consulta portas locais e retorna abas expostas por DevTools."""

        abas = []

        for porta in CDP_PORTS:
            try:
                resposta = requests.get(
                    f"http://127.0.0.1:{porta}/json",
                    timeout=0.4
                )

                if resposta.ok:
                    for aba in resposta.json():
                        if aba.get("type") == "page":
                            abas.append(aba)

            except Exception:
                continue

        return abas

    def _selecionar_aba(
            self,
            abas,
            titulo_janela):
        """Escolhe a aba com maior similaridade ao titulo da janela."""

        titulo_normalizado = self._normalizar_titulo(
            titulo_janela
        )

        melhor = None
        melhor_pontuacao = 0

        for aba in abas:
            titulo_aba = self._normalizar_titulo(
                aba.get("title")
            )

            url = (
                aba.get("url")
                or ""
            ).lower()

            pontuacao = 0

            if titulo_aba and titulo_aba in titulo_normalizado:
                pontuacao += 4

            if titulo_normalizado and titulo_normalizado in titulo_aba:
                pontuacao += 3

            dominio = self._dominio(
                url
            )

            if dominio and dominio in titulo_normalizado:
                pontuacao += 2

            if pontuacao > melhor_pontuacao:
                melhor = aba
                melhor_pontuacao = pontuacao

        if melhor_pontuacao:
            return melhor

        return None

    def _avaliar_dom(self, ws_url):
        """Executa JavaScript na pagina para ler texto e campos de formulario."""

        # Script autocontido para nao depender de bibliotecas no navegador.
        expressao = r"""
(() => {
  const text = (document.body && document.body.innerText || "").slice(0, 5000);
  const fieldLabel = (el) => {
    const labels = Array.from(el.labels || []).map(label => label.innerText.trim()).filter(Boolean);
    if (labels.length) return labels.join(" / ");
    return el.getAttribute("aria-label")
      || el.getAttribute("placeholder")
      || el.getAttribute("name")
      || el.getAttribute("id")
      || "";
  };
  const fieldValue = (el) => {
    if (el.tagName === "SELECT") {
      const selected = Array.from(el.selectedOptions || []).map(option => option.textContent.trim()).filter(Boolean);
      return selected.length ? selected.join(", ") : el.value;
    }
    if (el.type === "password") return "";
    if (el.type === "checkbox" || el.type === "radio") return el.checked ? "marcado" : "desmarcado";
    return el.value || "";
  };
  const fields = Array.from(document.querySelectorAll("input, select, textarea"))
    .map(el => ({
      chave: fieldLabel(el).slice(0, 120),
      tipo: (el.getAttribute("type") || el.tagName || "").toLowerCase(),
      valor: String(fieldValue(el)).slice(0, 500)
    }))
    .filter(item => item.chave || item.valor)
    .slice(0, 80);
  return JSON.stringify({
    url: location.href,
    titulo_pagina: document.title,
    texto,
    formularios: fields
  });
})()
"""

        try:
            # Cliente websocket minimo para enviar Runtime.evaluate ao CDP.
            cliente = _WebSocketCdpClient(
                ws_url,
                timeout=1.5
            )

            resposta = cliente.enviar({
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": expressao,
                    "returnByValue": True,
                    "awaitPromise": True
                }
            })

            cliente.fechar()

            valor = (
                resposta
                .get("result", {})
                .get("result", {})
                .get("value")
            )

            if valor:
                return json.loads(valor)

        except Exception:
            return None

        return None

    @staticmethod
    def inferir_url(titulo):
        """Extrai uma URL ou IP com caminho diretamente do titulo da janela."""

        if not titulo:
            return None

        match = re.search(
            r"((?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?::[0-9]+)?(?:/[^\s]*)?)",
            titulo,
            flags=re.IGNORECASE
        )

        if not match:
            match = re.search(
                r"((?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]+)?(?:/[^\s]*)?)",
                titulo
            )

        if not match:
            return None

        url = match.group(1).rstrip(" -")

        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"

        return url

    @staticmethod
    def _normalizar_titulo(titulo):
        """Remove sufixos de navegadores e espacos extras antes de comparar."""

        titulo = (
            titulo
            or ""
        ).lower()

        for sufixo in [
            " - opera",
            " - google chrome",
            " - chrome",
            " — microsoft edge",
            " - microsoft edge",
            " - mozilla firefox"
        ]:
            titulo = titulo.replace(
                sufixo,
                ""
            )

        return " ".join(
            titulo.split()
        )

    @staticmethod
    def _dominio(url):
        """Extrai dominio para pontuar correspondencia entre aba e janela."""

        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""


class _WebSocketCdpClient:
    """Implementa o minimo de WebSocket necessario para conversar com CDP."""

    def __init__(
            self,
            ws_url,
            timeout=1.5):
        """Abre a conexao websocket e guarda timeout curto para nao travar."""

        self.ws_url = ws_url
        self.timeout = timeout
        self.sock = None
        self._conectar()

    def _conectar(self):
        """Faz handshake WebSocket manual contra o endpoint do navegador."""

        parsed = urlparse(
            self.ws_url
        )

        host = parsed.hostname
        port = parsed.port or 80
        path = parsed.path

        if parsed.query:
            path = f"{path}?{parsed.query}"

        key = base64.b64encode(
            os.urandom(16)
        ).decode("ascii")

        self.sock = socket.create_connection(
            (host, port),
            timeout=self.timeout
        )
        self.sock.settimeout(
            self.timeout
        )

        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )

        self.sock.sendall(
            request.encode("ascii")
        )

        resposta = self.sock.recv(
            4096
        )

        if b" 101 " not in resposta:
            raise RuntimeError("CDP websocket recusado")

    def enviar(self, mensagem):
        """Envia comando JSON e aguarda a resposta do mesmo id."""

        self._send_frame(
            json.dumps(mensagem)
        )

        while True:
            payload = self._recv_frame()

            if not payload:
                continue

            dados = json.loads(
                payload.decode("utf-8")
            )

            if dados.get("id") == mensagem.get("id"):
                return dados

    def fechar(self):
        """Fecha o socket ignorando erros de encerramento."""

        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def _send_frame(self, texto):
        """Monta e envia um frame WebSocket mascarado."""

        payload = texto.encode("utf-8")
        mascara = os.urandom(4)
        tamanho = len(payload)

        frame = bytearray()
        frame.append(0x81)

        if tamanho < 126:
            frame.append(0x80 | tamanho)
        elif tamanho < 65536:
            frame.append(0x80 | 126)
            frame.extend(
                tamanho.to_bytes(2, "big")
            )
        else:
            frame.append(0x80 | 127)
            frame.extend(
                tamanho.to_bytes(8, "big")
            )

        frame.extend(mascara)
        frame.extend(
            byte ^ mascara[index % 4]
            for index, byte in enumerate(payload)
        )

        self.sock.sendall(frame)

    def _recv_frame(self):
        """Le um frame WebSocket e devolve seu payload."""

        header = self._recv_exact(2)

        if not header:
            return b""

        opcode = header[0] & 0x0F
        masked = header[1] & 0x80
        tamanho = header[1] & 0x7F

        if tamanho == 126:
            tamanho = int.from_bytes(
                self._recv_exact(2),
                "big"
            )
        elif tamanho == 127:
            tamanho = int.from_bytes(
                self._recv_exact(8),
                "big"
            )

        mascara = b""

        if masked:
            mascara = self._recv_exact(4)

        payload = self._recv_exact(
            tamanho
        )

        if masked:
            payload = bytes(
                byte ^ mascara[index % 4]
                for index, byte in enumerate(payload)
            )

        if opcode == 0x8:
            return b""

        if opcode == 0x9:
            return b""

        return payload

    def _recv_exact(self, tamanho):
        """Le exatamente a quantidade de bytes solicitada."""

        partes = []
        restante = tamanho

        while restante:
            parte = self.sock.recv(
                restante
            )

            if not parte:
                raise RuntimeError("conexao websocket encerrada")

            partes.append(parte)
            restante -= len(parte)

        return b"".join(partes)
