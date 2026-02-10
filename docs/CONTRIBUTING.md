# Contributing

Como adicionar novos tópicos, eventos e comandos ao `interfaces-aegis-test`.

---

## Fluxo geral

1. Definir o **contrato** (event ou command)
2. Definir o **tópico** (topologia de mensageria)
3. Atualizar os **wrappers** (Java e Python)
4. Submeter PR para revisão

---

## 1. Definir o contrato

### Para um novo evento

Criar arquivo em `events/`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://interfaces.aegis-test.com/events/test-finished.v1.json",
  "title": "TestFinishedEventV1",
  "description": "Event emitted when a test execution is completed",
  "type": "object",
  "required": [
    "eventId",
    "eventTimestamp",
    "testId",
    "status"
  ],
  "properties": {
    "eventId": {
      "type": "string",
      "format": "uuid"
    },
    "eventTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "testId": {
      "type": "string",
      "format": "uuid"
    },
    "status": {
      "type": "string",
      "enum": ["PASSED", "FAILED", "SKIPPED"]
    }
  },
  "additionalProperties": false
}
```

Todos os eventos no Aegis Test representam **fatos que aconteceram**.
Nenhum comando será aceito - apenas eventos.

---

## 2. Definir o tópico

Criar arquivo em `topics/`:

```yaml
# Test Finished Event Topic

name: test-finished
topic: aegis-test.test-execution.finished

description: |
  Event published when a test execution completes.
  Contains final status and execution metadata.

producedBy:
  - test-runner

consumedBy:
  - portal

subscriptions:
  portal: portal.aegis-test.test-execution.finished

payload:
  type: event
  schema: TestFinishedEventV1
  schemaPath: events/test-finished.v1.json

deliveryGuarantees:
  - at-least-once

version: 1.0.0
```

---

## 3. Atualizar os wrappers

### Java

**3.1. Criar classe de destino**

Em `wrappers/java/src/main/java/com/interfaces/aegis/test/topics/<dominio>/`:

```java
package com.interfaces.aegis.test.topics.testexecution;

import com.interfaces.aegis.test.messaging.Destination;
import java.util.Map;
import java.util.Objects;

public final class TestFinished implements Destination {
    
    private static final String NAME = "test-finished";
    private static final String TOPIC = "aegis-test.test-execution.finished";
    private static final String SCHEMA = "TestFinishedEventV1";
    private static final String DEFAULT_CONSUMER = "portal";
    
    private static final Map<String, String> SUBSCRIPTIONS = Map.of(
        "portal", "portal.aegis-test.test-execution.finished"
    );
    
    @Override
    public String getName() { return NAME; }
    
    @Override
    public String getTopic() { return TOPIC; }
    
    @Override
    public String getSubscription(String consumer) {
        Objects.requireNonNull(consumer);
        String subscription = SUBSCRIPTIONS.get(consumer);
        if (subscription == null) {
            throw new IllegalArgumentException("Unknown consumer: " + consumer);
        }
        return subscription;
    }
    
    @Override
    public String getSubscription() {
        return getSubscription(DEFAULT_CONSUMER);
    }
    
    @Override
    public String getSchema() { return SCHEMA; }
}
```

**3.2. Registrar em Topics.java**

```java
public final class Topics {
    
    // ... existing topics ...
    
    public static final Destination TEST_FINISHED = 
        new TestFinished();
}
```

### Python

**3.1. Adicionar em topics.py**

```python
class Topics:
    
    # ... existing topics ...
    
    TEST_FINISHED = Destination(
        name="test-finished",
        topic="aegis-test.test-execution.finished",
        subscriptions={
            "portal": "portal.aegis-test.test-execution.finished",
        },
        event_type=EventType.TEST_FINISHED,
        schema="TestFinishedEventV1",
        default_consumer="portal",
    )
    """Event published when test execution completes."""
```

**3.2. Adicionar o tipo de evento em destination.py**

```python
class EventType(Enum):
    # ... existing types ...
    TEST_FINISHED = "test.finished"
```

---

## 4. Checklist antes de submeter

- [ ] Evento (event) criado em JSON Schema
- [ ] Tópico definido em YAML
- [ ] Wrapper Java atualizado (nova classe + registry)
- [ ] Wrapper Python atualizado (topics.py + destination.py para new EventType)
- [ ] AsyncAPI atualizado (novo channel + message)
- [ ] Naming convention seguida (veja `PUB_SUB_GUIDELINES.md`)
- [ ] Subscriptions mapeadas para todos os consumidores

---

## Regras importantes

### Modelo Event-Driven

No Aegis Test, **tudo é um evento** que representa algo que **já aconteceu**.

Nunca adicione um comando. Se precisar de uma "intenção", isso é um evento de requisição.

### Versionamento

- Novos campos opcionais: compatível, adicione à mesma versão
- Campos removidos/renomeados: incompatível, crie nova versão (v2)

### Naming

Siga rigorosamente:
- Tópicos: `<produto>.<dominio>.<recurso>.<acao>`
- Subscriptions: `<consumidor>.<topic>`

Exemplo:
- Topic: `aegis-test.specification.requested` (evento de requisição, não comando)
- Subscription: `orchestrator.aegis-test.specification.requested`

Evite:
- `...create.requested` → use `...requested`
- `...execute.requested` → use `...requested`

### Responsabilidades

Este repositório define **contratos e topologia**, não **implementação**.

Nunca adicione:
- Lógica de negócio
- Código de infraestrutura (Terraform, etc.)
- Helpers ou utilitários
- Validações de runtime além do schema

### AsyncAPI

Após criar novos eventos/tópicos, atualize `asyncapi.yaml` para que a documentação visual permaneça sincronizada.

---

## Dúvidas?

Abra uma issue ou consulte a equipe de arquitetura.
