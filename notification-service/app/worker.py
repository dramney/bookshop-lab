import pika, json, os, time
from .senders import send_email, send_push

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")

def callback(ch, method, props, body):
    event = json.loads(body)
    print("[notification] received:", event)
    if event.get("type") == "UserRegistered":
        send_email(event)
    elif event.get("type") == "ItemAddedToCart":
        # for lab: just log
        print("[notification] ItemAddedToCart -> logged")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    time.sleep(5)  # wait for rabbit
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    ch = conn.channel()
    ch.queue_declare(queue="events", durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue="events", on_message_callback=callback)
    print("Notification worker started - waiting for messages")
    ch.start_consuming()

if __name__ == "__main__":
    main()
