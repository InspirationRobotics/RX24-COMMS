import time
import socket
from typing import List, Dict, Callable
from threading import Thread, Lock

from .logger import Logger

class Client(Logger):

    def __init__(self, server_address : str, *, callback = None, port = 37564) -> None:
        super().__init__('Client')
        if server_address == 'debug':
            server_address = socket.gethostname()
        self.server_address = (server_address, port)
        self.callback = callback

        self.conn = None
        self.address = None
        self.init = False
        self.data = None

        self.read_thread = Thread(target=self._run, daemon=True)
        self.read_lock = Lock()
        self.send_lock = Lock()
        self.active = False
        self.send_queue : List[str] = []
        

    def __del__(self):
        self.client_socket.close()

    def _init_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(0.05)
            if self.client_socket.connect_ex(self.server_address) != 0:
                self.client_socket.close()
                raise ConnectionRefusedError
            self.init = True
            self.log(f'Connected to {self.server_address}')
            return True
        except socket.timeout:
            return False
        except ConnectionRefusedError:
            self.warning(f'Connection refused by {self.server_address}')
            return False
        except Exception as e:
            return False

    def _run(self):
        while self.active:
            if not self.init:
                if not self._init_connection():
                    time.sleep(5)
                    continue
                self.send(f'Client: {socket.gethostname()}')
            self.receive()
            self._send()
            time.sleep(0.01)

    def start(self):
        self.active = True
        self.read_thread.start()

    def stop(self):
        try:
            self.log("Shutting down client")
            self.active = False
            self.read_thread.join(5)
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
        except:
            pass
    
    def _read_data(self):
        try:
            data = self.client_socket.recv(4096).decode()
        except socket.timeout:
            data = None
        except ConnectionResetError:
            data = None
            self.init = False
            self.warning(f'Lost connection to {self.server_address}')
        return data

    def receive(self):
        if not self.init:
            return
        with self.read_lock:
            data = self._read_data()
            if data:
                self.log(f'Received: {data} from {self.server_address}')
                self.data = data
                if self.callback is not None: 
                    self.callback(data, self.server_address)
    
    def get_data(self) -> str: 
        with self.read_lock:
            return self.data

    def send(self, data : str):
        with self.send_lock:
            self.send_queue.append(data)

    def _send_data(self, data : str):
        try:
            self.client_socket.send(data.encode())
            self.log(f'Sent: {data} to {self.server_address}')
        except ConnectionResetError:
            self.init = False
        except BrokenPipeError:
            self.init = False

    def _send(self):
        if not self.init:
            return
        with self.send_lock:
            for data in self.send_queue:
                self._send_data(data)
            self.send_queue = []