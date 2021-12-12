import json
import logging
import threading
from queue import Queue, Empty

SENDER_POOLING_TIME = 0.2
logger = logging.getLogger("game-socket")


class SenderWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self._queue_ = Queue(0)  # already thread-safe
        self._shutdown_flag_ = threading.Event()

    def send(self, connection, packet: dict):
        self._queue_.put((connection, json.dumps(packet)))

    def run(self):
        while not self._shutdown_flag_.is_set():
            try:
                connection, packet = self._queue_.get(block=False, timeout=SENDER_POOLING_TIME)
                logger.info("Sender send packet {} ".format(packet))
                packet = packet.encode('utf-8')
                data_size = len(packet)
                packet = data_size.to_bytes(4, 'big', signed=True) + packet
                connection.send(packet)
            except Empty:
                pass
            except OSError:
                logger.warning("Connection closed by client")

        logger.warning("Close Sender Thread")

    def set_shutdown_flag(self):
        self._shutdown_flag_.set()
