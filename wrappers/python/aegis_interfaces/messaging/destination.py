"""
Destination abstraction for Pub/Sub messaging.

A Destination represents a complete messaging endpoint including:
- Topic name (where messages are published)
- Subscription mappings (where messages are consumed from)
- Semantic metadata (name, schema, event type)

All destinations are immutable and thread-safe.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class EventType(Enum):
    """Type of event carried by a messaging destination."""
    
    # Events from domain topics
    SPECIFICATIONCREATEDEVENTV1 = "aegis-test.specification.created"
    SPECIFICATIONREQUESTEDEVENTV1 = "aegis-test.specification.requested"


@dataclass(frozen=True)
class Destination:
    """
    Immutable representation of an event-driven Pub/Sub messaging destination.
    
    Attributes:
        name: Semantic name in kebab-case (e.g., "specification-created")
        topic: Full Pub/Sub topic name (e.g., "aegis-test.specification.created")
        subscriptions: Mapping of consumer name to subscription name
        event_type: Type of event
        schema: Schema identifier (e.g., "SpecificationCreatedEventV1")
        default_consumer: Optional default consumer for single-consumer topics
    """
    
    name: str
    topic: str
    subscriptions: Dict[str, str]
    event_type: EventType
    schema: str
    default_consumer: Optional[str] = None
    
    def get_subscription(self, consumer: str) -> str:
        """
        Get the subscription name for a specific consumer.
        
        Args:
            consumer: Name of the consuming service
            
        Returns:
            Full subscription name
            
        Raises:
            KeyError: If the consumer is not registered for this topic
        """
        if consumer not in self.subscriptions:
            raise KeyError(
                f"Unknown consumer '{consumer}' for topic '{self.name}'. "
                f"Valid consumers: {list(self.subscriptions.keys())}"
            )
        return self.subscriptions[consumer]
    
    @property
    def subscription(self) -> str:
        """
        Get the default subscription name.
        
        Returns:
            Default subscription name
            
        Raises:
            ValueError: If there's no default consumer
        """
        if self.default_consumer is None:
            raise ValueError(
                f"Topic '{self.name}' has multiple consumers and no default. "
                f"Available consumers: {list(self.subscriptions.keys())}. "
                f"Use get_subscription(consumer) instead."
            )
        return self.get_subscription(self.default_consumer)
    
    def __str__(self) -> str:
        return (
            f"Destination(name='{self.name}', "
            f"topic='{self.topic}', "
            f"schema='{self.schema}')"
        )
