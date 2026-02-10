# Usage Examples

Exemplos práticos end-to-end mostrando como usar os wrappers em cenários reais.

---

## Cenário 1: Portal publica evento de requisição

### Java (Portal Service)

```java
package com.aegis.portal.service;

import com.google.cloud.pubsub.v1.Publisher;
import com.google.protobuf.ByteString;
import com.google.pubsub.v1.PubsubMessage;
import com.google.pubsub.v1.TopicName;
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.UUID;
import java.util.Map;

public class SpecificationPublisher {
    
    private final Publisher publisher;
    private final ObjectMapper objectMapper;
    private final String projectId;
    
    public void publishSpecificationRequestedEvent(
        String projectId,
        String description,
        String requestedBy
    ) {
        // 1. Get the destination (NEVER hardcode!)
        Destination destination = Topics.SPECIFICATION_REQUESTED;
        
        // 2. Build the payload according to SpecificationRequestedEventV1 schema
        Map<String, Object> event = Map.of(
            "eventId", UUID.randomUUID().toString(),
            "eventTimestamp", java.time.Instant.now().toString(),
            "specificationId", UUID.randomUUID().toString(),
            "projectId", projectId,
            "requestedBy", requestedBy,
            "description", description,
            "priority", "MEDIUM"
        );
        
        try {
            // 3. Serialize payload
            String json = objectMapper.writeValueAsString(event);
            ByteString data = ByteString.copyFromUtf8(json);
            
            // 4. Add metadata
            PubsubMessage message = PubsubMessage.newBuilder()
                .setData(data)
                .putAttributes("schema", destination.getSchema())
                .putAttributes("source", "portal")
                .build();
            
            // 5. Publish to the topic
            TopicName topicName = TopicName.of(this.projectId, destination.getTopic());
            Publisher publisher = Publisher.newBuilder(topicName).build();
            publisher.publish(message).get();
            
            System.out.println("Published to: " + destination.getTopic());
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to publish event", e);
        }
    }
}
```

---

## Cenário 2: Orchestrator consome evento e publica evento de conclusão

### Java (Orchestrator Service)

```java
package com.aegis.orchestrator.messaging;

import com.google.cloud.pubsub.v1.AckReplyConsumer;
import com.google.cloud.pubsub.v1.MessageReceiver;
import com.google.cloud.pubsub.v1.Subscriber;
import com.google.pubsub.v1.ProjectSubscriptionName;
import com.google.pubsub.v1.PubsubMessage;
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Map;

public class EventSubscriber {
    
    private final ObjectMapper objectMapper;
    private final String projectId;
    
    public void startListening() {
        // 1. Get the destination
        Destination destination = Topics.SPECIFICATION_REQUESTED;
        
        // 2. Get the subscription for this consumer (orchestrator)
        String subscriptionName = destination.getSubscription("orchestrator");
        
        // 3. Create subscriber
        ProjectSubscriptionName subscription = 
            ProjectSubscriptionName.of(projectId, subscriptionName);
        
        MessageReceiver receiver = new MessageReceiver() {
            @Override
            public void receiveMessage(PubsubMessage message, AckReplyConsumer consumer) {
                try {
                    // 4. Deserialize based on schema
                    String json = message.getData().toStringUtf8();
                    Map<String, Object> event = objectMapper.readValue(json, Map.class);
                    
                    // 5. Validate it's the expected type
                    String schema = message.getAttributesOrDefault("schema", "");
                    if (!destination.getSchema().equals(schema)) {
                        System.err.println("Schema mismatch: " + schema);
                        consumer.nack();
                        return;
                    }
                    
                    // 6. Process the event
                    handleSpecificationRequestedEvent(event);
                    
                    // 7. Acknowledge
                    consumer.ack();
                    
                } catch (Exception e) {
                    System.err.println("Error processing message: " + e.getMessage());
                    consumer.nack();
                }
            }
        };
        
        Subscriber subscriber = Subscriber.newBuilder(subscription, receiver).build();
        subscriber.startAsync().awaitRunning();
        
        System.out.println("Listening on: " + subscriptionName);
    }
    
    private void handleSpecificationRequestedEvent(Map<String, Object> event) {
        String specificationId = (String) event.get("specificationId");
        String projectId = (String) event.get("projectId");
        
        System.out.println("Processing specification request: " + specificationId);
        
        // Business logic here...
        // After processing, emit SpecificationCreated event
        publishSpecificationCreatedEvent(specificationId, projectId);
    }
    
    private void publishSpecificationCreatedEvent(String specificationId, String projectId) {
        // Use Topics.SPECIFICATION_CREATED to publish the completion event
        // (similar to Scenario 1)
    }
}
```

---

