import _thread
import pprint
import subprocess
import threading
import time
import zmq
import random


class Subscriber:
    def __init__(self, state="idle", id=0, file="", last_ka= 0):
        self.file = file
        self.state = state
        self.id = id
        self.last_ka = last_ka

    def __str__(self) -> str:
        if self.state == "idle":
            return "id: " + str(self.id) + " state: " + self.state
        return "id: " + str(self.id) + " state: " + self.state + " file: " + self.file

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __hash__(self) -> int:
        return hash(self.id)


def keepalive(socket=None, subscriber=None):
    while True:
        msg = {"action": "announcement", "state": subscriber.state, "id": subscriber.id, "file": subscriber.file}
        socket.send_json(msg)
        msg = socket.recv_json()
        pprint.pprint(msg)
        time.sleep(10)


def crack(f_name=None, e=None, subscriber=None, socket=None):
    #executa o john
    cmd = "exec john " + f_name
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    while True:
        if e.isSet():
            p.kill()
            subscriber.state = "idle"
            break
        if p.poll() is not None:
            msg = {"action": "done", "file": f_name, "id": subscriber.id, "status": p.returncode}
            socket.send_json(msg)
            msg = socket.recv_json()
            pprint.pprint(msg)
            subscriber.state = "idle"
            break
        time.sleep(5)


def main():
    subscriber_id = random.randrange(1, 1000)
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

    s = Subscriber(id=subscriber_id)
    _thread.start_new_thread(keepalive, (syncclient, s,))
    e = threading.Event()

    while True:
        msg = subscriber.recv_json()
        if "action" in msg:
            if msg["action"] == "crack" and s.state == "idle":
                #cria o arquivo
                f_name = msg["f_name"]
                s.file = f_name
                f = open(f_name, "a+")
                f.write(msg["file"])
                f.close()
                _thread.start_new_thread(crack, (f_name, e, s, syncclient,))

                #muda o estado do subscriber
                s.state = "working"
            elif msg["action"] == "stop" and s.state == "working":
                e.set()
                s.state = "idle"
                s.file = ""


if __name__ == '__main__':
    main()
