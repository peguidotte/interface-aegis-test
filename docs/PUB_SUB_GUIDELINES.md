# Pub/Sub Guidelines

## Objetivo

Este guideline define **como tópicos e subscriptions devem ser nomeados, declarados e utilizados** no ecossistema **Aegis Test**.

O objetivo é:

* evitar nomes inconsistentes
* evitar hardcode espalhado
* tornar a topologia de mensageria legível
* garantir rastreabilidade entre produtores e consumidores

Pub/Sub é tratado como **interface pública**, não como detalhe de implementação.

---

## Princípio fundamental

> **Nunca hardcode nomes de tópicos ou subscriptions no código de negócio.**

Todo nome deve:

* existir neste repositório
* possuir um identificador semântico
* apontar claramente para seu produtor e consumidores

---

## Centralização obrigatória

Cada linguagem deve possuir um **wrapper centralizado de destinos de mensageria**, gerado ou mantido a partir das definições deste repositório.

Exemplo conceitual (Python):

* um único módulo
* classes imutáveis
* acesso por constante semântica

Isso garante:

* refactor seguro
* autocomplete
* consistência global

---

## Estrutura de definição

Cada destino de mensageria representa **um contrato completo**:

* nome semântico
* tópico Pub/Sub
* subscription Pub/Sub

Um destino não é apenas um tópico. Ele representa **uma intenção de comunicação**.

---

## Naming convention — Tópicos

Formato padrão:

```
<produto>.<dominio>.<contexto>.<acao>.<estado>
```

Exemplo:

```
aegis-test.test-generation.planning.started
aegis-test.test-generation.planning.completed
aegis-test.test-generation.planning.failed
```

Regras:

* sempre lowercase
* separado por ponto (`.`)
* sem abreviações obscuras
* nomes devem ser legíveis por humanos

---

## Naming convention — Subscriptions

Formato padrão:

```
<consumidor>.<topic>
```

Exemplo:

```
orchestrator.aegis-test.test-generation.planning.started
test-planner.aegis-test.test-generation.requested
```

Regras:

* consumidor explícito
* uma subscription por consumidor
* nunca reutilizar subscription entre serviços diferentes

---

## Agrupamento lógico

Os destinos devem ser organizados por **domínio funcional**, não por serviço.

Exemplo:

* TEST GENERATION
* TEST PLANNING
* AGENT EXECUTION

Isso facilita leitura e evolução.

---

## Relação com eventos e commands

Todo tópico deve apontar explicitamente para **qual contrato trafega nele**:

* Event (algo que aconteceu)
* Command (intenção)

Nenhum tópico deve transportar múltiplos tipos não relacionados.

---

## Fonte da verdade

Este repositório define:

* quais tópicos existem
* quem publica
* quem consome
* qual contrato trafega

Código de aplicação **apenas referencia**.

Infra apenas **provisiona**.

---

## Evolução

Mudanças seguem estas regras:

### Permitido

* criar novos tópicos
* adicionar novos consumidores (nova subscription)

### Não permitido

* renomear tópicos existentes
* reutilizar tópico para outro significado

Mudanças semânticas exigem **novo tópico**.

---

## Regra final

> **Se não está documentado aqui, não existe.**

Qualquer exceção cria dívida técnica explícita.

Este guideline existe para manter o Pub/Sub previsível, auditável e escalável.
