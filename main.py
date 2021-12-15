from controller.controller import Controller
from network.signal_handler import register_exit_signal

from utils.log import GameLog

GameLog.load_config()

if __name__ == "__main__":
    register_exit_signal()
    controller = Controller()
    controller.loop()


