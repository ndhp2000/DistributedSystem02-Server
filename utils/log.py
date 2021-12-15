import logging

from config import LOGGER

logging.root.setLevel(logging.NOTSET)


class GameLog:

    @staticmethod
    def load_config():
        for log_name, log_dir in LOGGER:
            GameLog.register_logger(log_name, log_dir)

    @staticmethod
    def register_logger(log_name, log_dir=None):
        logger = logging.getLogger(log_name)
        logger.addHandler(GameLog.get_console_handler())
        if log_dir is not None:
            logger.addHandler(GameLog.get_file_handler("{}/{}.log".format(log_dir, log_name)))

    @staticmethod
    def get_console_handler():
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_format = logging.Formatter('%(name)s - %(levelname)s: \n%(message)s\n--------------------')
        c_handler.setFormatter(c_format)
        return c_handler

    @staticmethod
    def get_file_handler(directory):
        f_handler = logging.FileHandler(directory)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: \n%(message)s\n---------------------')
        f_handler.setFormatter(f_format)
        return f_handler
