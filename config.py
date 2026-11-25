"""Shared settings for the IT4735 MQTT demo. Edit this file in VS Code."""

# Option A: Local Mosquitto
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883

# Option B: HiveMQ Public Broker (uncomment to use)
# BROKER_HOST = "broker.hivemq.com"
# BROKER_PORT = 1883

# For a PUBLIC broker, replace this with a personal prefix, e.g.
# TOPIC_ROOT = "it4735/demo/your-unique-id/greenhouse"
# A public broker is shared: topics and messages are NOT private.
TOPIC_ROOT = "greenhouse"

# Simulated light sensor (change these values in VS Code)
SENSOR_AREA = 1
LUX_MIN = 100
LUX_MAX = 1000
PUBLISH_INTERVAL_SECONDS = 5

# Core MQTT settings (simple demo: QoS 0 and no retained messages)
MQTT_QOS = 0
MQTT_KEEPALIVE_SECONDS = 60


def light_topic(area: int) -> str:
    """Topic Name used by a sensor publisher."""
    if type(area) is not int or area < 1:
        raise ValueError("area must be a positive integer")
    return f"{TOPIC_ROOT}/area/{area}/light"


def light_topic_filter() -> str:
    """Topic Filter used by a viewer subscriber."""
    return f"{TOPIC_ROOT}/area/+/light"

