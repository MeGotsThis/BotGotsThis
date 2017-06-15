import bot.globals
import select
import threading
from contextlib import suppress
from itertools import filterfalse
from typing import Callable, List
from .. import data, utils


class SocketsThread(threading.Thread):
    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=utils.now(), name=self.__class__.__name__))
        
        while bot.globals.running:
            try:
                self.process()
            except:
                utils.logException()
        self.terminate()
        
        print('{time} Ending {name}'.format(
            time=utils.now(), name=self.__class__.__name__))

    def process(self):
        sockets: List[data.SocketHandler] = list(bot.globals.clusters.values())
        isActive: Callable[[data.SocketHandler], bool] = lambda s: s.isConnected
        socket: data.SocketHandler
        try:
            for socket in filterfalse(isActive, sockets):
                socket.connect()
        except:
            utils.logException()
        for socket in filter(isActive, sockets):
            socket.queueMessages()
        connections: List[data.SocketHandler] = list(filter(isActive, sockets))
        if connections:
            read: List[data.SocketHandler]
            write: List[data.SocketHandler]
            exceptional: List[data.SocketHandler]
            read, write, exceptional = select.select(
                connections, connections, connections, 0.01)
            for socket in filter(isActive, read):
                socket.read()
            for socket in filter(isActive, write):
                socket.flushWrite()
        for socket in filter(isActive, sockets):
            socket.sendPing()
    
    def terminate(self):
        socket: data.SocketHandler
        for socket in bot.globals.clusters.values():
            with suppress(ConnectionError):
                socket.disconnect()
