import threading
import os
import time

def inicia_programa(nome_arquivo):
    os.system('python3 {}'.format(nome_arquivo))

if __name__ == "__main__":

    arquivos = ['main.py','interface.py']

    processos = []
    for arquivo in arquivos:
        processos.append(threading.Thread(target=inicia_programa, args=(arquivo,)))
        # Ex: adicionar o porcesso `threading.Thread(target=inicia_programa, args=('x.py',))`

    for processo in processos:
        processo.start()
        time.sleep(0.5)