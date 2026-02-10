package com.interfaces.aegis.test.topics.specification;

import com.interfaces.aegis.test.messaging.Destination;
import java.util.Map;
import java.util.Objects;

/**
 * Destination for specification-created event.
 * 
 * <p>Event topic published when a test specification has been successfully created.
Emitted by the orchestrator after specification is persisted.
Consumed by analytics and notification services.
</p>
 * 
 * <p><strong>Contract:</strong> {@code SpecificationCreatedEventV1}</p>
 * 
 * @see com.interfaces.aegis.test.messaging.Topics#SPECIFICATION_CREATED
 */
public final class SpecificationCreated implements Destination {
    
    private static final String NAME = "specification-created";
    private static final String TOPIC = "aegis-test.specification.created";
    private static final String SCHEMA = "SpecificationCreatedEventV1";
    
    private static final Map<String, String> SUBSCRIPTIONS = Map.of(
            "analytics", "analytics.aegis-test.specification.created",
            "notifications", "notifications.aegis-test.specification.created"
        );
    
    public SpecificationCreated() {
        // Public constructor for instantiation
    }
    
    @Override
    public String getName() {
        return NAME;
    }
    
    @Override
    public String getTopic() {
        return TOPIC;
    }
    
    @Override
    public String getSubscription(String consumer) {
        Objects.requireNonNull(consumer, "consumer cannot be null");
        String subscription = SUBSCRIPTIONS.get(consumer);
        if (subscription == null) {
            throw new IllegalArgumentException(
                "Unknown consumer " + consumer + " for topic " + NAME + ". " +
                "Valid consumers: " + SUBSCRIPTIONS.keySet()
            );
        }
        return subscription;
    }
    
    @Override
    public String getSubscription() {
        throw new UnsupportedOperationException(
            "Topic " + NAME + " has multiple consumers. " +
            "Available consumers: " + SUBSCRIPTIONS.keySet() + ". " +
            "Use getSubscription(consumer) instead."
        );
    }
    
    @Override
    public String getSchema() {
        return SCHEMA;
    }
    
    @Override
    public String toString() {
        return "SpecificationCreated{" +
               "name='" + NAME + "'" +
               ", topic='" + TOPIC + "'" +
               ", schema='" + SCHEMA + "'" +
               "}";
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SpecificationCreated that = (SpecificationCreated) o;
        return Objects.equals(TOPIC, that.getTopic());
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(TOPIC);
    }
}
