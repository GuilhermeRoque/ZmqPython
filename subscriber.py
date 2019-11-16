import _thread
import pprint
import time

import zmq
import random


class Subscriber:
    def __init__(self, state="idle", id=0, path=""):
        self.path = path
        self.state = state
        self.id = id

    def __str__(self) -> str:
        return "ID: " + str(self.id) + " STATE: " + self.state + " FILE: " + self.path

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __hash__(self) -> int:
        return hash(self.id)


def keepalive(socket=None, subscriber=None):
    while True:
        msg = {"action": "announcement", "state": subscriber.path, "id": subscriber.id, "path": subscriber.path}
        socket.send_json(msg)
        msg = socket.recv_json()
        pprint.pprint(msg)
        time.sleep(10)


def main():
    subscriber_id = random.randrange(1, 10)
    print("I am subscriber #%s" % subscriber_id)

    context = zmq.Context()

    # subscribe to all messages of the publisher socket
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://127.0.0.1:5561")
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    time.sleep(1)

    # sincronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect("tcp://127.0.0.1:5562")

    s = Subscriber()
    _thread.start_new_thread(keepalive, (syncclient, s,))

    while True:
        msg = subscriber.recv_json()
        pprint.pprint(msg)
        result = {"action": "none", "state": "idle"}
        syncclient.send_json(result)
        msg = syncclient.recv_json()
        pprint.pprint(msg)


if __name__ == '__main__':
    main()
