import socket
import time
from queue import Queue
from threading import Thread 

class Remote():

    def __init__(self):
        self.__retryInterval = 2

    def addToQueue(self, message):
        self.__msgQueue.put(message)

    def startRemote(self):
        self.__sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__addr = ('adsb-remote', 49001)
        self.__sck.connect(self.__addr)
        self.__msgQueue = Queue()
        self.__t1 = Thread(target = self.__sendToRemote, args =(self.__msgQueue, ), daemon=True) 
        self.__t1.start() 
    
    def __sendToRemote(self, q):
        while True:
            adsbRec = q.get()   # block, wait for ads-b data
            msg = bytes(adsbRec, 'utf-8')

            retry = True
            while (retry):
                try:
                    self.__sck.send(msg)
                except ConnectionRefusedError:
                    time.sleep(self.__retryInterval)
                except:
                    time.sleep(self.__retryInterval)
                else:
                    retry = False
                
