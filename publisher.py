import _thread
import random
import time
import zmq
from subscriber import Subscriber
import signal
import sys


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

subscribers = []
TIMEOUT = 20
cfg = ["All5", "All6", "All7", "All8"]
files = []


def rcv_signal(unique=None, publisher=None):
    while True:
        msg = unique.recv_json()
        if "action" in msg:
            if msg["action"] == "announcement":

                s = Subscriber(msg["state"], msg["id"], msg["file"], int(time.time()), msg["cfg"])
                msg = {"status": "ok"}

                if s in subscribers:
                    subscribers.remove(s)
                else:
                    print("\nNovo trabalhador " + s.id+" online!\n")
                    if not len(s.cfg):
                        if len(cfg):
                            s.cfg = cfg.pop(0)

                msg["cfg"] = s.cfg
                subscribers.append(s)
                unique.send_json(msg)

            elif msg["action"] == "done":
                f_name = msg["f_name"]
                if f_name in files and len(msg["results"]):
                    print("\nArquivo de senha " + f_name + " quebrado!\n")
                    files.remove(f_name)
                    f = open("resultados.txt", "a+")
                    f.write(f_name+"\n")
                    f.write(msg["data"]+"\n")
                    f.write(msg["results"]+"\n\n")
                    f.close()
                    msg = {"action": "stop", "f_name": f_name}
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
            (2) Quebrar arquivo
            (3) Parar quebra de arquivo
            :""")
        if opcao == '1':
            agora = int(time.time())
            ativos = 0
            ociosos = 0
            subscribers_copy = subscribers.copy()
            for count in range(len(subscribers)):
                sub = subscribers[count]
                if agora - sub.last_ka > TIMEOUT:
                    print("\nTrabalhador " + sub.id + " desconectou!\n")
                    subscribers_copy.remove(sub)
                    cfg.append(sub.cfg)
                else:
                    print(sub)
                    if sub.state == "ocioso":
                        ociosos = ociosos + 1
                    else:
                        ativos = ativos + 1
            subscribers.clear()
            subscribers[:] = subscribers_copy[:]
            print("Total online: ", len(subscribers))
            print("Total trabalhando: ", ativos)
            print("Total ociosos: ", ociosos)
        elif opcao == '2':
            msg = {"action": "crack"}
            path = input("file path: ")
            f = open(path, "rb")

            names = path.split("/")
            f_name = names[len(names) - 1]
            if f_name not in files:
                files.append(f_name)
            msg["f_name"] = f_name
            msg["file"] = f.read().decode("utf-8")
            publisher.send_json(msg)
        elif opcao == '3':
            path = input("file: ")
            names = path.split("/")
            f_name = names[len(names) - 1]
            msg = {"action": "stop", "f_name": f_name}
            publisher.send_json(msg)


if __name__ == '__main__':
    main()


