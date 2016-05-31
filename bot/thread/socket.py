from .. import config, globals
from datetime import datetime
from itertools import filterfalse
import select
import socket
import threading

class SocketsThread(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._socketConnections = []
    
    @property
    def socketConnections(self):
        return self._socketConnections
    
    def run(self):
        print('{time} Starting {name} {thread}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__,
            thread=self.name))
        
        isActive = lambda s: s.socket
        while globals.running:
            for socketConnection in filterfalse(isActive,
                                                self._socketConnections):
                socketConnection.connect()
            connections = list(filter(isActive, self._socketConnections))
            if connections:
                read, write, exceptional = select.select(
                    connections, connections, connections, 0.01)
                for socketConnection in read:
                    socketConnection.read()
                for socketConnection in write:
                    socketConnection.flushWrite()
            for socketConnection in filter(isActive, self._socketConnections):
                socketConnection.sendPing()
        
        for socketConnection in self._socketConnections:
            socketConnection.cleanup()
        print('{time} Ending {name} {thread}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__,
            thread=self.name))
    
    def register(self, socketConn):
        self._socketConnections.append(socketConn)
