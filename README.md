# interfaces-aegis-test

## Manifesto

Este repositório é a **fonte única da verdade** das interfaces do **Aegis Test**.

Tudo que define **como os sistemas conversam entre si** vive aqui.
Nada que define **como eles funcionam internamente** deve viver aqui.

Se um serviço publica, consome, integra ou depende de algo de outro serviço, **isso é uma interface** — e pertence a este repositório.

---

## O que são “interfaces” neste contexto

Interfaces não são código executável.
Interfaces são **acordos**.

Este repositório define:

* schemas de eventos
* topologia de mensageria (tópicos e subscriptions)
* contratos assíncronos baseados em eventos
* regras de versionamento

Ele existe para garantir que:

* produtores e consumidores evoluam de forma segura
* mudanças sejam explícitas
* integrações não quebrem silenciosamente

A comunicação no Aegis Test é **100% event-driven**: não há commands, apenas eventos que representam fatos imutáveis no domínio.

---

## Responsabilidade

Este repositório é responsável por:

* � **Eventos de domínio** (schemas JSON Schema)
* 🧵 **Tópicos e subscriptions** (definições YAML e AsyncAPI)
* 🔢 **Versionamento e compatibilidade**
* 📚 **Documentação visual da topologia** (AsyncAPI)

Este repositório **não é responsável** por:

* lógica de negócio
* regras de domínio
* validações de runtime
* código de infraestrutura
* helpers ou utilitários

---

## Estrutura

```
interfaces-aegis-test/
├── events/          # Eventos publicados no sistema (JSON Schema)
├── topics/          # Definições de tópicos e subscriptions (YAML)
├── wrappers/        # Wrappers de mensageria por linguagem
│   ├── java/        # Wrapper Java (obrigatório)
│   └── python/      # Wrapper Python
├── docs/            # Documentação e guidelines
├── asyncapi.yaml    # Especificação AsyncAPI 3.0 (visualizável)
└── README.md
```

A estrutura existe para **organizar responsabilidade**, não por estética.

Cada diretório tem um propósito claro:
- `events/` define **contratos de payload** (schemas JSON)
- `topics/` define **topologia de mensageria** (quem publica, quem consome)
- `asyncapi.yaml` documenta a topologia de forma **visual e interativa**
- `wrappers/` gera **código type-safe** para consumo nas aplicações

---

## Eventos

Eventos representam **algo que já aconteceu** no domínio.

Eles são fatos imutáveis que outros sistemas podem reagir, mas **não controlam**.

Exemplos:

* TestCreated
* TestFinished
* SpecificationRequested
* SpecificationCreated

Regras:

* eventos são imutáveis
* eventos são versionados
* eventos não são reaproveitados para outros significados

Exemplo de versionamento:

* `specification-created.v1.json`
* `specification-created.v2.json`

Nunca altere uma versão existente de forma incompatível.

---

## Comunicação: Puramente Event-Driven

O Aegis Test utiliza um modelo **100% event-driven**.

Todos os eventos fluem através de Google Cloud Pub/Sub:

```
portal                orchestrator           analytics
  |                       |                      |
  ├─> SpecificationRequested (event) ──────────>|
  |                       |
  |                       ├─> SpecificationCreated (event) ──────────>|
```

Não há **commands** (pedidos): apenas **eventos** que representam fatos no domínio.

Cada consumidor reage de forma independente aos eventos conforme sua lógica de negócio.

---

## Versionamento

Mudanças seguem estas regras:

### Compatível (permitido)

* adicionar campos opcionais
* adicionar novos eventos

### Incompatível (não permitido)

* remover campos
* renomear campos
* mudar significado sem criar nova versão

Mudanças incompatíveis **exigem nova versão**.

---

## Tópicos e Subscriptions

Tópicos e subscriptions fazem parte da **interface pública de integração**.

Eles documentam **como** os contratos trafegam no sistema.

A topologia de mensageria deve ser declarativa.

### Estrutura esperada

```
topics/
├── test-created.yaml
├── test-finished.yaml
└── agent-events.yaml
```

### Exemplo de definição de tópico

```yaml
name: test-created
description: Evento emitido quando um teste é criado
producedBy:
  - orchestrator
consumedBy:
  - agents
  - analytics
payload:
  event: TestCreatedEventV1
```

Regras:

* todo tópico deve ter dono
* todo consumidor deve estar explícito
* payload deve apontar para um contrato versionado

Nenhum tópico deve existir sem definição neste repositório.

Tópicos e subscriptions são tratados como **interfaces públicas**.

Eles documentam:

* quem publica
* quem consome
* finalidade
* payload esperado

Nenhum serviço deve criar tópicos “por fora” sem atualização aqui.

---

## Wrappers por linguagem

Os contratos definidos neste repositório **não são consumidos diretamente como objetos brutos** nas aplicações.

Cada linguagem **possui um wrapper**, garantindo tipagem, ergonomia e consistência.

### Wrappers disponíveis

* **Java** → `wrappers/java/` (obrigatório, linguagem de intersecção do sistema)
* **Python** → `wrappers/python/` (usando dataclasses imutáveis)

### Como usar

**Java:**
```java
import com.interfaces.aegis.test.messaging.Topics;

Destination dest = Topics.SPECIFICATION_REQUESTED;
publisher.publish(dest.getTopic(), message);
```

**Python:**
```python
from aegis_interfaces.messaging import Topics

dest = Topics.SPECIFICATION_REQUESTED
publisher.publish(dest.topic, message)
```

### Regras

* wrappers refletem fielmente os contratos definidos em `topics/`
* wrappers não contêm lógica de negócio
* nenhum código de aplicação deve usar strings literais para tópicos/subscriptions
* wrappers são imutáveis e thread-safe

Os schemas e definições de tópicos são o source of truth. 
Os wrappers são projeções type-safe desses contratos.

---

## AsyncAPI: Visualização Dinâmica

A topologia é documentada em **AsyncAPI 3.0** no arquivo `asyncapi.yaml`.

AsyncAPI permite visualizar dinamicamente:
- Todos os tópicos e eventos
- Fluxo de dados entre serviços
- Esquemas das mensagens
- Produtores e consumidores

### Ver a topologia visualmente

Você pode visualizar `asyncapi.yaml` usando ferramentas como:

* [AsyncAPI Studio](https://studio.asyncapi.com/) - arraste o arquivo ou cole a URL
* [Swagger Editor](https://editor.swagger.io/) - suporta AsyncAPI
* [Redoc](https://redoc.ly/) - gerador de documentação

**Exemplo: Copie a URL do arquivo `asyncapi.yaml` no GitHub e abra em:**
```
https://studio.asyncapi.com/?url=https://raw.githubusercontent.com/peguidotte/interface-aegis-test/main/asyncapi.yaml
```

---

## Regra de Ouro

> **Se mais de um sistema depende disso, isso é uma interface.**

Se for interface, pertence aqui.
Se não for, não pertence.

---

## Filosofia

Este repositório existe para:

* reduzir acoplamento
* tornar mudanças explícitas
* permitir evolução segura
* evitar contratos implícitos

Ele deve crescer **devagar**, com intenção clara.

Quando houver dúvida se algo deve entrar aqui, a resposta padrão é:

> **provavelmente não**.

---

## Nota final

Este repositório é um **contrato social** entre serviços.

Quebrá-lo sem cuidado quebra sistemas.
Respeitá-lo mantém o Aegis Test saudável e escalável.
