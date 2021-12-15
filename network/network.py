from datetime import datetime
import logging
import queue
import socket

from config import SERVER_PORT, SERVER_IP
from network.receiver import ConnectionListener
from network.sender import SenderWorker

logger = logging.getLogger("game-socket")
CONNECTION_LISTENER_TIME_OUT = 0.2


class ServerNetwork:
    _IP_ = SERVER_IP
    _PORT_ = SERVER_PORT

    def __init__(self):
        self._socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_.bind((self._IP_, self._PORT_))
        self._socket_.settimeout(CONNECTION_LISTENER_TIME_OUT)

        self._sender_ = SenderWorker()
        self._sender_.start()

        self._receiver_list_ = {}
        self._received_queue_ = queue.Queue(0)

        logger.info("Server is Listening on {}:{}".format(self._IP_, self._PORT_))
        self._connection_listener_ = ConnectionListener(self._socket_, self._received_queue_, self._receiver_list_)
        self._connection_listener_.start()

    def send(self, packet, address):
        connection = self._receiver_list_[address].get_connection()
        packet = {
            '__time_sent__': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'game': packet
        }
        self._sender_.send(connection, packet)

    def receive(self, max_nums_packets: int):
        result = []
        for i in range(max_nums_packets):
            try:
                packet = self._received_queue_.get(block=False)
                result.append(packet)
            except queue.Empty:
                return result
        return result

    def broadcast(self, packet):
        packet = {
            '__time_sent__': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'game': packet
        }
        for receiver_key in self._receiver_list_:
            connection = self._receiver_list_[receiver_key].get_connection()
            if connection:
                self._sender_.send(connection, packet)
            else:
                del self._receiver_list_[receiver_key]  # TODO FIX

    def safety_closed(self):
        logger.warning('Force to stop. Cleaning all children processes.')
        self._connection_listener_.set_shutdown_flag()
        self._sender_.set_shutdown_flag()
        for receiver_key in self._receiver_list_:
            self._receiver_list_[receiver_key].set_shutdown_flag()
