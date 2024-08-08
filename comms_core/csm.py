from .data_interface import Interface

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
    def encode(data : dict | Interface) -> str:
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
    def _process_tuple_or_list(data : str) -> tuple | list:
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
            value = CustomSocketMessage._process_tuple_or_list(value)
        # Return the key and value
        return key, value


    @staticmethod
    def decode(message : str, *, as_interface = False) -> dict:
        data = {}
        message = message.split('*%*')
        for item in message:
            if item == '':
                continue
            key, value = CustomSocketMessage._process_message(item)
            data[key] = value
        if as_interface:
            data = Interface(data)
        return data