import logging
import os

class Logger:

    def __init__(self, name: str, level: int = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Check if the logger already has handlers (to avoid adding duplicate handlers)
        if not self.logger.hasHandlers():
            # Create and configure the stream handler (console output)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            stream_handler.setLevel(logging.WARNING)  # Only log warnings and above to console
            self.logger.addHandler(stream_handler)

            # Create and configure the file handler
            log_directory = 'logs'
            os.makedirs(log_directory, exist_ok=True)
            file_handler = logging.FileHandler(f'{log_directory}/{name}.log', mode="w")
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            file_handler.setLevel(logging.DEBUG)  # Log all messages to the file
            self.logger.addHandler(file_handler)

    def log(self, message: str, level: int = logging.DEBUG):
        self.logger.log(level, message)

    def debug(self, message: str):
        self.log(message, logging.DEBUG)

    def info(self, message: str):
        self.log(message, logging.INFO)

    def warning(self, message: str):
        self.log(message, logging.WARNING)

    def error(self, message: str):
        self.log(message, logging.ERROR)

    def critical(self, message: str):
        self.log(message, logging.CRITICAL)
