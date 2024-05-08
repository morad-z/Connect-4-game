
#Morad Zubidat - 208156828

import socket
import threading
import select
import random
def initialize_game():
    # 7x6 game board initialized to None (7 stacks, each with 6 slots)
    return [[None for _ in range(6)] for _ in range(7)]
def print_game(game):
    for slot in range(5, -1, -1):  # Start from the top (5) down to the bottom (0)
        row_display = []
        for stack in range(7):  # Iterate through each of the 7 stacks
            if game[stack][slot] is None:
                row_display.append('-')
            else:
                row_display.append(str(game[stack][slot]))
        print(' '.join(row_display))

def make_move(game, stack, player, check_only=False):
    for i in range(6):
        if game[stack][i] is None:
            if check_only:
                return True
            game[stack][i] = player
            return True
    return False

def check_win(game):
    # Check verticals for four in a row
    for stack in range(7):  # Check within 7 stacks
        for slot in range(3):  # Only need to check up to the 3rd index for four in a row
            if (game[stack][slot] is not None and
                game[stack][slot] == game[stack][slot+1] ==
                game[stack][slot+2] == game[stack][slot+3]):
                return game[stack][slot]

    # Check horizontals for four in a row
    for slot in range(6):  # Check within 6 slots
        for stack in range(4):  # Check only up to the 4th stack index for four in a row
            if (game[stack][slot] is not None and
                game[stack][slot] == game[stack+1][slot] ==
                game[stack+2][slot] == game[stack+3][slot]):
                return game[stack][slot]

    # Optional: Implement diagonal checks for completeness

    return None  # No winner yet

def find_best_move(game, player):
    # First, check if the server can win in the next move
    for stack in range(7):
        if make_move(game, stack, player, check_only=True):
            temp_game = [row[:] for row in game]  # Create a copy of the game board
            make_move(temp_game, stack, player)  # Simulate the move
            if check_win(temp_game) == player:  # Check if this move wins the game
                return stack  # Return this stack as the best move

    # Next, check to block the opponent's winning move
    opponent = 1 - player
    for stack in range(7):
        if make_move(game, stack, opponent, check_only=True):
            temp_game = [row[:] for row in game]  # Create a copy of the game board
            make_move(temp_game, stack, opponent)  # Simulate the move
            if check_win(temp_game) == opponent:  # Check if the opponent would win
                return stack  # Block this move

    # If no immediate win or block, pick a random column (This can be improved)
    return random.randrange(0, 7)


class ChatServer:
    def __init__(self, host='192.168.1.219', port=5560):
        self.clients = {}  # Maps client names to their socket and address
        self.reverse_lookup = {}  # Maps sockets to client names
        self.direct_communications = {}  # Maps client names to their direct communication partner
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)
        print(f"Server listening on {host}:{port}")

    def broadcast_clients(self, exclude=None):
        client_list = "\n".join([name for name in self.clients if name != exclude])
        message = f"Currently connected clients:\n{client_list}\nWho do you want to communicate with?"
        for name, (client, _) in self.clients.items():
            if name != exclude:
                client.send(message.encode())

    def handle_client(self, client, address):
        try:
            self.broadcast_clients()
            game = initialize_game()
            player = 0  # Player 1 starts
            moves = 0
            i = 0
            client.send("What is your name?".encode())
            name = client.recv(1024).decode().strip()
            self.clients[name] = (client, address)
            self.reverse_lookup[client] = name

            # Ask the client if they want to communicate with the server or another client
            client.send("Do you want to Play with me (server) or another client? Reply 'server' or 'client'".encode())
            choice = client.recv(1024).decode().strip().lower()

            if choice == 'server':
                client.send("Choose difficulty level: 1. Easy 2. Hard".encode())
                difficulty = client.recv(1024).decode().strip()
                client.send("You are now Game with the server. Type 'exit' to end.".encode())
                while True:
                    message = client.recv(1024).decode().strip()
                    if message == "exit":
                        break

                    client.send(f"{player}~{game}".encode())
                    client.send(f"Choose stack (0-6):".encode())
                    if difficulty == "2":  # If Hard difficulty selected
                        move = find_best_move(game, player)
                    else:  # Default to Easy
                        move = random.randrange(0, 7)
                    if make_move(game, int(message), player):
                        moves += 1
                        if check_win(game) is not None:
                            print_game(game)
                            message = f"Player {player + 1} wins!"
                            print(message)
                            client.send(message.encode())
                            break  # Ensure to exit the loop after a win

                            # break
                        if moves == 42:  # Now 42 moves possible in total (7 stacks * 6 slots each)
                            print("It's a draw!")
                            client.send(f"It's a draw!".encode())
                            # break
                        player = 1 - player  # Switch players
                        print("Next Player is: ", player)
                    else:
                        print("That Board is full, choose another.")


