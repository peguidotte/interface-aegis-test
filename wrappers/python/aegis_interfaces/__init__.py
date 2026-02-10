"""
Aegis Test Interfaces - Python

Python wrapper for Aegis Test messaging interfaces.
Provides type-safe access to Pub/Sub topics and subscriptions.

Usage:
    from aegis_interfaces.messaging import Topics
    
    # Access destinations
    destination = Topics.SPECIFICATION_CREATED
    topic = destination.topic
    subscription = destination.subscription
"""

__version__ = "1.0.0"

from aegis_interfaces.messaging.topics import Topics
from aegis_interfaces.messaging.destination import Destination, EventType

__all__ = [
    "Topics",
    "Destination",
    "EventType",
]
