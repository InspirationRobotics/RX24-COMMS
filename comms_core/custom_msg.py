
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
    def encode(data : dict) -> str:
        message = ''
        for key in data.keys():
            build = f'{key}:{data[key]}<{type(data[key]).__name__}>'
            message += '{' + build + '}*%*'
        return message
    
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
        # Return the key and value
        return key, value


    @staticmethod
    def decode(message : str) -> dict:
        data = {}
        message = message.split('*%*')
        for item in message:
            if item == '':
                continue
            key, value = CustomSocketMessage._process_message(item)
            data[key] = value
        return data