#                   Server Side
                    print_game(game)
                    print(f"Server Play ({player})")
                    print(f"Choose stack (0-6):")
                    message = random.randrange(0, 6)
                    client.send(str(message).encode())
                    print("Server select: ", message)
                    i = i+1
                    if make_move(game, int(message), player):
                        moves += 1
                        if check_win(game) is not None:
                            print_game(game)
                            message = f"Player {player + 1} wins!"
                            print(message)
                            client.send(message.encode())
                            break  # Ensure to exit the loop after a win

                        if moves == 42:  # Now 42 moves possible in total (7 stacks * 6 slots each)
                            print("It's a draw!")
                            break
                        player = 1 - player  # Switch players
                    else:
                        print("That Board is full, choose another.")

            elif choice == 'client':

                while True:
                    # print("global value of i is: ", i)
                    message = client.recv(1024).decode().strip()
                    if message == "exit":
                        partner_name = self.direct_communications.pop(name, None)
                        if partner_name:
                            partner_client, _ = self.clients[partner_name]
                            partner_client.send(f"{name} has exited the Game.".encode())
                            self.direct_communications.pop(partner_name, None)
                        break


                    if name in self.direct_communications:
                        partner_name = self.direct_communications[name]
                        partner_client, _ = self.clients[partner_name]
                        print("I is: ", i)
                        # player = int(i%2)
                        print_game(game)

                        partner_client.send(f"{player}~{message}".encode())
                        # partner_client.send(f"Choose stack (0-6):".encode())
                        i = i+1
                        if make_move(game, int(message), 0):
                            moves += 1
                            if check_win(game) is not None:
                                print_game(game)
                                message = f"Player {player + 1} wins!"
                                print(message)
                                client.send(message.encode())
                                break  # Ensure to exit the loop after a win

                            if moves == 42:  # Now 42 moves possible in total (7 stacks * 6 slots each)
                                print("It's a draw!")
                                break
                            player = 1 - player  # Switch players
                        else:
                            print("That Board is full, choose another.")


                        partner_name = self.direct_communications[name]
                        partner_client, _ = self.clients[partner_name]

                        partner_client.send(f"{player}~{game}".encode())
                        partner_client.send(f"Choose stack (0-6):".encode())
                        i = i+1
                        if make_move(game, int(message), 1):
                            moves += 1
                            if check_win(game) is not None:
                                print_game(game)
                                message = f"Player {player + 1} wins!"
                                print(message)
                                client.send(message.encode())
                                break  # Ensure to exit the loop after a win

                            if moves == 42:  # Now 42 moves possible in total (7 stacks * 6 slots each)
                                print("It's a draw!")
                                break
                            player = 1 - player  # Switch players
                            # print("Next Player is: ", player)
                        else:
                            print("That Board is full, choose another.")

                    else:
                        if message in self.clients and message != name:
                            partner_client, _ = self.clients[message]
                            partner_client.send(f"{name} wants to Play with you. Reply?".encode())
                            reply = partner_client.recv(1024).decode().strip()
                            if reply.lower() == "yes":
                                self.direct_communications[name] = message
                                self.direct_communications[message] = name
                                client.send("You are now in direct Play. Type 'exit' to end.".encode())
                                partner_client.send("You are now in direct Play. Type 'exit' to end.".encode())
                                # partner_client.send(f"{player}~{game}".encode())
                                # print("I is: ", i)
                                # i = i+1

                            else:
                                client.send(f"{message} declined the Play request.".encode())

            client.close()
            del self.clients[name]
            del self.reverse_lookup[client]

        except Exception as e:
            print(f"Error handling client {address}: {e}")

    def run(self):
        print("Server running...")
        try:
            while True:
                client, address = self.sock.accept()
                print(f"Connection from {address}")
                threading.Thread(target=self.handle_client, args=(client, address)).start()
        finally:
            for client, _ in self.clients.values():
                client.close()
            self.sock.close()

if __name__ == "__main__":
    server = ChatServer()
    server.run()