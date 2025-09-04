import pika
import json

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"✅ [Received] Message: {message}")
    except json.JSONDecodeError:
        print(f"⚠️ [Received] Non-JSON message: {body}")

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672)
    )
    channel = connection.channel()

    # ประกาศ exchange (ต้องตรงกับฝั่งส่ง)
    exchange_name = 'machine_state_updates'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)

    # สร้าง queue ชั่วคราว (auto-delete) และ bind กับ exchange
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # bind queue กับ exchange
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print("🎧 Waiting for messages. To exit press CTRL+C")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted. Closing...")
        channel.close()
        connection.close()

if __name__ == "__main__":
    main()
