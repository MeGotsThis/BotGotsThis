import select
import threading
from datetime import datetime
from itertools import filterfalse
from .. import globals, utils


class SocketsThread(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._socketConnections = []
    
    @property
    def socketConnections(self):
        return self._socketConnections
    
    def run(self):
        print('{time} Starting {name}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__))
        
        while globals.running:
            try:
                self.process()
            except:
                utils.logException()
        self.terminate()
        
        print('{time} Ending {name}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__))
    
    def register(self, socketConn):
        self._socketConnections.append(socketConn)
    
    def process(self):
        isActive = lambda s: s.socket
        try:
            for socketConnection in filterfalse(isActive, self._socketConnections):
                socketConnection.connect()
        except:
            utils.logException()
        for socketConnection in filter(isActive, self._socketConnections):
            socketConnection.queueMessages()
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
    
    def terminate(self):
        for socketConnection in self._socketConnections:
            socketConnection.disconnect()
