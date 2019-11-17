import _thread
import time

import zmq
from subscriber import Subscriber

subscribers = []
TIMEOUT = 60


def rcv_signal(unique=None, publisher=None):
    while True:
        msg = unique.recv_json()
        if "action" in msg:
            if msg["action"] == "announcement":

                s = Subscriber(msg["state"], msg["id"], msg["file"], int(time.time()))
                if s in subscribers:
                    subscribers.remove(s)
                subscribers.append(s)

                msg = {"status": "ok"}
                unique.send_json(msg)

            elif msg["action"] == "done":
                f_name = msg["file"]
                msg = {"action": "stop", "file": f_name}
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
            :""")
        if opcao == '1':
            agora = int(time.time())
            ativos = 0
            ociosos = 0
            subscribers_copy = subscribers.copy()
            for count in range(len(subscribers)):
                if agora - subscribers[count].last_ka > TIMEOUT:
                    subscribers_copy.remove(subscribers[count])
                else:
                    print(subscribers[count])
                    if subscribers[count].state == "idle":
                        ociosos = ociosos + 1
                    else:
                        ativos = ativos + 1
            subscribers.clear()
            subscribers[:] = subscribers_copy[:]
            print("Total trabalhadores: ", len(subscribers))
            print("Total ativos: ", ativos)
            print("Total ociosos: ", ociosos)
        elif opcao == '2':
            msg = {"action": "crack"}
            path = input("file path: ")
            f = open(path, "rb")

            names = path.split("/")
            f_name = names[len(names) - 1]

            msg["f_name"] = f_name
            msg["file"] = f.read().decode("utf-8")
            publisher.send_json(msg)


if __name__ == '__main__':
    main()


