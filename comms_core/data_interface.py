# data_interface.py

# The goal of this class is to provide a common interface.
# The class should have easy ways to assign values into the class, and then also get values
# When a value is added, it can optionally also be given a remove time, meaning that after a certain duration the value is "gone"
# By default the value will never be removed, but a parameter can be given to set a time limit
# The class should also be able to convert a dictionary into itself
# It should also be able to cleanly append a dictionary to itself and update its variables accordingly
# The class should also be able to convert itself into a dictionary

import time
from typing import Any, Dict

# A small helper class so each value can have a timestamp
class DataObject:

    def __init__(self, data = None, *, timeout = None, timestamp = None):
        self.set_data(data, timeout, timestamp)

    def __eq__(self, other: object) -> bool:
        return self.data == other.data

    def __floordiv__(self, data):
        self.set_data(data)
        return self

    def set_data(self, data, timeout = None, timestamp = None):
        self.data = data
        self.timestamp = timestamp
        if self.timestamp == None:
            self.timestamp = time.time()
        self.timeout = timeout

    def get_data(self):
        if self.timeout is not None and time.time() - self.timestamp > self.timeout:
            return None
        return self.data

    def get_timestamp(self):
        return self.timestamp
    
    def __str__(self) -> str:
        return f'Data: {self.data} | Timestamp: {self.timestamp}'
    
    def __repr__(self) -> str:
        return str(self)
    
class Interface:

    local_variables = [
        'interface_local_data',
        'interface_local_timestamp',
        'default_remove_time'
    ]

    def __init__(self, default_remove_time = None):
        self.default_remove_time = default_remove_time
        self.interface_local_data : Dict[str, DataObject] = {}
        self.interface_local_timestamp = time.time()

    def change_default_remove_time(self, remove_time):
        self.default_remove_time = remove_time
        for key in self.interface_local_data:
            self.set_remove_time(key, remove_time)

    def set_remove_time(self, key, remove_time):
        self.interface_local_data[key].timeout = remove_time

    def __setattr__(self, name: str, value: Any) -> None:
        if name in Interface.local_variables:
            return super().__setattr__(name, value)
        if name in self.interface_local_data:
            self.interface_local_data[name] // value
        else:
            self.interface_local_data[name] = DataObject(value, timeout = self.default_remove_time)
        self.interface_local_timestamp = time.time()

    def __getattr__(self, name: str) -> Any:
        if name in Interface.local_variables:
            return super().__getattr__(name)
        if name not in self.interface_local_data:
            return None
        return self.interface_local_data[name].get_data()
    
    def __delattr__(self, name: str) -> None:
        if name in self.interface_local_data:
            del self.interface_local_data[name]

    def __add__(self, other):
        if isinstance(other, dict):
            self.from_dict(other)
        if isinstance(other, Interface):
            self.from_interface(other)
        return self

    def __getitem__(self, name: str) -> Any:
        return self.__getattr__(name)
    
    def __setitem__(self, name: str, value: Any) -> None:
        self.__setattr__(name, value)

    def __delitem__(self, name: str) -> None:
        self.__delattr__(name)

    def __contains__(self, name: str) -> bool:
        return name in self.interface_local_data
    
    def __iter__(self):
        return iter(self.interface_local_data)
    
    def __len__(self):
        return len(self.interface_local_data)
    
    def __str__(self):
        return f'Interface: Last Update: {self.interface_local_timestamp}\n' + str(self.to_dict_with_timestamps())
    
    def __repr__(self) -> str:
        return str(self)
    
    def to_dict(self):
        return {key: self.interface_local_data[key].get_data() for key in self.interface_local_data}
    
    def to_dict_with_timestamps(self):
        return {key: (self.interface_local_data[key].get_data(), self.interface_local_data[key].get_timestamp()) for key in self.interface_local_data}
    
    def from_dict(self, data: Dict[str, Any]):
        for key in data:
            self.interface_local_data[key] = DataObject(data[key], timeout = self.default_remove_time)
        self.interface_local_timestamp = time.time()

    def from_dict_with_timestamps(self, data: Dict[str, tuple]):
        for key in data:
            self.interface_local_data[key] = DataObject(data[key][0], timeout = self.default_remove_time, timestamp = data[key][1])
        self.interface_local_timestamp = time.time()

    def from_interface(self, other):
        self.from_dict_with_timestamps(other.to_dict_with_timestamps())
    
if __name__ == '__main__':
    interface = Interface()
    interfaceA = Interface()
    interface.a = 5
    interfaceA.b = 10
    print(interface['a'])
    print(interface + interfaceA)
    interface += interfaceA
    # print(interface)