import socket
from _thread import *
import pickle

import pyautogui

from game import Game

# Set up the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = ('192.168.100.8', 8888)

try:
    s.bind(ADDR)
except socket.error as se:
    print(f'SOCKET ERROR: {str(se)}')

s.listen(4)  # Allow up to 4 players to connect
print('Listening for incoming connections...')
tp = 2
connected = set()
games = {}
player_counts = {}  # Dictionary to track player counts for each game ID
idCount = 0

# Threaded client handler function
def thread_client(conn, player_id, game_id):
    global idCount, player_counts

    print(f'SERVER: Player ID {player_id} Sent!')
    conn.send(str.encode(str(player_id)))  # Send player ID to the client

    reply = ""
    while True:
        #try:
        data = conn.recv(4096).decode()

        if game_id in games:
            game = games[game_id]

            if not data:
                break
            else:
                if data == "reset":
                    game.reset()
                elif data == "game":
                    conn.send('get-game'.encode())
                    new_game = pickle.loads(conn.recv(8192))
                    if new_game is None:
                        print('Received a None game object.')
                    else:
                        print('New Game received from client')
                        games[game_id] = new_game
                elif data == 'get':
                    if game is None:
                        print('Sent NONE')
                    conn.sendall(pickle.dumps(game))


        else:
            print(f"No game found for game ID: {game_id}")
            break
        # except Exception as e:
        #     print(f"Error during client communication: {e}")
        #     break

    print("Lost connection")
    try:
        # If the player disconnects, remove them from the player count for this game
        player_counts[game_id] -= 1
        if player_counts[game_id] <= 0:
            del player_counts[game_id]
            del games[game_id]
            print("Closing Game", game_id)
    except Exception as e:
        print(f"Error during player count adjustment: {e}")
    idCount -= 1
    conn.close()

# Main loop to accept incoming connections
while True:
    conn, addr = s.accept()
    print(f'Connected With: {addr}')

    idCount += 1
    player_id = idCount-1  # Player ID is simply the count
    game_id = (idCount - 1) // tp  # Determine game ID based on player count (4 players per game)

    if idCount % tp == 1:
        games[game_id] = Game(game_id)# Create a new game if it doesn't exist
        games[game_id].shuffle(tp)
        player_counts[game_id] = 0      # Initialize the player count for this game
        print(f'Created a new game with ID: {game_id}')

    if player_counts[game_id] < tp:
        player_counts[game_id] += 1  # Increment player count for the game
        start_new_thread(thread_client, (conn, player_id, game_id))  # Start a new thread for this client
    else:
        conn.close()
        print(f'Rejected connection! Game {game_id} is full.')
