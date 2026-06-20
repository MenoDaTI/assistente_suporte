from report_generator import ReportGenerator

gerador = ReportGenerator(
    sessao_id=13
)

print(
    gerador.gerar_relatorio()
)