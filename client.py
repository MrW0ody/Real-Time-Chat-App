import socket
import sys
import threading
import getpass


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.username: str | None = None
        self.host: str = host
        self.port: int = port
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected: bool = False

    def connect(self) -> None:
        self.client.connect((self.host, self.port))
        self.connected = True

    def send_message(self, message: str) -> None:
        try:
            if self.connected:
                self.client.send(message.encode('utf-8'))
        except:
            print("Not connected to server.")
            sys.exit()

    def close_message(self, message: str, start_message: str | None = None) -> bool:
        if start_message:
            if start_message == 'BANNED ':
                print(message[len(start_message):])
                self.connected = False
                self.client.close()
            else:
                print(message[len(start_message):])
                self.connected = False
                self.client.close()
                return False
        else:
            print(message)
            self.connected = False
            self.client.close()
            return False

    def receive_messages(self) -> bool:
        while self.connected:
            try:
                message = self.client.recv(2048).decode('utf-8')
                if message.startswith('LOGGED '):
                    self.close_message(message=message, start_message='LOGGED ')
                elif message.startswith('BANNED '):
                    self.close_message(message=message, start_message='BANNED ')
                elif message.startswith('INCORRECT PASSWORD'):
                    self.close_message(message=message)
                elif message:
                    print(message)
            except:
                print(f'An error occurred!')
                self.client.close()
                return False

    def send_messages(self) -> None:
        while self.connected:
            message = f'{self.username}: {input("")}'
            if message[len(self.username) + 2:].startswith('/'):
                if message[len(self.username) + 2:].startswith('/kick'):
                    message = f'KICK {message[len(self.username) + 2 + 6:]}'
                    self.send_message(message=message)
                elif message[len(self.username) + 2:].startswith('/ban'):
                    message = f'BAN {message[len(self.username) + 2 + 5:]}'
                    self.send_message(message=message)
                elif message[len(self.username) + 2:].startswith('/quit'):
                    message = f'QUIT {self.username}'
                    self.send_message(message=message)
            elif message:
                self.send_message(message=message)
            else:
                continue

    def run(self):
        try:
            self.connect()
            command = input('Enter login or register: ')
            self.send_message(command)
            message = self.client.recv(2048).decode('utf-8')
            if message:
                self.username = input(message)
                self.send_message(message=self.username)
                message = self.client.recv(2048).decode('utf-8')
                if message:
                    password = getpass.getpass(message)
                    self.send_message(message=password)
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()
            send_thread = threading.Thread(target=self.send_messages)
            send_thread.start()
            receive_thread.join()
            send_thread.join()
            self.client.close()
        except:
            print(f'An error occurred!')
            self.client.close()
            sys.exit()


if __name__ == '__main__':
    client = Client('127.0.0.1', 1234)
    client.run()
