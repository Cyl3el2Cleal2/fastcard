from aio_pika import connect_robust
from aio_pika.patterns import Master
import os

RMQ_USER = os.getenv('RMQ_USER', 'guest')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD', 'guest')
RMQ_HOST = os.getenv('RMQ_HOST', 'localhost')


class MQ:
    master = None

    def __init__(self):
        """ Constructor.
        """
        if MQ.master is None:
            MQ.master = self
        else:
            raise Exception("You cannot create another MQ class")

    @staticmethod
    async def create_master():
        try:
            connection = await connect_robust(f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}/")

            channel = await connection.channel()
            MQ.master = Master(channel)
            print("RABBITMQ is connected")
            return MQ.master
        except:
            raise Exception('Can not connect to RABBITMQ')

    @staticmethod
    def get_master():
        if not MQ.master:
            MQ()
        return MQ.master
