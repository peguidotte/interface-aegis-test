package com.interfaces.aegis.test.topics.specification;

import com.interfaces.aegis.test.messaging.Destination;
import java.util.Map;
import java.util.Objects;

/**
 * Destination for specification-requested event.
 * 
 * <p>Event published when a new test specification is requested.
Published by the portal when a user submits a new specification request.
Consumed by the orchestrator to initiate test generation workflow.
</p>
 * 
 * <p><strong>Contract:</strong> {@code SpecificationRequestedEventV1}</p>
 * 
 * @see com.interfaces.aegis.test.messaging.Topics#SPECIFICATION_REQUESTED
 */
public final class SpecificationRequested implements Destination {
    
    private static final String NAME = "specification-requested";
    private static final String TOPIC = "aegis-test.specification.requested";
    private static final String SCHEMA = "SpecificationRequestedEventV1";
    private static final String DEFAULT_CONSUMER = "orchestrator";
    
    private static final Map<String, String> SUBSCRIPTIONS = Map.of(
            "orchestrator", "orchestrator.aegis-test.specification.requested"
        );
    
    public SpecificationRequested() {
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
        return getSubscription(DEFAULT_CONSUMER);
    }
    
    @Override
    public String getSchema() {
        return SCHEMA;
    }
    
    @Override
    public String toString() {
        return "SpecificationRequested{" +
               "name='" + NAME + "'" +
               ", topic='" + TOPIC + "'" +
               ", schema='" + SCHEMA + "'" +
               "}";
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SpecificationRequested that = (SpecificationRequested) o;
        return Objects.equals(TOPIC, that.getTopic());
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(TOPIC);
    }
}
