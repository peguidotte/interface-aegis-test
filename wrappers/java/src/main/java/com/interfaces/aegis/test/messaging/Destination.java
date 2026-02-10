package com.interfaces.aegis.test.messaging;

/**
 * Represents a complete Pub/Sub messaging destination.
 * 
 * A destination encapsulates:
 * - The topic name (where messages are published)
 * - The subscription name (where messages are consumed from)
 * - Semantic information about purpose and participants
 * 
 * This is an immutable value object that serves as the single source
 * of truth for Pub/Sub routing within Aegis Test.
 * 
 * @implNote All implementations MUST be immutable and thread-safe.
 */
public interface Destination {
    
    /**
     * Returns the semantic name of this destination.
     * Used for logging and debugging purposes.
     * 
     * @return semantic name in kebab-case (e.g., "specification-create-requested")
     */
    String getName();
    
    /**
     * Returns the full Pub/Sub topic name.
     * This is the actual GCP Pub/Sub topic identifier.
     * 
     * @return topic name (e.g., "aegis-test.specification.create.requested")
     */
    String getTopic();
    
    /**
     * Returns the full Pub/Sub subscription name for a specific consumer.
     * 
     * @param consumer the service consuming from this topic
     * @return subscription name (e.g., "orchestrator.aegis-test.specification.create.requested")
     */
    String getSubscription(String consumer);
    
    /**
     * Returns the default subscription name.
     * This is typically used when there's only one primary consumer.
     * 
     * @return default subscription name
     * @throws UnsupportedOperationException if there's no default consumer
     */
    String getSubscription();
    
    /**
     * Returns the schema identifier for the payload.
     * 
     * @return schema name (e.g., "SpecificationCreatedEventV1")
     */
    String getSchema();
}
