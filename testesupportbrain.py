from support_brain import SupportBrain

brain = SupportBrain(
    sessao_id=17
)

resultado = brain.analisar_sessao()

print(resultado)