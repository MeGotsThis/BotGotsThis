import select
import threading
from contextlib import suppress
from itertools import filterfalse
from typing import Callable, List, Tuple
from .. import data, globals, utils


class SocketsThread(threading.Thread):
    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=utils.now(), name=self.__class__.__name__))
        
        while globals.running:
            try:
                self.process()
            except:
                utils.logException()
        self.terminate()
        
        print('{time} Ending {name}'.format(
            time=utils.now(), name=self.__class__.__name__))

    def process(self):
        sockets = list(globals.clusters.values()) # type: List[data.Socket]
        isActive = lambda s: s.isConnected  # type: Callable[[data.Socket], bool]
        try:
            for socket in filterfalse(isActive, sockets):  # --type: Socket
                socket.connect()
        except:
            utils.logException()
        for socket in filter(isActive, sockets):  # --type: data.Socket
            socket.queueMessages()
        connections = list(filter(isActive, sockets))  # type: List[data.Socket]
        if connections:
            read, write, exceptional = select.select(
                connections, connections, connections,
                0.01)  # type: List[data.Socket], List[data.Socket], List[data.Socket]
            for socket in read:  # --type: Socket
                socket.read()
            for socket in write:  # --type: Socket
                socket.flushWrite()
        for socket in filter(isActive, sockets):  # --type: data.Socket
            socket.sendPing()
    
    def terminate(self):
        for socket in globals.clusters.values():  # --type: data.Socket
            with suppress(ConnectionError):
                socket.disconnect()
