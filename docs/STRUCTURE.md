# Repository Structure

```
interfaces-aegis-test/
│
├── commands/                           # Command schemas (JSON Schema)
│   └── create-specification.v1.json   # CreateSpecificationCommandV1
│
├── events/                             # Event schemas (JSON Schema)
│   └── specification-created.v1.json  # SpecificationCreatedEventV1
│
├── topics/                             # Topic definitions (YAML)
│   ├── specification-create-requested.yaml
│   └── specification-created.yaml
│
├── wrappers/                           # Language-specific wrappers
│   │
│   ├── java/                          # Java wrapper
│   │   ├── pom.xml
│   │   ├── README.md
│   │   └── src/main/java/com/interfaces/aegis/test/
│   │       ├── messaging/
│   │       │   ├── Destination.java   # Interface for all destinations
│   │       │   └── Topics.java        # Central registry
│   │       └── topics/
│   │           └── specification/
│   │               ├── SpecificationCreateRequested.java
│   │               └── SpecificationCreated.java
│   │
│   └── python/                        # Python wrapper
│       ├── pyproject.toml
│       ├── README.md
│       └── aegis_interfaces/
│           ├── __init__.py
│           └── messaging/
│               ├── __init__.py
│               ├── destination.py     # Destination dataclass
│               └── topics.py          # Central registry
│
├── docs/                              # Documentation
│   ├── PUB_SUB_GUIDELINES.md         # Naming and conventions
│   ├── GETTING_STARTED.md            # Usage guide
│   ├── CONTRIBUTING.md               # How to add new topics
│   └── STRUCTURE.md                  # This file
│
└── README.md                          # Repository manifest
```

---

## Directory purposes

### `commands/`
JSON Schema definitions for **command payloads**.

Commands represent **intentions** - requests for something to happen.
Examples: CreateTest, ExecuteAgent, CancelExecution

### `events/`
JSON Schema definitions for **event payloads**.

Events represent **facts** - things that already happened.
Examples: TestCreated, AgentFinished, ExecutionCompleted

### `topics/`
YAML definitions of **Pub/Sub topology**.

Each file describes:
- Topic name (GCP Pub/Sub topic)
- Producers (who publishes)
- Consumers (who subscribes)
- Subscriptions (consumer-specific subscription names)
- Payload reference (which schema it carries)

### `wrappers/`
Type-safe code for each language.

Wrappers provide:
- No hardcoded strings in application code
- IDE autocomplete and type checking
- Single source of truth for messaging
- Immutable, thread-safe access

### `docs/`
Guidelines, conventions, and contribution guides.

---

## Data flow

```
Schema Definition (JSON)
    ↓
Topic Definition (YAML) ← references schema
    ↓
Wrapper Generation (Java/Python) ← references topic
    ↓
Application Code ← imports wrapper
```

---

## Extension points

### Adding a new domain

1. Create new directory in `wrappers/java/.../topics/<domain>/`
2. Create new directory for Python (if needed)
3. Group related topics together

### Adding new language support

1. Create `wrappers/<language>/`
2. Implement equivalent of `Destination` abstraction
3. Implement equivalent of `Topics` registry
4. Mirror the topology from YAML definitions

---

## Principles

1. **Schemas are source of truth** for contracts
2. **Topics YAML is source of truth** for topology
3. **Wrappers are projections** (generated/maintained from definitions)
4. **No business logic** in this repository
5. **No infrastructure code** in this repository
