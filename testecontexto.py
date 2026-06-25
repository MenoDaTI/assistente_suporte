from ai_context_analyzer import AIContextAnalyzer

ia = AIContextAnalyzer()

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