from comms_core import Client

def callback(data, addr):
    print(f'Received: {data}\n>>> ', end='')

if __name__ == '__main__':
    client = Client('debug', callback=callback)
    client.start()
    while True:
        to_send = input('>>> ')
        if to_send == 'quit':
            break
        client.send(to_send)
    client.stop()