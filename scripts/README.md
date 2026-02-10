# Generator Scripts

This directory contains automation scripts that synchronize the entire codebase with definitions from `events/` and `topics/`.

## Single Source of Truth

The actual definitions of your messaging system are in **two places only**:
1. **`events/`** - Event schemas (JSON Schema)
2. **`topics/`** - Topic definitions (YAML)

Everything else is **auto-generated** from these two sources:
- `asyncapi.yaml` - Visual topology documentation
- `wrappers/java/` - Java wrapper classes
- `wrappers/python/` - Python wrapper code

**This means:** When you modify a topic or event, you run the generator and everything stays in sync automatically. No more manual updates to 4 different places!

## Quick Start

### Option 1: PowerShell (Windows)
```powershell
.\scripts\generate.ps1
```

### Option 2: Direct Python
```bash
python scripts/generate.py
```

### Option 3: Make/bash
```bash
cd scripts && python generate.py
```

## Workflow

### ✅ Do This
1. Modify/add files in `events/` or `topics/`
2. Run `scripts/generate.ps1` (or `python scripts/generate.py`)
3. Commit the generated files

### ❌ Don't Do This
- ❌ Manually edit `asyncapi.yaml`
- ❌ Manually edit Java destination classes
- ❌ Manually edit Python Topics registry

(Any manual changes will be overwritten by the next generation)

## Adding a New Event Topic

### Step 1: Create Event Schema
Create a new file in `events/` following the naming convention: `<domain>-<resource>-<action>.v1.json`

Example: `events/execution-test-started.v1.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ExecutionTestStartedEventV1",
  "description": "Fired when an orchestrator begins executing a test",
  "required": ["eventId", "eventTimestamp", "executionId"],
  "properties": {
    "eventId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this event"
    },
    "eventTimestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the test execution started"
    },
    "executionId": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the test execution"
    }
  }
}
```

### Step 2: Create Topic Definition
Create a new file in `topics/` following the naming convention: `<domain>-<resource>-<action>.yaml`

Example: `topics/execution-test-started.yaml`

```yaml
name: execution-test-started
description: Signals that a test execution has begun
topic: aegis-test.execution.test.started

producedBy:
  - orchestrator

consumedBy:
  - agents
  - dashboard

subscriptions:
  agents: agents.aegis-test.execution.test.started
  dashboard: dashboard.aegis-test.execution.test.started

payload:
  type: event
  schema: ExecutionTestStartedEventV1
```

### Step 3: Generate
```powershell
.\scripts\generate.ps1
```

That's it! The generator automatically:
- ✅ Creates `ExecutionTestStarted.java` in the right domain folder
- ✅ Registers it in `Topics.java`
- ✅ Creates Python destination in `Topics` class
- ✅ Adds the channel to `asyncapi.yaml`
- ✅ References the event schema in AsyncAPI

## Generator Details

### Input Files
- `events/` - JSON Schema files for all event types
- `topics/*.yaml` - Topic definitions with producer/consumer mappings

### Output Files (Auto-Generated)
- `asyncapi.yaml` - AsyncAPI 3.1.0 specification
- `wrappers/java/src/main/java/com/interfaces/aegis/test/topics/<domain>/<EventType>.java`
- `wrappers/python/aegis_interfaces/messaging/topics.py`
- `wrappers/python/aegis_interfaces/messaging/destination.py` (with EventType enum)

### Validation
The generator validates:
- ✅ All referenced events exist
- ✅ All topics are event-driven (no commands)
- ✅ Required fields in topic definitions
- ✅ Consistent naming conventions

## Topic YAML Schema

```yaml
name: <kebab-case-topic-name>
description: <human-readable description>
topic: aegis-test.<domain>.<resource>.<action>

producedBy:
  - <service-1>
  - <service-2>

consumedBy:
  - <service-1>
  - <service-2>

subscriptions:
  <consumer-1>: <consumer-1>.<full-topic-name>
  <consumer-2>: <consumer-2>.<full-topic-name>

payload:
  type: event  # Only "event" is supported
  schema: <SchemaNameFromEventsFile>  # Must match title in JSON schema
```

## Naming Conventions

### Topic Names (kebab-case)
```
specification-created
execution-test-started
```

→ Used for: Java constant names, channel names, references

### Topic Paths (dot-notation)
```
aegis-test.specification.created
aegis-test.execution.test.started
```

Format: `aegis-test.<domain>.<resource>.<action>`

### Subscription Names (dot-notation)
```
orchestrator.aegis-test.specification.created
agents.aegis-test.execution.test.started
```

Format: `<consumer>.aegis-test.<domain>.<resource>.<action>`

### Event Schema Names (PascalCase+Version)
```
SpecificationCreatedEventV1
ExecutionTestStartedEventV1
```

Format: `<Resource><Action>EventV<N>`

## Troubleshooting

### "Unknown consumer 'xyz' for topic..."
- Check the `subscriptions` in the topic YAML
- Verify the consumer name matches what you're using in code

### Generator errors about missing events
- Check that the `schema` field in topic YAML matches the `title` in the JSON Schema file
- File naming doesn't have to match - only the schema title matters

### Generated Java code has wrong domain
- Check the topic path format: must be `aegis-test.<domain>.<resource>.<action>`
- The first part after `aegis-test` is the domain folder

## Advanced

### Using Generated Code in Java
```java
import com.interfaces.aegis.test.messaging.Topics;
import com.interfaces.aegis.test.messaging.Destination;

// Access topic
Destination topic = Topics.SPECIFICATION_CREATED;
String topicName = topic.getTopic();  // "aegis-test.specification.created"

// Get subscription
String subscription = topic.getSubscription("portal");
```

### Using Generated Code in Python
```python
from aegis_interfaces.messaging.topics import Topics
from aegis_interfaces.messaging.destination import EventType

# Access topic
destination = Topics.SPECIFICATION_CREATED
print(destination.topic)  # "aegis-test.specification.created"

# Get subscription
subscription = destination.get_subscription("portal")
# Or use default if single consumer:
subscription = destination.subscription
```

## CI/CD Integration

Add this to your CI/CD pipeline to ensure definitions and generated code stay in sync:

```bash
# Regenerate everything
python scripts/generate.py

# Check if anything changed
if git diff --quiet asyncapi.yaml wrappers/; then
  echo "✅ Generated code is up-to-date"
else
  echo "❌ Generated code is stale. Run: python scripts/generate.py"
  exit 1
fi
```
