import pika


class Subscriber:
    def __init__(self, listening_route):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'
                                                                       , credentials=pika.PlainCredentials('guest',
                                                                                                           'guest')
                                                                       , heartbeat_interval=600))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='JIM', exchange_type='topic')
        result = self.channel.queue_declare(exclusive=True)

        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange='JIM',
                                queue=self.queue_name,
                                routing_key=listening_route)

    def consume(self, callback):
        self.channel.basic_consume(callback,
                                   queue=self.queue_name,
                                   no_ack=True)

        self.channel.start_consuming()
