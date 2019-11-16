import _thread
import time

import zmq
from subscriber import Subscriber

subscribers = {}
TIMEOUT = 60

def rcv_signal(unique=None, publisher=None):
    while True:
        msg = unique.recv_json()
        if "action" in msg:
            if msg["action"] == "announcement":
                subscriber = Subscriber(msg["state"], msg["id"], msg["path"])
                if subscriber not in subscribers:
                    subscribers[subscriber] = int(time.time())
                msg = {"status": "ok"}
                unique.send_json(msg)

            elif msg["action"] == "done":
                path = msg["path"]
                msg = {"action": "stop", "file": path}
                publisher.send_json(msg)

                msg = {"status": "ok"}
                unique.send_json(msg)
            else:
                msg = {"status": "ok"}
                unique.send_json(msg)


def main():
    context = zmq.Context()

    # Socket to talk to clients
    publisher = context.socket(zmq.PUB)
    # set SNDHWM, so we don't drop messages for slow subscribers
    publisher.sndhwm = 1100000
    publisher.bind('tcp://*:5561')

    # Socket to receive signals
    syncservice = context.socket(zmq.REP)
    syncservice.bind('tcp://*:5562')

    _thread.start_new_thread(rcv_signal, (syncservice, publisher,))

    while True:
        opcao = input(
            """\n\nEscolha uma opção
            (1) Ver status
            (2) Quebrar arquivo de senha
            (3) Send msg
            :""")
        if opcao == '1':
            agora = int(time.time())
            for subscriber in list(subscribers):
                if agora - subscribers[subscriber] > TIMEOUT:
                    subscribers.pop(subscriber)
                else:
                    print(subscriber)
        elif opcao == '2':
            msg = {"action": "crack"}
            path = input("file path: ")
            f = open(path, "rb")
            msg["file"] = f.read().decode("utf-8")
            publisher.send_json(msg)

        elif opcao == '3':
            msg = {"msg": input("msg: ")}
            publisher.send_json(msg)


if __name__ == '__main__':
    main()


