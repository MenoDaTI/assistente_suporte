"""Executa um teste manual direto do analisador de contexto por IA."""

from ai_context_analyzer import AIContextAnalyzer

ia = AIContextAnalyzer()

# Exemplo fixo que valida se o modelo local classifica um cenario VOIP.
resultado = ia.analisar(
    janela="172.16.11.77 - PuTTY",
    aplicativo="putty.exe",
    texto_ocr="""
asterisk -rvvv
sip show peers
core reload
ramal 2001
""",
    protocolo="20260625001",
    cliente="Cliente Teste",
    descricao="Ramal não registra",
    timeline=[
        "Consulta ao VS Omnia",
        "Consulta à Wiki",
        "Acesso SSH",
        "Teste via MicroSIP"
    ],
    categorias_navegacao=[
        "OMNIA",
        "WIKI"
    ]
)

print(resultado)
