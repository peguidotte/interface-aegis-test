# Aegis Test Interfaces - Java

Java wrapper for Aegis Test messaging interfaces.

## Building

```bash
mvn clean install
```

## Usage

### Adding Dependency

Add to your `pom.xml`:

```xml
<dependency>
    <groupId>com.interfaces.aegis.test</groupId>
    <artifactId>aegis-test-interfaces-java</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Accessing Topics

```java
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;

// Get a command destination
Destination dest = Topics.SPECIFICATION_CREATE_REQUESTED;

// Access topic and subscription
String topic = dest.getTopic();              // "aegis-test.specification.create.requested"
String subscription = dest.getSubscription(); // "orchestrator.aegis-test..."
```

### Multiple Consumers

```java
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;

// Get an event destination with multiple consumers
Destination dest = Topics.SPECIFICATION_CREATED;

// Access specific consumer subscriptions
String analyticsSub = dest.getSubscription("analytics");
String notificationsSub = dest.getSubscription("notifications");
```

### Publishing Messages

```java
import com.google.cloud.pubsub.v1.Publisher;
import com.google.pubsub.v1.TopicName;
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;

Destination dest = Topics.SPECIFICATION_CREATE_REQUESTED;
TopicName topicName = TopicName.of(projectId, dest.getTopic());

Publisher publisher = Publisher.newBuilder(topicName).build();
publisher.publish(message);
```

### Subscribing to Messages

```java
import com.google.cloud.pubsub.v1.Subscriber;
import com.google.pubsub.v1.SubscriptionName;
import com.interfaces.aegis.test.messaging.Destination;
import com.interfaces.aegis.test.messaging.Topics;

Destination dest = Topics.SPECIFICATION_CREATED;
SubscriptionName subscription = SubscriptionName.of(
    projectId, 
    dest.getSubscription("analytics")
);

Subscriber subscriber = Subscriber.newBuilder(subscription, receiver).build();
subscriber.startAsync().awaitRunning();
```

## Design Principles

- **No hardcoded strings**: All topic and subscription names are defined once
- **Type safety**: Full IDE autocomplete and compile-time validation
- **Immutability**: All destinations are immutable value objects
- **Single source of truth**: This library is the contract between all services

## Architecture

### Package Structure

```
com.interfaces.aegis.test
├── messaging/              # Core interfaces and registry
│   ├── Destination.java   # Destination abstraction
│   └── Topics.java        # Central registry
└── topics/                # Domain-specific destinations
    └── specification/
        ├── SpecificationCreateRequested.java
        └── SpecificationCreated.java
```

### Adding New Topics

1. Create a new class implementing `Destination`
2. Add it to the appropriate domain package under `topics/`
3. Register it as a constant in `Topics.java`

## Requirements

- Java 17 or higher
- No external runtime dependencies (standalone wrapper)
