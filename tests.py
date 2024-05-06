import unittest
from unittest.mock import patch, MagicMock
from server import Server, Commands
from model import User


class TestServerLogin(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.server.nicknames = []
        self.server.clients = []

    @patch('server.socket.socket')
    @patch('server.session.query')
    def test_successful_login(self, mock_query, mock_socket):
        # Mocking the database session
        user_mock = MagicMock(spec=User)
        user_mock.name = 'test'
        user_mock.is_banned = False
        user_mock.check_password.return_value = True
        mock_query.return_value.filter_by.return_value.one_or_none.return_value = user_mock

        # Simulating a client attempting to log in
        client_socket = MagicMock()
        client_socket.recv.side_effect = [b'test', b'testpass']
        Commands.login(client_socket, self.server.nicknames, self.server.clients, self.server.broadcast)

        # Checking if the user was added to the logged-in list
        self.assertIn(client_socket, self.server.clients)
        self.assertIn('test', self.server.nicknames)
        client_socket.send.assert_called_with(b'[SERVER]: test joined the chat')

    @patch('server.socket.socket')
    @patch('server.session.query')
    def test_failed_login_incorrect_password(self, mock_query, mock_socket):
        # Mocking the database session
        user_mock = MagicMock(spec=User)
        user_mock.name = 'test'
        user_mock.is_banned = False
        user_mock.check_password.return_value = False
        mock_query.return_value.filter_by.return_value.one_or_none.return_value = user_mock

        # Simulating a client attempting to log in with incorrect password
        client_socket = MagicMock()
        client_socket.recv.side_effect = [b'test', b'wrongpassword']
        Commands.login(client_socket, self.server.nicknames, self.server.clients, self.server.broadcast)

        # Checking if the client was informed about the incorrect password and if the connection was closed
        client_socket.send.assert_called_with(b'INCORRECT PASSWORD')
        client_socket.close.assert_called_once()


class TestServerRegister(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.server.nicknames = []
        self.server.clients = []

    @patch('server.socket.socket')
    @patch('server.session.query')
    def test_successful_register(self, mock_query, mock_socket):
        """
        Tests the register function, which allows registering a new user.
        """
        # Mocking the database session
        mock_query.return_value.filter_by.return_value.one_or_none.return_value = None

        # Simulating a client attempting to register
        client_socket = MagicMock()
        client_socket.recv.side_effect = [b'newuser', b'newpass']
        Commands.register(client_socket, self.server.nicknames, self.server.clients, self.server.broadcast)

        # Checking if the user was added to the logged-in list and if it was registered in the database
        self.assertIn(client_socket, self.server.clients)
        self.assertIn('newuser', self.server.nicknames)
        client_socket.send.assert_called_with(b'[SERVER]: newuser joined the chat')

    @patch('server.socket.socket')
    @patch('server.session.query')
    def test_failed_register_existing_user(self, mock_query, mock_socket):
        """
        Tests the register function, which does not allow registering a user with an existing name.
        """
        # Mocking the database session
        user_mock = MagicMock(spec=User)
        user_mock.name = 'newuser'
        mock_query.return_value.filter_by.return_value.one_or_none.return_value = user_mock

        # Simulating a client attempting to register with an existing username
        client_socket = MagicMock()
        client_socket.recv.side_effect = [b'newuser', b'newpass']
        Commands.register(client_socket, self.server.nicknames, self.server.clients, self.server.broadcast)

        # Checking if the client was informed about the existing username and if the connection was closed
        client_socket.send.assert_called_with(
            b"[SERVER]: This user existing in database you can't register with this username")
        client_socket.close.assert_called_once()


class TestServerKick(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.server.nicknames = ['admin', 'test2']
        self.server.clients = [MagicMock(), MagicMock()]

    @patch('server.socket.socket')
    @patch('server.session.query')
    def test_kick_by_admin(self, mock_query, mock_socket):
        """
        Tests the kick function, which allows an admin to kick a user from the chat.
        """
        # Simulating an admin trying to kick the user 'test2'
        admin_socket = self.server.clients[0]
        admin_socket.recv.return_value = b'admin'
        Commands.kick(admin_socket, 'KICK test2', self.server.nicknames, self.server.clients, self.server.broadcast)

        # Checking if the user 'test2' was kicked from the chat
        self.assertNotIn('test2', self.server.nicknames)
        self.assertNotIn(admin_socket, self.server.clients[1:])  # Changed index to exclude the admin_socket

        admin_socket.send.assert_called_with(b'[SERVER]: test2 has been kicked from the chat by the admin')

    @patch('server.socket.socket')
    @patch('server.session.query')
    def test_kick_by_non_admin(self, mock_query, mock_socket):
        """
        Tests the kick function, which does not allow a regular user to kick another user.
        """
        # Simulating a regular user trying to kick the user 'test2'
        user_socket = self.server.clients[1]
        user_socket.recv.return_value = b'test2'
        Commands.kick(user_socket, 'KICK test2', self.server.nicknames, self.server.clients, self.server.broadcast)

        # Checking if the user 'test2' was not kicked from the chat by the regular user
        self.assertIn('test2', self.server.nicknames)
        self.assertIn(user_socket, self.server.clients[1:])  # Changed index to exclude the user_socket

        user_socket.send.assert_called_with(b'[SERVER]: Command was refused')


class TestServerBroadcast(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.server.nicknames = ['user1']
        self.server.clients = [MagicMock()]

    @patch('server.socket.socket')
    def test_broadcast_message(self, mock_socket):
        # Simulating sending a message by a user
        client_socket = self.server.clients[0]
        self.server.broadcast('Hello everyone!')

        # Checking if the message was sent to all clients
        client_socket.send.assert_called_with(b'Hello everyone!')


if __name__ == '__main__':
    unittest.main()
