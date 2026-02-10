# Getting Started

Este guia mostra como começar a usar o `interfaces-aegis-test` nas suas aplicações.

---

## Para desenvolvedores Java (Orchestrator)

### 1. Adicionar dependência

No `pom.xml` do seu projeto:

```xml
<dependency>
    <groupId>com.interfaces.aegis.test</groupId>
    <artifactId>aegis-test-interfaces-java</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 2. Importar e usar

```java
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;

public class SpecificationService {
    
    public void publishSpecificationCreatedEvent(String specificationId) {
        // Nunca use strings literais!
        // ❌ String topic = "aegis-test.specification.created";
        
        // ✅ Use o wrapper
        Destination dest = Topics.SPECIFICATION_CREATED;
        
        // Publique usando o destino tipado
        publisher.publish(dest.getTopic(), buildEvent(specificationId));
    }
    
    public void subscribeToRequests() {
        Destination dest = Topics.SPECIFICATION_REQUESTED;
        
        // Obtenha a subscription para o orchestrator
        String subscription = dest.getSubscription();
        subscriber.subscribe(subscription, this::handleRequest);
    }
}
```

---

## Para desenvolvedores Python (Agents)

### 1. Instalar pacote

```bash
cd wrappers/python
pip install -e .
```

### 2. Importar e usar

```python
from aegis_interfaces.messaging import Topics

class SpecificationHandler:
    
    def publish_event(self, specification_id: str):
        # Nunca use strings literais!
        # ❌ topic = "aegis-test.specification.created"
        
        # ✅ Use o wrapper
        dest = Topics.SPECIFICATION_CREATED
        
        # Publique usando o destino tipado
        self.publisher.publish(dest.topic, self.build_event(specification_id))
    
    def subscribe_to_requests(self):
        dest = Topics.SPECIFICATION_REQUESTED
        
        # Obtenha a subscription
        subscription = dest.subscription  # ou dest.get_subscription("orchestrator")
        self.subscriber.subscribe(subscription, self.handle_request)
```

---

## Princípios fundamentais

### ❌ Nunca faça isso

```java
// ERRADO: hardcoded strings
String topic = "aegis-test.specification.created";
String subscription = "orchestrator.aegis-test.specification.created";
```

```python
# ERRADO: hardcoded strings
topic = "aegis-test.specification.created"
subscription = "orchestrator.aegis-test.specification.created"
```

### ✅ Sempre faça isso

```java
// CORRETO: usando wrapper tipado
Destination dest = Topics.SPECIFICATION_CREATED;
String topic = dest.getTopic();
String subscription = dest.getSubscription();
```

```python
# CORRETO: usando wrapper tipado
dest = Topics.SPECIFICATION_CREATED
topic = dest.topic
subscription = dest.subscription
```

---

## Visualizar a topologia

Para ver todos os eventos e fluxos de forma visual e interativa:

1. Abra [AsyncAPI Studio](https://studio.asyncapi.com/)
2. Selecione "Open URL" e cole:
   ```
   https://raw.githubusercontent.com/peguidotte/interface-aegis-test/main/asyncapi.yaml
   ```
3. Visualize a topologia completa, fluxos e esquemas

Isso torna fácil entender como os serviços se comunicam sem ler código.

---

## Benefícios

### Type safety
O IDE autocompleta e valida em tempo de compilação/desenvolvimento.

### Refactoring seguro
Se um tópico mudar de nome, o compilador/type checker avisa todos os usos.

### Documentação viva
A lista de tópicos em `Topics.java` ou `Topics.py` é a documentação canônica.

### Auditabilidade
É trivial encontrar quem publica e quem consome cada tópico.

---

## Próximos passos

- Consulte [PUB_SUB_GUIDELINES.md](./PUB_SUB_GUIDELINES.md) para naming conventions
- Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para adicionar novos tópicos
- Explore os schemas em `events/` e `commands/` para entender os contratos
