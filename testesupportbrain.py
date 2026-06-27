"""Executa um teste manual do SupportBrain para uma sessao existente."""

from support_brain import SupportBrain

# Teste manual para reprocessar uma sessao ja gravada no banco.
brain = SupportBrain(
    sessao_id=19
)

resultado = brain.analisar_sessao()

print(resultado)
