import pika, json, os, time

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")

def publish_event(event: dict):
    for _ in range(5):
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
            ch = conn.channel()
            ch.queue_declare(queue="events", durable=True)
            ch.basic_publish(
                exchange="",
                routing_key="events",
                body=json.dumps(event).encode(),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            conn.close()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Cannot publish event")
