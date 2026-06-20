# Banco de Dados - Assistente de Suporte

## Visão Geral

O banco de dados do Assistente de Suporte utiliza SQLite e tem como objetivo armazenar todas as informações coletadas durante os atendimentos técnicos, permitindo posterior análise, geração de relatórios, construção de base de conhecimento e integração com sistemas externos.

---

# Tabela: sessoes

## Objetivo

Armazenar os dados principais de cada atendimento ou sessão de resolução iniciada pelo analista.

Cada sessão representa um chamado ou atividade específica.

## Campos

| Campo     | Tipo     | Descrição                          |
| --------- | -------- | ---------------------------------- |
| id        | INTEGER  | Identificador único da sessão      |
| protocolo | TEXT     | Número do protocolo do atendimento |
| cliente   | TEXT     | Nome do cliente                    |
| descricao | TEXT     | Descrição resumida do problema     |
| inicio    | DATETIME | Data e hora de início              |
| fim       | DATETIME | Data e hora de encerramento        |
| status    | TEXT     | Situação da sessão                 |

## Relacionamentos

* 1:N com eventos
* 1:N com capturas_contexto
* 1:N com navegacao
* 1:N com evidencias_ocr
* 1:N com entidades

## Exemplo

```json
{
  "id": 1,
  "protocolo": "20260620001",
  "cliente": "Grupo Carbel",
  "descricao": "Ramal não registra",
  "inicio": "2026-06-20 09:10:00",
  "fim": "2026-06-20 09:25:00",
  "status": "FINALIZADA"
}
```

---

# Tabela: eventos

## Objetivo

Registrar alterações de contexto durante o atendimento.

Normalmente representa troca de janela ou mudança de aplicação utilizada.

## Campos

| Campo            | Tipo     | Descrição                        |
| ---------------- | -------- | -------------------------------- |
| id               | INTEGER  | Identificador único              |
| sessao_id        | INTEGER  | Sessão relacionada               |
| data_hora        | DATETIME | Momento do evento                |
| janela           | TEXT     | Nome da janela                   |
| aplicativo       | TEXT     | Processo executado               |
| titulo_janela    | TEXT     | Título completo da janela        |
| observacao       | TEXT     | Informação adicional             |
| duracao_segundos | INTEGER  | Tempo gasto até o próximo evento |

## Relacionamentos

* N:1 com sessoes

## Exemplo

```json
{
  "id": 25,
  "sessao_id": 1,
  "data_hora": "2026-06-20 09:15:00",
  "janela": "PuTTY",
  "aplicativo": "putty.exe",
  "titulo_janela": "172.16.11.77 - PuTTY",
  "observacao": null,
  "duracao_segundos": 180
}
```

---

# Tabela: capturas_contexto

## Objetivo

Armazenar informações adicionais coletadas durante o monitoramento.

Permite registrar dados estruturados identificados durante a sessão.

## Campos

| Campo     | Tipo     | Descrição              |
| --------- | -------- | ---------------------- |
| id        | INTEGER  | Identificador          |
| sessao_id | INTEGER  | Sessão relacionada     |
| evento_id | INTEGER  | Evento associado       |
| data_hora | DATETIME | Data e hora da captura |
| tipo      | TEXT     | Tipo da informação     |
| origem    | TEXT     | Origem da captura      |
| chave     | TEXT     | Nome da informação     |
| valor     | TEXT     | Valor identificado     |

## Relacionamentos

* N:1 com sessoes
* N:1 com eventos

## Exemplo

```json
{
  "id": 10,
  "sessao_id": 1,
  "evento_id": 25,
  "tipo": "SERVIDOR",
  "origem": "PUTTY",
  "chave": "IP",
  "valor": "172.16.11.77"
}
```

---

# Tabela: navegacao

## Objetivo

Registrar páginas consultadas durante o atendimento.

Utilizada para identificar pesquisas, consultas na Wiki, Omnia, VsPhone e outras ferramentas.

## Campos

| Campo     | Tipo     | Descrição                |
| --------- | -------- | ------------------------ |
| id        | INTEGER  | Identificador            |
| sessao_id | INTEGER  | Sessão relacionada       |
| data_hora | DATETIME | Data e hora              |
| navegador | TEXT     | Navegador utilizado      |
| titulo    | TEXT     | Título da aba            |
| categoria | TEXT     | Classificação automática |
| url       | TEXT     | URL capturada            |

## Relacionamentos

* N:1 com sessoes

## Exemplo

```json
{
  "id": 8,
  "sessao_id": 1,
  "data_hora": "2026-06-20 09:12:00",
  "navegador": "chrome.exe",
  "titulo": "Wiki Virtual Sistemas - Configuração SIP",
  "categoria": "WIKI",
  "url": null
}
```

---

# Tabela: evidencias_ocr

## Objetivo

Armazenar textos extraídos pelo OCR das aplicações monitoradas.

Permite reconstruir ações executadas pelo analista.

## Campos

| Campo          | Tipo     | Descrição                   |
| -------------- | -------- | --------------------------- |
| id             | INTEGER  | Identificador               |
| sessao_id      | INTEGER  | Sessão relacionada          |
| data_hora      | DATETIME | Data e hora                 |
| origem         | TEXT     | Aplicação monitorada        |
| texto_extraido | TEXT     | Conteúdo capturado pelo OCR |

## Relacionamentos

* N:1 com sessoes

## Exemplo

```json
{
  "id": 3,
  "sessao_id": 1,
  "data_hora": "2026-06-20 09:17:00",
  "origem": "putty.exe",
  "texto_extraido": "sip show peers\ncore reload"
}
```

---

# Tabela: entidades

## Objetivo

Armazenar entidades identificadas automaticamente a partir do OCR e demais fontes.

Serve como base para geração de relatórios inteligentes.

## Campos

| Campo     | Tipo     | Descrição          |
| --------- | -------- | ------------------ |
| id        | INTEGER  | Identificador      |
| sessao_id | INTEGER  | Sessão relacionada |
| data_hora | DATETIME | Data e hora        |
| tipo      | TEXT     | Tipo da entidade   |
| valor     | TEXT     | Valor identificado |

## Tipos atualmente suportados

* IP
* RAMAL
* COMANDO

## Relacionamentos

* N:1 com sessoes

## Exemplo

```json
{
  "id": 12,
  "sessao_id": 1,
  "data_hora": "2026-06-20 09:18:00",
  "tipo": "COMANDO",
  "valor": "core reload"
}
```

---

# Diagrama de Relacionamento

sessoes
├── eventos
├── capturas_contexto
├── navegacao
├── evidencias_ocr
└── entidades

Todas as tabelas operacionais possuem relacionamento direto com a tabela principal de sessões.
