package com.interfaces.aegis.test.messaging;

import com.interfaces.aegis.test.topics.specification.SpecificationCreated;
import com.interfaces.aegis.test.topics.specification.SpecificationRequested;

/**
 * Central registry of all Pub/Sub destinations in Aegis Test.
 * 
 * <p>This class serves as the single entry point for accessing
 * topic and subscription information. All messaging code should
 * reference destinations through this class, never using string
 * literals directly.</p>
 * 
 * <p><strong>Design Principles:</strong></p>
 * <ul>
 *   <li>NO string literals for topics or subscriptions in application code</li>
 *   <li>Type-safe access to all messaging destinations</li>
 *   <li>Single source of truth for Pub/Sub topology</li>
 *   <li>Immutable and thread-safe</li>
 * </ul>
 */
public final class Topics {
    
    private Topics() {
        throw new AssertionError("Topics class should not be instantiated");
    }
    
    // ────────────────────────────────────────────────────────────────
    // SPECIFICATION DOMAIN
    // ────────────────────────────────────────────────────────────────

    /**
     * Event topic: specification-created
     * 
     * <p><strong>Producers:</strong> orchestrator</p>
     * <p><strong>Consumers:</strong> analytics, notifications</p>
     * <p><strong>Payload:</strong> {@code SpecificationCreatedEventV1}</p>
     */
    public static final Destination SPECIFICATION_CREATED = new SpecificationCreated();

    /**
     * Event topic: specification-requested
     * 
     * <p><strong>Producers:</strong> portal</p>
     * <p><strong>Consumers:</strong> orchestrator</p>
     * <p><strong>Payload:</strong> {@code SpecificationRequestedEventV1}</p>
     */
    public static final Destination SPECIFICATION_REQUESTED = new SpecificationRequested();

}
