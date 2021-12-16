import json
import logging
import socket
import threading

logger = logging.getLogger("game-socket")
CONNECTION_TIMEOUT = 0.1


class ReceiverWorker(threading.Thread):
    def __init__(self, connection, address, received_queue, disconnect_callback):
        threading.Thread.__init__(self)
        self._connection_ = connection
        self._address_ = address
        self._received_queue_ = received_queue
        self._disconnect_callback_ = disconnect_callback
        self._shutdown_flag_ = threading.Event()

    def run(self):
        while not self._shutdown_flag_.is_set():
            try:
                data_size = int.from_bytes(self._connection_.recv(4), 'big', signed=True)
                if not data_size:  # Close connection
                    self._shutdown_flag_.set()
                    break
                raw_packet = self._connection_.recv(data_size)
                packet = json.loads(raw_packet.decode('utf-8'))
                packet['__client_address__'] = self._address_
                self._received_queue_.put(packet)
                logger.info(
                    "Connection to {}:{} received a packet {}".format(self._address_[0], self._address_[1], packet))
            except socket.timeout:
                pass
            except ConnectionResetError:
                logger.warning("Connection to {}:{} closed by client".format(self._address_[0], self._address_[1]))
                self.set_shutdown_flag()  # Close the receiver connection

        self._connection_.close()
        self._disconnect_callback_(self._address_)
        logger.warning('Close connection to {}:{}'.format(self._address_[0], self._address_[1]))

    def set_shutdown_flag(self):
        self._shutdown_flag_.set()

    def get_connection(self):
        if self._shutdown_flag_.is_set():
            return None
        return self._connection_


class ConnectionListener(threading.Thread):
    def __init__(self, game_socket, received_queue, receiver_list, disconnect_callback):
        threading.Thread.__init__(self)
        self._socket_ = game_socket
        self._received_queue_ = received_queue
        self._receiver_list_ = receiver_list
        self._disconnect_callback_ = disconnect_callback
        self._shutdown_flag_ = threading.Event()

    def run(self):
        self._socket_.listen()
        while not self._shutdown_flag_.is_set():
            try:
                connection, address = self._socket_.accept()
                connection.settimeout(CONNECTION_TIMEOUT)
                logger.info('Open Connection with {}:{}'.format(address[0], address[1]))
                receiver = ReceiverWorker(connection, address, self._received_queue_,
                                          disconnect_callback=self._disconnect_callback_)
                self._receiver_list_[address] = receiver
                receiver.start()
            except socket.timeout:
                pass
        self._socket_.close()
        logger.warning("Close connection listener Thread")

    def set_shutdown_flag(self):
        self._shutdown_flag_.set()
