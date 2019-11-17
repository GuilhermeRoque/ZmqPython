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
TIMEOUT = 60
cfg = ["All5", "All6", "All7", "All8"]
cfg_applied = []
files =[]


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
                    if not len(s.cgf):
                        if len(cfg):
                            s.cgf = cfg.pop(0)
                            cfg_applied.append(s.cgf)
                        else:
                            s.cgf = cfg_applied[random.randrange(0, len(cfg_applied))]

                msg["cfg"] = s.cgf
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
                    if subscribers[count].state == "ocioso":
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
            if f_name not in files:
                files.append(f_name)
            msg["f_name"] = f_name
            msg["file"] = f.read().decode("utf-8")
            publisher.send_json(msg)


if __name__ == '__main__':
    main()


