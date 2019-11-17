import _thread
from datetime import datetime
import random
import socket
import subprocess
import threading
import time
import zmq
import signal
import sys


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class Subscriber:
    def __init__(self, state="ocioso", id=socket.gethostname(), file="", last_ka= 0, cfg=""):
        self.file = file
        self.state = state
        self.id = id
        self.last_ka = last_ka
        self.cgf = cfg

    def __str__(self) -> str:
        if self.state == "ocioso":
            return "host: " + str(self.id) + " state: " + str(self.state) + " config: " + str(self.cgf)
        return "host: " + str(self.id) + " state: " + self.state + " file: " + self.file + " config: " + self.cgf

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __hash__(self) -> int:
        return hash(self.id)


def keepalive(socket=None, subscriber=None):
    while True:
        msg = {"action": "announcement", "state": subscriber.state, "id": subscriber.id, "file": subscriber.file, "cfg": subscriber.cgf}
        socket.send_json(msg)
        msg = socket.recv_json()
        subscriber.cgf = msg["cfg"]
        time.sleep(10)


def crack(f_name=None, e=None, subscriber=None, socket=None):
    print("Começando quebra do arquivo ", f_name)
    #executa o john
    cmd = "exec john -i="+subscriber.cgf + " " + f_name
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        if e.isSet():
            e.clear()
            p.kill()
            subscriber.state = "ocioso"
            print("Arquivo quebrado por terceiro.")
            break
        if p.poll() is not None:
            print("Arquivo quebrado!!")
            subscriber.state = "ocioso"
            cmd = "john --show "+f_name
            p = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            results = p.stdout.decode("utf-8").splitlines()
            if len(results) >= 2:
                results = results[:len(results)-2]
                results = "\n".join(results)
            else:
                results = ""
            msg = {"action": "done", "f_name": f_name, "id": subscriber.id, "status": p.returncode, "results": results, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            socket.send_json(msg)
            socket.recv_json()
            break


def main():
    ipAddr = input("Publisher IP: ")

    context = zmq.Context()


    # subscribe to all messages of the publisher socket
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://" + ipAddr + ":5561")
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    time.sleep(1)
    # sincronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect("tcp://" + ipAddr + ":5562")


    s = Subscriber(id = str(random.randrange(0, 1000)))
    _thread.start_new_thread(keepalive, (syncclient, s,))
    e = threading.Event()
    while True:
        msg = subscriber.recv_json()
        if "action" in msg:
            if msg["action"] == "crack" and s.state == "ocioso":
                #cria o arquivo
                f_name = msg["f_name"]
                s.file = f_name
                f = open(f_name, "w")
                f.write(msg["file"])
                f.close()
                _thread.start_new_thread(crack, (f_name, e, s, syncclient,))

                #muda o estado do subscriber
                s.state = "trabalhando"
            elif msg["action"] == "stop" and s.state == "trabalhando":
                e.set()
                s.state = "ocioso"
                s.file = ""


if __name__ == '__main__':
    main()
