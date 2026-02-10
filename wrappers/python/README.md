# Aegis Test Interfaces - Python

Python wrapper for Aegis Test messaging interfaces.

## Installation

```bash
pip install -e .
```

## Usage

### Accessing Topics

```python
from aegis_interfaces.messaging import Topics

# Get a command destination
dest = Topics.SPECIFICATION_CREATE_REQUESTED

# Access topic and subscription
print(dest.topic)         # "aegis-test.specification.create.requested"
print(dest.subscription)  # "orchestrator.aegis-test.specification.create.requested"
```

### Multiple Consumers

```python
from aegis_interfaces.messaging import Topics

# Get an event destination with multiple consumers
dest = Topics.SPECIFICATION_CREATED

# Access specific consumer subscription
analytics_sub = dest.get_subscription("analytics")
notifications_sub = dest.get_subscription("notifications")
```

### Publishing Messages

```python
from aegis_interfaces.messaging import Topics
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
dest = Topics.SPECIFICATION_CREATE_REQUESTED

# Publish using the destination
publisher.publish(dest.topic, data=message_bytes)
```

### Subscribing to Messages

```python
from aegis_interfaces.messaging import Topics
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
dest = Topics.SPECIFICATION_CREATED

# Subscribe to specific consumer
subscription_path = f"projects/{project_id}/subscriptions/{dest.get_subscription('analytics')}"
subscriber.subscribe(subscription_path, callback=process_message)
```

## Design Principles

- **No hardcoded strings**: All topic and subscription names are defined once
- **Type safety**: IDEs can autocomplete and validate usage
- **Immutability**: All destinations are frozen dataclasses
- **Single source of truth**: This library is the contract between all services

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run type checking
mypy aegis_interfaces/
```
