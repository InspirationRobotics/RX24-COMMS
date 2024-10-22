import time
import socket
from typing import List, Dict, Callable, Union
from threading import Thread, Lock

from .logger import Logger

class Server(Logger):

    def __init__(self, *, default_callback: Callable = None):
        super().__init__('Server')
        self.local_server_address = ('0.0.0.0', 37564)
        self.default_callback = default_callback

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.local_server_address)
        self.server_socket.listen(5)
        self.server_socket.settimeout(0.05)

        self.connections: Dict[tuple, Dict] = {}
        self.lock = Lock()
        self.active = False
        self.accept_thread = Thread(target=self._accept_connections)
        
    def __del__(self):
        self.stop()
        self.server_socket.close()

    def _accept_connections(self):
        while self.active:
            try:
                conn, addr = self.server_socket.accept()
                conn.settimeout(0.05)
                with self.lock:
                    self.connections[addr] = {
                        'conn': conn,
                        'ip': addr[0],
                        'callback': self.default_callback,
                        'data': None,
                        'thread': Thread(target=self._handle_client, args=(conn, addr)),
                        'send_queue': [],
                        'send_lock': Lock(),
                        'read_lock': Lock(),
                    }
                    self.connections[addr]['thread'].start()
                    self.log(f'Connected to {addr}')
            except socket.timeout:
                continue

    def _kill_client(self, addr):
        self.warning(f'Lost connection to {addr}')
        try:
            self.connections[addr]['conn'].shutdown(socket.SHUT_RDWR)
            self.connections[addr]['conn'].close()
        except Exception as e:
            pass
        del self.connections[addr]

    def _handle_client(self, conn, addr):
        while self.active:
            data = self._read_data(conn, addr)
            if data:
                self.log(f'Received: {data} from {addr}')
                with self.lock:
                    if "Client: " not in data:
                        self.connections[addr]['data'] = data
                        if self.connections[addr]['callback']:
                            self.connections[addr]['callback'](data, addr)
            self._send_data(conn, addr)
            time.sleep(0.01)

    def _read_data(self, conn : socket.socket, addr):
        try:
            data = conn.recv(4096).decode()
            return data
        except socket.timeout:
            return None
        except ConnectionResetError:
            with self.lock:
                self._kill_client(addr)
            return None
        

    def _send_data(self, conn : socket.socket, addr):
        with self.lock:
            if addr not in self.connections:
                return
            with self.connections[addr]['send_lock']:
                for data in self.connections[addr]['send_queue']:
                    try:
                        data : str
                        conn.send(data.encode())
                        self.log(f'Sent: {data} to {addr}')
                    except ConnectionResetError:
                        with self.lock:
                            self._kill_client(addr)
                        break
                self.connections[addr]['send_queue'] = []

    def start(self):
        self.active = True
        self.accept_thread.start()

    def stop(self):
        self.log("Shutting down server")
        self.active = False
        self.accept_thread.join()
        with self.lock:
            for addr, info in self.connections.items():
                try:
                    info['conn'].shutdown(socket.SHUT_RDWR)
                    info['conn'].close()
                except:
                    continue
            self.connections.clear()

    def send(self, data: str, addr : Union[tuple, str] = None):
        if addr is None:
            with self.lock:
                if len(self.connections) == 0:
                    return
                addr = list(self.connections.keys())[0]
        with self.lock:
            if isinstance(addr, tuple):
                if addr in self.connections:
                    with self.connections[addr]['send_lock']:
                        self.connections[addr]['send_queue'].append(data)
            if isinstance(addr, str):
                for address, info in self.connections.items():
                    if info['ip'] == addr:
                        with self.connections[address]['send_lock']:
                            self.connections[address]['send_queue'].append(data)

    def set_callback(self, addr, callback: Callable):
        with self.lock:
            if addr in self.connections:
                self.connections[addr]['callback'] = callback

    def get_data(self, ip) -> str:
        with self.lock:
            for addr, info in self.connections.items():
                if info["ip"] == ip:
                    with self.connections[addr]['read_lock']:
                        return self.connections[addr]['data']
        return None