import paho.mqtt.client as mqtt
import json
import time
import socket
import ssl
import sys
from iwatch_simulator import IWatchSimulator


class MQTTPublisher:

    def __init__(self, config_path, broker_ip, broker_port, thing_id, topic, username, password):
        self.simulator = IWatchSimulator(config_path)
        self.client = mqtt.Client()
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.thing_id = thing_id
        self.org_name, self.thing = thing_id.split(':')
        self.topic = topic
        self.username = username
        self.password = password
        self.setup_client()

    def setup_client(self):
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.tls_set(ca_certs="/app/Eclipse-Ditto-MQTT-iWatch-SSL/mosquitto/config/ca.crt",
                            certfile="/app/Eclipse-Ditto-MQTT-iWatch-SSL/mosquitto/config/client.crt",
                            keyfile="/app/Eclipse-Ditto-MQTT-iWatch-SSL/mosquitto/config/client.pk8",
                            tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.username_pw_set(self.username, self.password)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        client.subscribe(self.topic)

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker with result code " + str(rc))

    def on_publish(self, client, userdata, mid):
        print("Message published to " + self.topic)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def send_data_to_ditto(self, iwatch_data):
        ditto_data = {
            "topic": f"{self.org_name}/{self.thing}/things/twin/commands/modify",
            "path": "/",
            "value": {
                "thingId": self.thing_id,
                "policyId": f"{self.org_name}:policy",
                "definition": "https://raw.githubusercontent.com/bernar0507/Eclipse-Ditto-MQTT-iWatch/main/iwatch/wot/iwatch.tm.jsonld",
                "attributes": {
                    "heart_rate": iwatch_data['heart_rate'],
                    "timestamp": iwatch_data['timestamp'],
                    "longitude": iwatch_data['longitude'],
                    "latitude": iwatch_data['latitude']
                }
            }
        }
        ditto_data_str = json.dumps(ditto_data)
        self.client.publish(self.topic, payload=ditto_data_str)
        print(ditto_data)
        print("Data sent to Ditto: " + json.dumps(ditto_data))

    def start(self):
        self.client.connect(self.broker_ip, self.broker_port, 60)
        self.client.loop_start()
        while True:
            iwatch_data = next(self.simulator.generate_data())
            self.send_data_to_ditto(iwatch_data)
            time.sleep(1)


if __name__ == '__main__':
    MQTT_BROKER_PORT = 8883
    THING_ID = f"org.Iotp2c:{sys.argv[1]}" if len(sys.argv) > 1 else "org.Iotp2c:iwatch"
    MQTT_TOPIC = f"{THING_ID}/things/twin/commands/modify"
    CONFIG_PATH = "config/iwatch_config.yaml"
    broker_ip = socket.gethostbyname("mosquitto")
    publisher = MQTTPublisher(CONFIG_PATH, broker_ip, MQTT_BROKER_PORT, THING_ID, MQTT_TOPIC, 'ditto', 'ditto')
    publisher.start()
