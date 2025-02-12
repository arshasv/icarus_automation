import pika

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "test_queue"

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body='Test message')
    print("Message sent successfully")
    connection.close()
except Exception as e:
    print(f"Failed to connect to RabbitMQ: {e}")
