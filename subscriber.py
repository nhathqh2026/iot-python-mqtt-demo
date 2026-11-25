"""Viewer client: subscribe to sensor topics and display received readings."""

import argparse
from uuid import uuid4

import paho.mqtt.client as mqtt

from config import (
    BROKER_HOST,
    BROKER_PORT,
    MQTT_KEEPALIVE_SECONDS,
    MQTT_QOS,
    light_topic_filter,
)
from measurement import decode_measurement


def on_connect(client, userdata, flags, reason_code, properties):
    """Subscribe after connecting; also runs after an automatic reconnection."""
    if reason_code == 0:
        topic_filter = userdata["topic_filter"]
        result, _ = client.subscribe(topic_filter, qos=MQTT_QOS)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"[SUBSCRIBE] {topic_filter} (QoS {MQTT_QOS})")
        else:
            print(f"[ERROR] SUBSCRIBE could not be sent: {mqtt.error_string(result)}")
    else:
        print(f"[ERROR] MQTT connection rejected: {reason_code}")


def on_message(client, userdata, msg):
    """Called automatically whenever a matching PUBLISH arrives from the broker."""
    try:
        measurement = decode_measurement(msg.payload)
        print(
            f"[RECEIVED] timestamp={measurement['timestamp']} | "
            f"area={measurement['area']} | lux={measurement['lux']} "
            f"| topic={msg.topic}"
        )
    except (UnicodeDecodeError, ValueError, TypeError) as exc:
        print(f"[WARNING] Ignoring invalid payload on {msg.topic}: {exc}")


def main():
    parser = argparse.ArgumentParser(description="View MQTT sensor measurements")
    parser.add_argument(
        "--filter", default=light_topic_filter(),
        help="MQTT Topic Filter (default: all areas' light measurements)",
    )
    args = parser.parse_args()
    if not args.filter:
        parser.error("--filter cannot be empty")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"it4735-viewer-{uuid4().hex[:10]}",
        protocol=mqtt.MQTTv311,
        userdata={"topic_filter": args.filter},
    )
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[BROKER] {BROKER_HOST}:{BROKER_PORT}")
    print(f"[FILTER] {args.filter}")
    print("[INFO] Waiting for measurements... Press Ctrl+C to stop.")
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=MQTT_KEEPALIVE_SECONDS)
        client.loop_forever()  # Runs the network loop and processes on_message events.
    except KeyboardInterrupt:
        print("\n[STOP] Subscriber stopped by user")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        print("[HINT] Check the broker address and whether the broker is running.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
