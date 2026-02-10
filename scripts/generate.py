#!/usr/bin/env python3
"""
Aegis Test Interfaces Generator

Generates all wrappers and documentation from events/ and topics/ definitions.
Single source of truth: events/ and topics/ YAML files.

Generates:
  - asyncapi.yaml (3.1.0)
  - Java wrappers
  - Python wrappers
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Event:
    """Represents a domain event."""
    name: str
    schema_path: str
    schema: Dict[str, Any]

    @property
    def schema_name(self) -> str:
        """Extract schema name from title."""
        return self.schema.get("title", self.name)

    @property
    def description(self) -> str:
        """Get schema description."""
        return self.schema.get("description", "")

    @property
    def properties(self) -> Dict[str, Any]:
        """Get schema properties."""
        return self.schema.get("properties", {})

    @property
    def required(self) -> List[str]:
        """Get required fields."""
        return self.schema.get("required", [])


@dataclass
class Topic:
    """Represents a messaging topic."""
    name: str
    topic: str
    description: str
    produced_by: List[str]
    consumed_by: List[str]
    subscriptions: Dict[str, str]
    event_schema: str
    event_type: str

    def get_default_consumer(self) -> str:
        """Get default consumer if only one exists."""
        if len(self.consumed_by) == 1:
            return self.consumed_by[0]
        return None

    def get_java_constant_name(self) -> str:
        """Convert topic name to Java constant."""
        return "_".join(self.name.upper().split("-"))


class Generator:
    """Main generator orchestrator."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.events_dir = repo_root / "events"
        self.topics_dir = repo_root / "topics"
        self.wrappers_java_dir = repo_root / "wrappers" / "java"
        self.wrappers_python_dir = repo_root / "wrappers" / "python"

        self.events: Dict[str, Event] = {}
        self.topics: List[Topic] = []
        self.domains: Dict[str, List[Topic]] = {}

    def load_events(self) -> None:
        """Load all events from events/ directory."""
        print(f"📖 Loading events from {self.events_dir}...")

        if not self.events_dir.exists():
            raise FileNotFoundError(f"Events directory not found: {self.events_dir}")

        for json_file in sorted(self.events_dir.glob("*.json")):
            with open(json_file) as f:
                schema = json.load(f)
            
            # Extract event name from filename (e.g., specification-created.v1.json)
            base_name = json_file.stem.rsplit(".", 1)[0]
            
            event = Event(
                name=base_name,
                schema_path=str(json_file.relative_to(self.repo_root)),
                schema=schema
            )
            
            self.events[event.schema_name] = event
            print(f"  ✓ {event.schema_name}")

    def load_topics(self) -> None:
        """Load all topics from topics/ directory."""
        print(f"📖 Loading topics from {self.topics_dir}...")

        if not self.topics_dir.exists():
            raise FileNotFoundError(f"Topics directory not found: {self.topics_dir}")

        for yaml_file in sorted(self.topics_dir.glob("*.yaml")):
            with open(yaml_file) as f:
                topic_def = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ["name", "topic", "producedBy", "consumedBy", "subscriptions", "payload"]
            for field in required_fields:
                if field not in topic_def:
                    raise ValueError(f"Topic {yaml_file.name} missing required field: {field}")

            payload = topic_def.get("payload", {})
            
            topic = Topic(
                name=topic_def.get("name"),
                topic=topic_def.get("topic"),
                description=topic_def.get("description", ""),
                produced_by=topic_def.get("producedBy", []),
                consumed_by=topic_def.get("consumedBy", []),
                subscriptions=topic_def.get("subscriptions", {}),
                event_schema=payload.get("schema", ""),
                event_type=payload.get("type", "event")
            )
            
            self.topics.append(topic)
            
            # Group by domain (first part of topic name)
            domain = topic.topic.split(".")[1]
            if domain not in self.domains:
                self.domains[domain] = []
            self.domains[domain].append(topic)
            
            print(f"  ✓ {topic.name} ({topic.topic})")

    def validate(self) -> None:
        """Validate consistency between events and topics."""
        print("\n🔍 Validating...")
        
        for topic in self.topics:
            if topic.event_schema not in self.events:
                raise ValueError(
                    f"Topic '{topic.name}' references unknown event schema: {topic.event_schema}"
                )
            
            if topic.event_type != "event":
                raise ValueError(
                    f"Topic '{topic.name}' has invalid type '{topic.event_type}'. Only 'event' is supported."
                )
        
        print("  ✓ All topics reference valid events")
        print("  ✓ All topics are event-driven (no commands)")

    def generate_asyncapi(self) -> None:
        """Generate asyncapi.yaml from topics and events."""
        print("\n📝 Generating asyncapi.yaml...")

        asyncapi = {
            "asyncapi": "3.1.0",
            "info": {
                "title": "Aegis Test Event-Driven Architecture",
                "description": "Complete event topology for the Aegis Test system.\nThis specification defines all events flowing through Google Cloud Pub/Sub,\nincluding producers, consumers, and payload schemas.",
                "version": "1.0.0",
                "contact": {
                    "name": "Aegis Test Team",
                    "url": "https://github.com/peguidotte/interface-aegis-test"
                },
                "license": {
                    "name": "MIT"
                }
            },
            "defaultContentType": "application/json",
            "servers": {
                "production": {
                    "host": "pubsub.googleapis.com",
                    "protocol": "googlepubsub",
                    "description": "Google Cloud Pub/Sub production server",
                    "variables": {
                        "projectId": {
                            "default": "aegis-test-prod",
                            "description": "Google Cloud Project ID"
                        }
                    }
                }
            },
            "channels": {},
            "components": {
                "messages": {},
                "schemas": {},
                "messageTraits": {
                    "CommonEventMetadata": {
                        "headers": {
                            "type": "object",
                            "properties": {
                                "schema": {
                                    "type": "string",
                                    "description": "Schema identifier for validation",
                                    "example": "SpecificationRequestedEventV1"
                                },
                                "correlationId": {
                                    "type": "string",
                                    "format": "uuid",
                                    "description": "Correlation ID for tracing events across services"
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Service that published the event",
                                    "example": "portal"
                                },
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time",
                                    "description": "Server timestamp when event was published"
                                }
                            }
                        }
                    }
                }
            }
        }

        # Add channels and messages
        for topic in self.topics:
            event = self.events[topic.event_schema]
            
            # Build topology description
            topology = f"Producer: {', '.join(topic.produced_by)}\nConsumer: {', '.join(topic.consumed_by)}"
            
            # Add channel
            asyncapi["channels"][topic.name] = {
                "address": f"projects/{{projectId}}/topics/{topic.topic}",
                "title": topic.name.replace("-", " ").title(),
                "description": topic.description + f"\n\n**Topology:**\n- {topology.replace(chr(10), chr(10) + '- ')}\n- Guarantee: at-least-once",
                "messages": {
                    topic.event_schema: {
                        "$ref": f"#/components/messages/{topic.event_schema}"
                    }
                },
                "bindings": {
                    "googlepubsub": {
                        "schemaSettings": {
                            "name": topic.event_schema,
                            "encoding": "json"
                        }
                    }
                }
            }

            # Add message if not already added
            if topic.event_schema not in asyncapi["components"]["messages"]:
                asyncapi["components"]["messages"][topic.event_schema] = {
                    "name": topic.event_schema,
                    "title": event.schema_name,
                    "contentType": "application/json",
                    "description": event.description,
                    "payload": {
                        "$ref": f"#/components/schemas/{topic.event_schema}"
                    },
                    "traits": [
                        {"$ref": "#/components/messageTraits/CommonEventMetadata"}
                    ]
                }

            # Add schema if not already added
            if topic.event_schema not in asyncapi["components"]["schemas"]:
                asyncapi["components"]["schemas"][topic.event_schema] = event.schema

        # Write asyncapi.yaml
        asyncapi_path = self.repo_root / "asyncapi.yaml"
        with open(asyncapi_path, "w", encoding="utf-8") as f:
            yaml.dump(asyncapi, f, default_flow_style=False, sort_keys=False)
        
        print(f"  ✓ Generated {asyncapi_path.relative_to(self.repo_root)}")

    def generate_java_wrappers(self) -> None:
        """Generate Java wrapper classes."""
        print("\n🔧 Generating Java wrappers...")

        # Generate each topic class
        for topic in self.topics:
            domain = topic.topic.split(".")[1]
            domain_dir = self.wrappers_java_dir / "src" / "main" / "java" / "com" / "interfaces" / "aegis" / "test" / "topics" / domain
            domain_dir.mkdir(parents=True, exist_ok=True)

            # Generate class name from topic name
            class_name = "".join(word.capitalize() for word in topic.name.split("-"))
            java_file = domain_dir / f"{class_name}.java"

            java_code = self._generate_java_class(topic, class_name)
            
            with open(java_file, "w", encoding="utf-8") as f:
                f.write(java_code)
            
            print(f"  ✓ Generated {java_file.relative_to(self.repo_root)}")

        # Generate Topics.java registry
        self._generate_java_topics_registry()

    def _generate_java_class(self, topic: Topic, class_name: str) -> str:
        """Generate a Java destination class."""
        domain = topic.topic.split(".")[1]
        default_consumer = topic.get_default_consumer()
        
        # Build subscriptions map
        subscriptions_lines = []
        for consumer, sub in topic.subscriptions.items():
            subscriptions_lines.append('            "{}", "{}"'.format(consumer, sub))
        
        if len(subscriptions_lines) == 0:
            subscriptions_map = "Map.of();"
        elif len(subscriptions_lines) == 1:
            subscriptions_map = "Map.of(\n" + subscriptions_lines[0] + "\n        );"
        else:
            subscriptions_map = "Map.of(\n" + ",\n".join(subscriptions_lines) + "\n        );"

        # Get subscription implementation
        if default_consumer:
            get_subscription_impl = "    @Override\n    public String getSubscription() {\n        return getSubscription(DEFAULT_CONSUMER);\n    }"
        else:
            get_subscription_impl = (
                "    @Override\n"
                "    public String getSubscription() {\n"
                "        throw new UnsupportedOperationException(\n"
                '            "Topic " + NAME + " has multiple consumers. " +\n'
                '            "Available consumers: " + SUBSCRIPTIONS.keySet() + ". " +\n'
                '            "Use getSubscription(consumer) instead."\n'
                "        );\n"
                "    }"
            )

        default_consumer_decl = 'private static final String DEFAULT_CONSUMER = "{}";'.format(default_consumer) if default_consumer else ""
        const_name = "_".join(topic.name.upper().split("-"))

        output = []
        output.append("package com.interfaces.aegis.test.topics.{};".format(domain))
        output.append("")
        output.append("import com.interfaces.aegis.test.messaging.Destination;")
        output.append("import java.util.Map;")
        output.append("import java.util.Objects;")
        output.append("")
        output.append("/**")
        output.append(" * Destination for {} event.".format(topic.name))
        output.append(" * ")
        output.append(" * <p>{}</p>".format(topic.description))
        output.append(" * ")
        output.append(" * <p><strong>Contract:</strong> {{{}}}</p>".format("@code " + topic.event_schema))
        output.append(" * ")
        output.append(" * @see com.interfaces.aegis.test.messaging.Topics#{}".format(const_name))
        output.append(" */")
        output.append("public final class {} implements Destination {{".format(class_name))
        output.append("    ")
        output.append('    private static final String NAME = "{}";'.format(topic.name))
        output.append('    private static final String TOPIC = "{}";'.format(topic.topic))
        output.append('    private static final String SCHEMA = "{}";'.format(topic.event_schema))
        if default_consumer_decl:
            output.append("    " + default_consumer_decl)
        output.append("    ")
        output.append("    private static final Map<String, String> SUBSCRIPTIONS = {}".format(subscriptions_map))
        output.append("    ")
        output.append("    public {}() {{".format(class_name))
        output.append("        // Public constructor for instantiation")
        output.append("    }")
        output.append("    ")
        output.append("    @Override")
        output.append("    public String getName() {")
        output.append("        return NAME;")
        output.append("    }")
        output.append("    ")
        output.append("    @Override")
        output.append("    public String getTopic() {")
        output.append("        return TOPIC;")
        output.append("    }")
        output.append("    ")
        output.append("    @Override")
        output.append("    public String getSubscription(String consumer) {")
        output.append('        Objects.requireNonNull(consumer, "consumer cannot be null");')
        output.append("        String subscription = SUBSCRIPTIONS.get(consumer);")
        output.append("        if (subscription == null) {")
        output.append('            throw new IllegalArgumentException(')
        output.append('                "Unknown consumer " + consumer + " for topic " + NAME + ". " +')
        output.append('                "Valid consumers: " + SUBSCRIPTIONS.keySet()')
        output.append("            );")
        output.append("        }")
        output.append("        return subscription;")
        output.append("    }")
        output.append("    ")
        output.append(get_subscription_impl)
        output.append("    ")
        output.append("    @Override")
        output.append("    public String getSchema() {")
        output.append("        return SCHEMA;")
        output.append("    }")
        output.append("    ")
        output.append("    @Override")
        output.append("    public String toString() {")
        output.append("        return \"{}{{\" +".format(class_name))
        output.append("               \"name='\" + NAME + \"'\" +")
        output.append("               \", topic='\" + TOPIC + \"'\" +")
        output.append("               \", schema='\" + SCHEMA + \"'\" +")
        output.append("               \"}\";")
        output.append("    }")
        output.append("    ")
        output.append("    @Override")
        output.append("    public boolean equals(Object o) {")
        output.append("        if (this == o) return true;")
        output.append("        if (o == null || getClass() != o.getClass()) return false;")
        output.append("        {} that = ({}) o;".format(class_name, class_name))
        output.append("        return Objects.equals(TOPIC, that.getTopic());")
        output.append("    }")
        output.append("    ")
        output.append("    @Override")
        output.append("    public int hashCode() {")
        output.append("        return Objects.hash(TOPIC);")
        output.append("    }")
        output.append("}")
        
        return "\n".join(output) + "\n"

    def _generate_java_topics_registry(self) -> None:
        """Generate Topics.java registry class."""
        topics_file = self.wrappers_java_dir / "src" / "main" / "java" / "com" / "interfaces" / "aegis" / "test" / "messaging" / "Topics.java"
        
        imports = []
        for topic in self.topics:
            domain = topic.topic.split(".")[1]
            class_name = "".join(word.capitalize() for word in topic.name.split("-"))
            imports.append("import com.interfaces.aegis.test.topics.{}.{};".format(domain, class_name))

        output = []
        output.append("package com.interfaces.aegis.test.messaging;")
        output.append("")
        output.extend(sorted(imports))
        output.append("")
        output.append("/**")
        output.append(" * Central registry of all Pub/Sub destinations in Aegis Test.")
        output.append(" * ")
        output.append(" * <p>This class serves as the single entry point for accessing")
        output.append(" * topic and subscription information. All messaging code should")
        output.append(" * reference destinations through this class, never using string")
        output.append(" * literals directly.</p>")
        output.append(" * ")
        output.append(" * <p><strong>Design Principles:</strong></p>")
        output.append(" * <ul>")
        output.append(" *   <li>NO string literals for topics or subscriptions in application code</li>")
        output.append(" *   <li>Type-safe access to all messaging destinations</li>")
        output.append(" *   <li>Single source of truth for Pub/Sub topology</li>")
        output.append(" *   <li>Immutable and thread-safe</li>")
        output.append(" * </ul>")
        output.append(" */")
        output.append("public final class Topics {")
        output.append("    ")
        output.append("    private Topics() {")
        output.append("        throw new AssertionError(\"Topics class should not be instantiated\");")
        output.append("    }")
        output.append("    ")
        
        # Group by domain
        for domain in sorted(self.domains.keys()):
            output.append("    // ────────────────────────────────────────────────────────────────")
            output.append("    // {} DOMAIN".format(domain.upper()))
            output.append("    // ────────────────────────────────────────────────────────────────")
            output.append("")
            
            for topic in self.domains[domain]:
                class_name = "".join(word.capitalize() for word in topic.name.split("-"))
                const_name = "_".join(topic.name.upper().split("-"))
                producers = ", ".join(topic.produced_by)
                consumers = ", ".join(topic.consumed_by)
                
                # Build javadoc with proper braces for @code tag
                output.append("    /**")
                output.append("     * Event topic: {}".format(topic.name))
                output.append("     * ")
                output.append("     * <p><strong>Producers:</strong> {}</p>".format(producers))
                output.append("     * <p><strong>Consumers:</strong> {}</p>".format(consumers))
                output.append("     * <p><strong>Payload:</strong> {" + "@code " + topic.event_schema + "}</p>")
                output.append("     */")
                output.append("    public static final Destination {} = new {}();".format(const_name, class_name))
                output.append("")
        
        output.append("}")
        
        with open(topics_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output) + "\n")
        
        print("  ✓ Generated {}".format(topics_file.relative_to(self.repo_root)))

    def generate_python_wrappers(self) -> None:
        """Generate Python wrapper files."""
        print("\n🐍 Generating Python wrappers...")

        # Generate destination.py with EventType enum
        self._generate_python_destination()

        # Generate topics.py registry
        self._generate_python_topics()

    def _generate_python_destination(self) -> None:
        """Generate Python destination.py with EventType enum."""
        dest_file = self.wrappers_python_dir / "aegis_interfaces" / "messaging" / "destination.py"

        event_types = "\n    ".join([
            f'{topic.event_schema.upper()} = "{topic.topic}"'
            for topic in sorted(self.topics, key=lambda t: t.event_schema)
        ])

        python_code = f'''"""
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
    {event_types}


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
                f"Unknown consumer '{{consumer}}' for topic '{{self.name}}'. "
                f"Valid consumers: {{list(self.subscriptions.keys())}}"
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
                f"Topic '{{self.name}}' has multiple consumers and no default. "
                f"Available consumers: {{list(self.subscriptions.keys())}}. "
                f"Use get_subscription(consumer) instead."
            )
        return self.get_subscription(self.default_consumer)
    
    def __str__(self) -> str:
        return (
            f"Destination(name='{{self.name}}', "
            f"topic='{{self.topic}}', "
            f"schema='{{self.schema}}')"
        )
'''

        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(python_code)
        
        print(f"  ✓ Generated {dest_file.relative_to(self.repo_root)}")

    def _generate_python_topics(self) -> None:
        """Generate Python topics.py registry."""
        topics_file = self.wrappers_python_dir / "aegis_interfaces" / "messaging" / "topics.py"

        topics_content = '''"""
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
    
'''

        # Group by domain
        for domain in sorted(self.domains.keys()):
            topics_content += f"    # ────────────────────────────────────────────────────────────────\n"
            topics_content += f"    # {domain.upper()} DOMAIN\n"
            topics_content += f"    # ────────────────────────────────────────────────────────────────\n\n"
            
            for topic in self.domains[domain]:
                const_name = "_".join(topic.name.upper().split("-"))
                default_consumer = topic.get_default_consumer()
                
                subscriptions = "{\n"
                for consumer, sub in topic.subscriptions.items():
                    subscriptions += f'            "{consumer}": "{sub}",\n'
                subscriptions = subscriptions.rstrip(",\n") + "\n        }"
                
                default_consumer_str = f'"{default_consumer}"' if default_consumer else "None"
                
                topics_content += f'''    {const_name} = Destination(
        name="{topic.name}",
        topic="{topic.topic}",
        subscriptions={subscriptions},
        event_type=EventType.{topic.event_schema.upper()},
        schema="{topic.event_schema}",
        default_consumer={default_consumer_str},
    )
    """Event: {topic.name}"""
    
'''
        
        topics_content += '''    def __init__(self) -> None:
        """Private constructor - this class should not be instantiated."""
        raise TypeError("Topics class should not be instantiated")
'''
        
        with open(topics_file, "w", encoding="utf-8") as f:
            f.write(topics_content)
        
        print(f"  ✓ Generated {topics_file.relative_to(self.repo_root)}")

    def run(self) -> None:
        """Run the complete generation process."""
        print("\n" + "=" * 60)
        print("🚀 Aegis Test Interfaces Generator")
        print("=" * 60)
        
        try:
            self.load_events()
            self.load_topics()
            self.validate()
            self.generate_asyncapi()
            self.generate_java_wrappers()
            self.generate_python_wrappers()
            
            print("\n" + "=" * 60)
            print("✅ Generation complete!")
            print("=" * 60)
            print("\nUpdated files:")
            print("  📝 asyncapi.yaml")
            print("  🔧 wrappers/java/src/main/java/com/interfaces/aegis/test/...")
            print("  🐍 wrappers/python/aegis_interfaces/messaging/...")
            
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    generator = Generator(repo_root)
    generator.run()
