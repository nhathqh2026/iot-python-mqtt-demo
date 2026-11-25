"""Simulated IoT sensor: publish light measurements every five seconds."""

import argparse
import random
import threading
import time
from uuid import uuid4

import paho.mqtt.client as mqtt

from config import (
    BROKER_HOST,
    BROKER_PORT,
    LUX_MAX,
    LUX_MIN,
    MQTT_KEEPALIVE_SECONDS,
    MQTT_QOS,
    PUBLISH_INTERVAL_SECONDS,
    SENSOR_AREA,
    light_topic,
)
from measurement import create_measurement, encode_measurement

connected = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    """Called when the MQTT broker responds to CONNECT (Paho Callback API v2)."""
    if reason_code == 0:
        connected.set()
        print("[CONNECTED] MQTT Broker accepted the connection")
    else:
        connected.clear()
        print(f"[ERROR] MQTT connection rejected: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    connected.clear()
    if reason_code != 0:
        print(f"[WARNING] MQTT connection lost: {reason_code}")


def main():
    parser = argparse.ArgumentParser(description="Publish simulated light sensor data")
    parser.add_argument("--area", type=int, default=SENSOR_AREA, help="sensor area (default: config.py)")
    parser.add_argument("--count", type=int, default=0, help="number of readings; 0 = keep running")
    args = parser.parse_args()
    if args.area < 1 or args.count < 0:
        parser.error("--area must be >= 1 and --count must be >= 0")
    if LUX_MIN < 0 or LUX_MAX < LUX_MIN:
        parser.error("invalid LUX_MIN/LUX_MAX in config.py")

    topic = light_topic(args.area)
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"it4735-sensor-{uuid4().hex[:10]}",
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    print(f"[BROKER] {BROKER_HOST}:{BROKER_PORT}")
    print(f"[TOPIC]  {topic}")
    print(f"[MODE]   QoS {MQTT_QOS}, retain=False, interval={PUBLISH_INTERVAL_SECONDS}s")

    loop_started = False
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=MQTT_KEEPALIVE_SECONDS)
        client.loop_start()
        loop_started = True
        if not connected.wait(10):
            raise RuntimeError("MQTT connection was not accepted within 10 seconds")

        sent = 0
        while args.count == 0 or sent < args.count:
            if not connected.wait(10):
                print("[WARNING] Broker not connected; trying again...")
                continue

            measurement = create_measurement(args.area, random.randint(LUX_MIN, LUX_MAX))
            payload = encode_measurement(measurement)
            result = client.publish(topic, payload=payload, qos=MQTT_QOS, retain=False)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"[ERROR] Failed to queue PUBLISH: {mqtt.error_string(result.rc)}")
            else:
                result.wait_for_publish(timeout=5)
                if result.is_published():
                    print(f"[PUBLISH] {topic} -> {payload}")
                else:
                    print("[WARNING] PUBLISH did not finish within 5 seconds")
            sent += 1
            if args.count == 0 or sent < args.count:
                time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[STOP] Publisher stopped by user")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        print("[HINT] Check the broker address and whether the broker is running.")
    finally:
        if loop_started:
            client.disconnect()
            client.loop_stop()


if __name__ == "__main__":
    main()