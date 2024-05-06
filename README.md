# Simple Client-Server Chat

The client-server chat application enables users to engage in real-time text communication. Users can register, log in, send messages to all users in the chat room, and execute special commands such as kicking a user from the chat, banning a user, and quitting the chat. Additionally, there is an option to grant administrator privileges to a user named "admin".

## How to Run the Application

1.Make sure you have Python installed (version 3.12) on your computer.

2.Clone this project to your computer.

3.Install the required libraries by running pip install -r requirements.txt

4.Run the db.py file to create database to store your users

5.Run the server.py file to start the server.

6.Run the client.py file to start the client you can also open multiple client.py file to communicate.

7.Follow the on-screen instructions to log in or register a user.

## Application Features

- Login: Users can log in by providing their username and password.

- Registration: New users can register by providing a unique username and password.

- Sending Messages: Logged-in users can send text messages to all users in the chat room.

- Special Commands: Users with administrator privileges can execute commands such as kicking other users from the chat (
  kick), banning users (ban), and quitting the chat (quit).

## Requirements

- Python 3.12
- bcrypt library
- SQLAlchemy library

# Command Permissions and Usage:

## Login:

- Command: login

- Description: Allows users to log in to the chat by providing their username and password.

- Example: login

- After you entering login enter username and password

## Registration:

- Command: register

- Description: Allows new users to register for the chat by providing a unique username and password.

- Example: register

- After you entering register enter username and password

## Methods Kick and Ban
- you can only use if you are admin and if you want be admin create username=admin and comme up with a password
## Kick (Admin Only):

- Command: /kick [username]

- Description: Allows administrators to kick a user from the chat by providing their username.

- Example: /kick user123

## Ban (Admin Only):

- Command: /ban [username]

- Description: Allows administrators to ban a user from the chat by providing their username.

- Example: /ban user456

## Quit:

- Command: /quit

- Description: Allows users to quit the chat.

- Example: /quit
