from Models.rabbitmq_subscriber import Subscriber


def callback(ch, method, properties, body):
    print(" [x] %r" % body.decode('utf8'))


subscriber = Subscriber('#')

subscriber.consume(callback)