## Cenário 3: Portal (Python) consome evento de conclusão

### Python (Portal/Analytics Service)

```python
from google.cloud import pubsub_v1
from aegis_interfaces.messaging import Topics
import json
from typing import Callable

class EventSubscriber:
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.subscriber = pubsub_v1.SubscriberClient()
    
    def start_listening(self):
        # 1. Get the destination
        destination = Topics.SPECIFICATION_CREATED
        
        # 2. Get the subscription for portal consumer
        subscription_name = destination.get_subscription("portal")
        
        # 3. Build full subscription path
        subscription_path = self.subscriber.subscription_path(
            self.project_id, 
            subscription_name
        )
        
        # 4. Define callback
        def callback(message: pubsub_v1.subscriber.message.Message) -> None:
            try:
                # 5. Deserialize payload
                payload = json.loads(message.data.decode('utf-8'))
                
                # 6. Validate schema
                schema = message.attributes.get('schema', '')
                if schema != destination.schema:
                    print(f"Schema mismatch: {schema}")
                    message.nack()
                    return
                
                # 7. Process event
                self.handle_specification_created(payload)
                
                # 8. Acknowledge
                message.ack()
                
            except Exception as e:
                print(f"Error processing message: {e}")
                message.nack()
        
        # 9. Subscribe
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path, 
            callback=callback
        )
        
        print(f"Listening on: {subscription_name}")
        
        # Keep listening
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
    
    def handle_specification_created(self, event: dict) -> None:
        specification_id = event['specificationId']
        status = event['status']
        
        print(f"Received: Specification {specification_id} created with status {status}")
        
        # Business logic here (update UI, send notification, etc)
```

---

## Anti-patterns (NUNCA faça)

### ❌ Hardcoding topic names

```java
// ERRADO!
String topic = "aegis-test.specification.created";
publisher.publish(TopicName.of(projectId, topic), message);
```

### ❌ Hardcoding subscription names

```python
# ERRADO!
subscription_name = "orchestrator.aegis-test.specification.created"
subscriber.subscribe(subscription_path, callback)
```

### ❌ String comparisons for routing

```java
// ERRADO!
if (topicName.equals("aegis-test.specification.created")) {
    // ...
}
```

### ❌ Using commands

```java
// ERRADO! Aegis Test é 100% event-driven
// Não há commands, apenas eventos de requisição
Topics.SPECIFICATION_CREATE_COMMAND  // ❌ NUNCA
Topics.SPECIFICATION_REQUESTED       // ✅ Sempre
```

---

## Best practices

### ✅ Always use wrapper

```java
Destination dest = Topics.SPECIFICATION_CREATE_REQUESTED;
String topic = dest.getTopic();
```

### ✅ Validate schema on receive

```python
schema = message.attributes.get('schema')
if schema != destination.schema:
    message.nack()
    return
```

### ✅ Add metadata to messages

```java
PubsubMessage.newBuilder()
    .setData(data)
    .putAttributes("schema", destination.getSchema())
    .putAttributes("source", "portal")
    .putAttributes("correlationId", requestId)
    .build();
```

---

## Testing

### Java Unit Test

```java
@Test
void shouldGetCorrectTopicName() {
    Destination dest = Topics.SPECIFICATION_REQUESTED;
    
    assertEquals("specification-requested", dest.getName());
    assertEquals("aegis-test.specification.requested", dest.getTopic());
    assertEquals("SpecificationRequestedEventV1", dest.getSchema());
}

@Test
void shouldGetSubscriptionForOrchestrator() {
    Destination dest = Topics.SPECIFICATION_REQUESTED;
    
    String subscription = dest.getSubscription("orchestrator");
    
    assertEquals(
        "orchestrator.aegis-test.specification.requested", 
        subscription
    );
}

@Test
void shouldThrowForUnknownConsumer() {
    Destination dest = Topics.SPECIFICATION_REQUESTED;
    
    assertThrows(IllegalArgumentException.class, () -> {
        dest.getSubscription("unknown-service");
    });
}
```

### Python Unit Test

```python
def test_topic_name():
    dest = Topics.SPECIFICATION_REQUESTED
    
    assert dest.name == "specification-requested"
    assert dest.topic == "aegis-test.specification.requested"
    assert dest.schema == "SpecificationRequestedEventV1"

def test_subscription_for_orchestrator():
    dest = Topics.SPECIFICATION_REQUESTED
    
    subscription = dest.get_subscription("orchestrator")
    
    assert subscription == "orchestrator.aegis-test.specification.requested"

def test_unknown_consumer_raises_error():
    dest = Topics.SPECIFICATION_REQUESTED
    
    with pytest.raises(KeyError):
        dest.get_subscription("unknown-service")
```
