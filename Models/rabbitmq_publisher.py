import pika


class Publisher:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='JIM', exchange_type='topic')

    def publish(self, route, data):
        self.channel.basic_publish(exchange='JIM', routing_key=route, body=data)
