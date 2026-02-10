"""
Central registry of all Pub/Sub destinations in Aegis Test.

This module serves as the single entry point for accessing topic and
subscription information. All messaging code should reference destinations
through this module, never using string literals directly.

Design Principles:
    - NO string literals for topics or subscriptions in application code
    - Type-safe access to all messaging destinations
    - Single source of truth for Pub/Sub topology
    - Immutable and thread-safe
"""

from aegis_interfaces.messaging.destination import Destination, EventType


class Topics:
    """Central registry of all Pub/Sub messaging destinations."""
    
    # ────────────────────────────────────────────────────────────────
    # SPECIFICATION DOMAIN
    # ────────────────────────────────────────────────────────────────

    SPECIFICATION_CREATED = Destination(
        name="specification-created",
        topic="aegis-test.specification.created",
        subscriptions={
            "analytics": "analytics.aegis-test.specification.created",
            "notifications": "notifications.aegis-test.specification.created"
        },
        event_type=EventType.SPECIFICATIONCREATEDEVENTV1,
        schema="SpecificationCreatedEventV1",
        default_consumer=None,
    )
    """Event: specification-created"""
    
    SPECIFICATION_REQUESTED = Destination(
        name="specification-requested",
        topic="aegis-test.specification.requested",
        subscriptions={
            "orchestrator": "orchestrator.aegis-test.specification.requested"
        },
        event_type=EventType.SPECIFICATIONREQUESTEDEVENTV1,
        schema="SpecificationRequestedEventV1",
        default_consumer="orchestrator",
    )
    """Event: specification-requested"""
    
    def __init__(self) -> None:
        """Private constructor - this class should not be instantiated."""
        raise TypeError("Topics class should not be instantiated")
