from comms_core import Server

def callback(data, addr):
    print(f'Received: {data}\n>>> ', end='')

if __name__ == '__main__':
    server = Server(default_callback=callback)
    server.start()
    while True:
        to_send = input('>>> ')
        if to_send == 'quit':
            break
        server.send(to_send)
    server.stop()
