# Estrutura do Projeto - Assistente de Suporte

## Visão Geral

O projeto Assistente de Suporte é composto por módulos independentes responsáveis pela captura de atividades, coleta de contexto, processamento de informações e geração automática de documentação técnica.

A estrutura foi organizada para permitir escalabilidade futura, incluindo integração com VS Omnia, geração automática de Wiki e motores de Inteligência Artificial.

---

# Árvore de Diretórios

```text
assistente_suporte/

├── main.py
├── gui.py
├── database.py
├── session_manager.py
├── activity_monitor.py
├── window_monitor.py
├── browser_monitor.py
├── ocr_monitor.py
├── entity_extractor.py
├── flow_analyzer.py
├── session_summary.py
├── report_generator.py
├── suporte.db
│
├── docs/
│   ├── arquitetura.md
│   ├── roadmap.md
│   ├── banco_de_dados.md
│   └── instalacao.md
│
└── logs/
```

---

# Arquivos Principais

## main.py

### Objetivo

Ponto de entrada da aplicação.

### Responsabilidades

* Inicializar o sistema
* Criar tabelas do banco de dados
* Registrar atalhos globais
* Inicializar monitores
* Iniciar interface gráfica

### Dependências

* database.py
* session_manager.py
* activity_monitor.py
* gui.py

---

## gui.py

### Objetivo

Interface gráfica do sistema.

### Responsabilidades

* Exibir status da sessão
* Exibir estatísticas
* Permitir iniciar e finalizar atendimentos
* Mostrar indicadores operacionais

### Tecnologias

* Tkinter

---

## database.py

### Objetivo

Camada de acesso ao banco de dados.

### Responsabilidades

* Conexão SQLite
* Criação das tabelas
* Inserções
* Atualizações
* Consultas

### Tabelas Gerenciadas

* sessoes
* eventos
* capturas_contexto
* navegacao
* evidencias_ocr
* entidades

---

## session_manager.py

### Objetivo

Gerenciar o ciclo de vida das sessões.

### Responsabilidades

* Iniciar sessão
* Encerrar sessão
* Controlar sessão ativa
* Registrar eventos associados

### Entidade Principal

Sessão de Atendimento

---

## activity_monitor.py

### Objetivo

Monitorar continuamente a atividade do usuário.

### Responsabilidades

* Detectar troca de janelas
* Registrar eventos
* Calcular tempo de permanência
* Acionar capturas complementares

### Frequência

Monitoramento contínuo em background.

---

## window_monitor.py

### Objetivo

Capturar informações da janela atualmente em foco.

### Responsabilidades

* Obter título da janela
* Identificar processo ativo
* Identificar aplicação utilizada

### Tecnologias

* Win32 API
* psutil

---

## browser_monitor.py

### Objetivo

Monitorar navegação durante o atendimento.

### Responsabilidades

* Detectar navegadores suportados
* Classificar páginas acessadas
* Categorizar consultas

### Categorias Atuais

* OMNIA
* WIKI
* VSPHONE
* CHATGPT
* DOCUMENTACAO
* OUTRO

### Navegadores Suportados

* Google Chrome
* Opera GX
* Firefox
* Microsoft Edge

---

## ocr_monitor.py

### Objetivo

Capturar informações textuais de aplicações técnicas.

### Responsabilidades

* Captura de tela
* Execução OCR
* Registro de evidências

### Aplicações Monitoradas

* PuTTY
* CMD
* PowerShell
* AnyDesk
* MicroSIP

### Tecnologias

* EasyOCR
* MSS

---

## entity_extractor.py

### Objetivo

Extrair entidades relevantes dos textos capturados.

### Responsabilidades

* Identificação de IPs
* Identificação de ramais
* Identificação de comandos

### Tipos Suportados

* IP
* RAMAL
* COMANDO

---

## flow_analyzer.py

### Objetivo

Interpretar o fluxo do atendimento.

### Responsabilidades

* Classificar tipos de suporte
* Detectar padrões operacionais
* Preparar informações para IA

### Fluxos Atuais

* SUPORTE_VOIP
* SUPORTE_REMOTO
* GERAL

---

## session_summary.py

### Objetivo

Consolidar todas as informações da sessão.

### Responsabilidades

* Carregar dados relacionados
* Agrupar eventos
* Agrupar entidades
* Agrupar evidências

### Saída

Estrutura única em formato de objeto Python.

---

## report_generator.py

### Objetivo

Gerar documentação automática dos atendimentos.

### Responsabilidades

* Criar relatórios estruturados
* Organizar cronologia
* Consolidar informações técnicas

### Futuras Evoluções

* Narrative Generator
* Relatórios inteligentes
* Integração com IA

---

## suporte.db

### Objetivo

Banco de dados SQLite principal do sistema.

### Conteúdo

* Sessões
* Eventos
* Navegação
* OCR
* Entidades
* Contexto

---

# Diretório docs/

## Objetivo

Centralizar toda a documentação do projeto.

---

### arquitetura.md

Documentação técnica da arquitetura geral.

---

### roadmap.md

Planejamento e evolução das fases do projeto.

---

### banco_de_dados.md

Documentação completa das tabelas e relacionamentos.

---

### instalacao.md

Procedimentos de instalação e configuração.

---

# Diretório logs/

## Objetivo

Armazenar registros operacionais do sistema.

### Conteúdo Futuro

* Logs de execução
* Logs de erro
* Logs de OCR
* Logs de integração

---

# Fluxo Operacional

```text
main.py
    ↓
session_manager.py
    ↓
activity_monitor.py
    ↓
window_monitor.py
    ↓
browser_monitor.py
    ↓
ocr_monitor.py
    ↓
entity_extractor.py
    ↓
flow_analyzer.py
    ↓
session_summary.py
    ↓
report_generator.py
```

---

# Estado Atual do Projeto

Fase 1 - Captura de Atividades
Status: Concluída

Fase 2 - Captura de Contexto
Status: Concluída

Fase 3 - Motor de Inteligência
Status: Em Desenvolvimento

Fase 4 - Integração VS Omnia
Status: Planejada

Fase 5 - Wiki Automática
Status: Planejada

Fase 6 - IA Analista de Suporte
Status: Planejada
