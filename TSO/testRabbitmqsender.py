import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

exchange_name = 'machine_state_updates'
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)

message = {"status": "RUNNING", "machine": "MC001"}
channel.basic_publish(
    exchange=exchange_name,
    routing_key='',
    body=json.dumps(message)
)

print("📤 Sent test message")
connection.close()