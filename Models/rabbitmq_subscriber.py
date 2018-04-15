import pika


class Subscriber:
    def __init__(self, listening_route):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'
                                                                       , credentials=pika.PlainCredentials('guest',
                                                                                                           'guest')
                                                                       , heartbeat_interval=600))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='JIM', exchange_type='topic')

        self.listening_route = listening_route

    def consume(self, callback):
        result = self.channel.queue_declare(exclusive=True)

        queue_name = result.method.queue

        self.channel.queue_bind(exchange='JIM',
                                queue=queue_name,
                                routing_key=self.listening_route)

        self.channel.basic_consume(callback,
                                   queue=queue_name,
                                   no_ack=True)

        self.channel.start_consuming()

    def consume_multiple(self, routes, callbacks):
        if len(routes) != len(callbacks):
            raise ValueError('there must be the same number of routes ({0}) and Callbacks({1})'
                             , len(routes), len(callbacks))

        for i in range(len(routes)):
            result = self.channel.queue_declare(exclusive=True)

            queue_name = result.method.queue

            self.channel.queue_bind(exchange='JIM',
                                    queue=queue_name,
                                    routing_key=routes[i])

            self.channel.basic_consume(callbacks[i],
                                       queue=queue_name,
                                       no_ack=True)

        self.channel.start_consuming()
