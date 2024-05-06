import socket
import threading
from model import User
from db import session
from typing import List, Callable

HOST: str = '127.0.0.1'
PORT: int = 1234


class Commands:
    @staticmethod
    def login(client: socket.socket, nicknames: List[str], clients: List[socket.socket],
              broadcast: Callable[[str], None]) -> None:
        client.send('Username: '.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        client.send('Password: '.encode('utf-8'))
        password = client.recv(1024).decode('utf-8')
        user = session.query(User).filter_by(name=username).one_or_none()
        if not user:
            client.send(f'[SERVER]: Username does not exist'.encode('utf-8'))
            client.close()
        elif username in nicknames:
            client.send(f'LOGGED [SERVER]: You are already logged in'.encode('utf-8'))
            client.close()
        elif user.is_banned:
            client.send(f'BANNED [SERVER]: You have been banned from the chat'.encode('utf-8'))
            client.close()
        elif not user.check_password(password):
            client.send(f'INCORRECT PASSWORD'.encode('utf-8'))
            client.close()
        else:
            clients.append(client)
            nicknames.append(username)
            print(clients, nicknames)
            broadcast(f'[SERVER]: {username} joined the chat')

    @staticmethod
    def register(client: socket.socket, nicknames: List[str], clients: List[socket.socket],
                 broadcast: Callable[[str], None]) -> None:
        client.send('Username: '.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        client.send('Password: '.encode('utf-8'))
        password = client.recv(1024).decode('utf-8')
        try:
            user = session.query(User).filter_by(name=username).one_or_none()
            if not user:
                if username == 'admin':
                    user = User(name=username, is_admin=True)
                else:
                    user = User(name=username)
                user.set_password(password)
                session.add(user)
                session.commit()
                clients.append(client)
                nicknames.append(username)
                broadcast(f'[SERVER]: {username} joined the chat')
            else:
                client.send(
                    f"[SERVER]: This user existing in database you can't register with this username".encode('utf-8'))
                client.close()
        except:
            client.send(
                f"[SERVER]: This user existing in database you can't register with this username".encode('utf-8'))
            client.close()

    @staticmethod
    def kick(client, message: str, nicknames: List[str], clients: List[socket.socket],
             broadcast: Callable[[str], None]) -> None:
        if nicknames[clients.index(client)] == 'admin':
            name_to_kick = message[5:]
            if name_to_kick in nicknames and name_to_kick != 'admin':
                name_index = nicknames.index(name_to_kick)
                client_to_kick = clients[name_index]
                clients.remove(client_to_kick)
                client_to_kick.send(f'[SERVER]: You were kicked from the chat by the admin'.encode('utf-8'))
                client_to_kick.close()
                nicknames.remove(name_to_kick)
                broadcast(f'[SERVER]: {name_to_kick} has been kicked from the chat by the admin')
        else:
            client.send(f'[SERVER]: Command was refused'.encode('utf-8'))

    @staticmethod
    def ban(client: socket.socket, message: str, nicknames, clients, broadcast: Callable[[str], None]) -> None:
        if nicknames[clients.index(client)] == 'admin':
            name_to_ban = message[4:]
            if name_to_ban in nicknames and name_to_ban != 'admin':
                user_to_ban = session.query(User).filter_by(name=name_to_ban).one_or_none()
                if not user_to_ban:
                    client.send(f"[SERVER]: User doesn't exit you can't ban him".encode('utf-8'))
                if user_to_ban.is_banned is False:
                    user_to_ban.is_banned = True
                    session.commit()
                    name_index = nicknames.index(name_to_ban)
                    client_to_ban = clients[name_index]
                    client_to_ban.send(f'BANNED [SERVER]: You have been banned by admin.'.encode('utf-8'))
                    client_to_ban.close()
                    nicknames.remove(name_to_ban)
                    clients.remove(client_to_ban)
                    broadcast(f'[SERVER]: {name_to_ban} has been banned from the chat by the admin')
                else:
                    client.send(f'[SERVER]: User is already banned.'.encode('utf-8'))
            else:
                client.send(f"[SERVER]: This user does not exist or he isn't logged".encode('utf-8'))
        else:
            client.send(f"[SERVER]: Command was refused".encode('utf-8'))

    @staticmethod
    def quit(client: socket.socket, message, nicknames: List[str], clients: List[socket.socket],
             broadcast: Callable[[str], None]) -> None:
        nickname = message[5:]
        clients.remove(client)
        client.send(f'[SERVER]: You disconnected from the chat'.encode('utf-8'))
        client.close()
        nicknames.remove(nickname)
        broadcast(f'[SERVER]: {nickname} has been quit from the chat')


class Server:
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()
        self.nicknames: List[str] = []
        self.clients: List[socket.socket] = []
        self.commands = Commands()
        print(f'Server listening on {HOST}:{PORT}')

    def broadcast(self, message: str) -> None:
        for client in self.clients:
            client.send(message.encode('utf-8'))

    def handle(self, client: socket.socket) -> None:
        message = client.recv(2048).decode('utf-8')
        if message == 'login':
            self.commands.login(client=client, nicknames=self.nicknames, clients=self.clients, broadcast=self.broadcast)
        elif message == 'register':
            self.commands.register(client=client, nicknames=self.nicknames, clients=self.clients,
                                   broadcast=self.broadcast)
        else:
            client.send(f'[SERVER]: Invalid value'.encode('utf-8'))
            client.close()
            self.clients.remove(client)
        while True:
            try:
                message = client.recv(2048).decode('utf-8')
                if message.startswith('KICK'):
                    self.commands.kick(client=client, message=message, nicknames=self.nicknames, clients=self.clients,
                                       broadcast=self.broadcast)
                elif message.startswith('BAN'):
                    self.commands.ban(client=client, message=message, nicknames=self.nicknames, clients=self.clients,
                                      broadcast=self.broadcast)
                elif message.startswith('QUIT'):
                    self.commands.quit(client=client, message=message, nicknames=self.nicknames, clients=self.clients,
                                       broadcast=self.broadcast)
                else:
                    self.broadcast(message=message)
            except:
                if client in self.clients:
                    index = self.clients.index(client)
                    self.clients.remove(client)
                    client.close()
                    nickname = self.nicknames[index]
                    self.nicknames.remove(nickname)
                    break

    def run(self) -> None:
        while True:
            try:
                client, address = self.server.accept()
                print(f'Accepted connection from {address[0]}:{address[1]}')
                threading.Thread(target=self.handle, args=(client,)).start()
            except:
                continue


if __name__ == '__main__':
    server = Server()
    server.run()
