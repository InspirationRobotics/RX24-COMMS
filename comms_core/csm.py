from comms_core.data_interface import Interface
from typing import Union

class CustomSocketMessage:

    def __init__(self):
        pass

    @staticmethod
    def encode_vars(**kwargs) -> str:
        data = {}
        for key in kwargs.keys():
            data[key] = kwargs[key]
        return CustomSocketMessage.encode(data)

    @staticmethod
    def encode(data : Union[dict, Interface]) -> str:
        if isinstance(data, Interface):
            data = data.to_dict()
        message = ''
        for key in data.keys():
            if type(data[key]).__name__ == 'bytes':
                build = f'{key}:{data[key].hex()}<{type(data[key]).__name__}>'
            else:
                build = f'{key}:{data[key]}<{type(data[key]).__name__}>'
            message += '{' + build + '}*%*'
        return message
    
    @staticmethod
    def _process_2D_list(data : str) -> Union[tuple, list]:
        '''
        Sample Data:
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)]
        [1, 2, 3]
        (1.0, 2.0, 3.0)
        '''
        if data[1] not in ['[', '(']:
            return CustomSocketMessage._process_tuple_or_list(data)
        result = []
        # Remove the square brackets
        data = data[1:-1]
        # Split the values
        if data[0] == '(':
            is_tuple = True
        else:
            is_tuple = False
        if is_tuple:
            data = data.split('), ')
            # Add the closing parentheses back
            for i in range(len(data)):
                data[i] += ')' if data[i][-1] != ')' else ''
        else:
            data = data.split('], ')
            # Add the closing brackets back
            for i in range(len(data)):
                data[i] += ']' if data[i][-1] != ']' else ''
        # Convert the values to the correct type
        for val in data:
            result.append(CustomSocketMessage._process_tuple_or_list(val))
        return result

    @staticmethod
    def _process_tuple_or_list(data : str) -> Union[tuple, list]:
        '''Sample data: [1, 2, 3]'''
        # Remove the square brackets or parentheses
        if data[0] == '(':
            is_tuple = True
        else:
            is_tuple = False
        data = data[1:-1]
        # Split the values
        data = data.split(', ')
        # Convert the values to the correct type
        for i in range(len(data)):
            if data[i].isdigit():
                data[i] = int(data[i])
            elif '.' in data[i]:
                data[i] = float(data[i])
            elif data[i] == 'True':
                data[i] = True
            elif data[i] == 'False':
                data[i] = False
        # Return the data
        if is_tuple:
            data = tuple(data)
        return data


    @staticmethod
    def _process_message(data : str) -> tuple:
        '''Sample data: {key:value<type>}'''
        # Remove the curly braces
        data = data[1:-1]
        # Split the key and value/type
        key, value = data.split(':')
        # Split the value and type
        value, value_type = value.split('<')
        # Remove the closing bracket
        value_type = value_type[:-1]
        # Convert the value to the correct type
        if value_type == 'int':
            value = int(value)
        elif value_type == 'float':
            value = float(value)
        elif value_type == 'str':
            value = str(value)
        elif value_type == 'bool':
            value = bool(value)
        elif value_type == 'NoneType':
            value = None
        elif value_type == 'bytes':
            value = bytes.fromhex(value)
        elif value_type == 'list' or value_type == 'tuple':
            value = CustomSocketMessage._process_2D_list(value)
        # Return the key and value
        return key, value


    @staticmethod
    def decode(message : str, *, as_interface = False) -> dict:
        data = {}
        try:
            message = message.split('*%*')
            for item in message:
                if item == '':
                    continue
                key, value = CustomSocketMessage._process_message(item)
                data[key] = value
        except:
            pass
        if as_interface:
                interface = Interface()
                interface.from_dict(data)
                return interface
        return data
    

if __name__ == '__main__':
    data = {
        'key1': [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)],
        'key2': [[1,2,3], [4,5,6], [7,8,9]],
        'key3': (1,0, 2.0),
    }
    message = CustomSocketMessage.encode(data)
    print(message)
    dec = CustomSocketMessage.decode(message)
    print(dec)
