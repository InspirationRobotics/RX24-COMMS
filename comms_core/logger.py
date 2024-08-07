import logging

class Logger:

    def __init__(self, name : str, level : int = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(logging.WARNING)
        self.logger.addHandler(self.handler)
        logging.basicConfig(filename=f'logs/{name}.log', filemode='a', level=logging.DEBUG)

    def log(self, message : str, level : int = logging.DEBUG):
        self.logger.log(level, message)

    def debug(self, message : str):
        self.log(message, logging.DEBUG)

    def info(self, message : str):
        self.log(message, logging.INFO)

    def warning(self, message : str):
        self.log(message, logging.WARNING)

    def error(self, message : str):
        self.log(message, logging.ERROR)

    def critical(self, message : str):
        self.log(message, logging.CRITICAL)
