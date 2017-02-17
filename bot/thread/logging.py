from .. import utils
from typing import Tuple, IO
import bot.globals
import queue
import threading


class Logging(threading.Thread):
    def __init__(self, **kwargs) -> None:
        threading.Thread.__init__(self, **kwargs)
        self.queue: queue.Queue[Tuple[str, str]] = queue.Queue()

    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=utils.now(), name=self.__class__.__name__))
        try:
            while bot.globals.running or self.queue.qsize():
                self.process()
        finally:
            print('{time} Ending {name}'.format(
                time=utils.now(), name=self.__class__.__name__))
            bot.globals.running = False
    
    def log(self,
            file: str,
            log: str) -> None:
        self.queue.put((file, log))
    
    def process(self) -> None:
        filename: str
        log: str
        file: IO[str]
        filename, log = self.queue.get()
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(log)
