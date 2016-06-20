import select
import threading
from itertools import filterfalse
from typing import Callable, List, Tuple
from .. import data, globals, utils


class SocketsThread(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._socketConnections = []  # type: List[data.Socket]
    
    @property
    def socketConnections(self) -> Tuple['data.Socket', ...]:
        return tuple(self._socketConnections)
    
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

    def register(self, socketConn: 'data.Socket') -> None:
        self._socketConnections.append(socketConn)
    
    def process(self):
        isActive = lambda s: s.isConnected  # type: Callable[[data.Socket], bool]
        try:
            for socketConnection in filterfalse(
                    isActive, self._socketConnections):  # --type: Socket
                socketConnection.connect()
        except:
            utils.logException()
        for socketConnection in filter(isActive, self._socketConnections):  # --type: data.Socket
            socketConnection.queueMessages()
        connections = list(filter(isActive, self._socketConnections))  # type: List[data.Socket]
        if connections:
            read, write, exceptional = select.select(
                connections, connections, connections,
                0.01)  # type: List[data.Socket], List[data.Socket], List[data.Socket]
            for socketConnection in read:  # --type: Socket
                socketConnection.read()
            for socketConnection in write:  # --type: Socket
                socketConnection.flushWrite()
        for socketConnection in filter(isActive, self._socketConnections):  # --type: data.Socket
            socketConnection.sendPing()
    
    def terminate(self):
        for socketConnection in self._socketConnections:  # --type: data.Socket
            socketConnection.disconnect()
