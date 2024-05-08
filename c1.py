
#Morad Zubidat - 208156828

import socket
import threading
import ast

global game


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


def make_move(game, stack, player):
    for i in range(6):  # Now iterating through 6 slots
        if game[stack][i] is None:
            game[stack][i] = player
            return True
    return False  # Stack is full


def check_win(game):
    # Check verticals for four in a row
    for stack in range(7):  # Check within 7 stacks
        for slot in range(3):  # Only need to check up to the 3rd index for four in a row
            if (game[stack][slot] is not None and
                    game[stack][slot] == game[stack][slot + 1] ==
                    game[stack][slot + 2] == game[stack][slot + 3]):
                return game[stack][slot]

    # Check horizontals for four in a row
    for slot in range(6):  # Check within 6 slots
        for stack in range(4):  # Check only up to the 4th stack index for four in a row
            if (game[stack][slot] is not None and
                    game[stack][slot] == game[stack + 1][slot] ==
                    game[stack + 2][slot] == game[stack + 3][slot]):
                return game[stack][slot]

    return None  # No winner yet


def receive_messages(client_socket, game):
    while True:

        player = 0  # Player 1 starts
        moves = 0
        try:
            message = client_socket.recv(1024).decode()
            data = message.split('~')
            if len(data) == 2:
                # print("Player-", data[0])
                data = data[1]

            else:
                if message.isdigit():
                    if make_move(game, int(message), 1):
                        moves += 1
                        if check_win(game) is not None:
                            print_game(game)
                            print(f"Player {player + 1} wins!")
                            # break
                        if moves == 42:  # Now 42 moves possible in total (7 stacks * 6 slots each)
                            print("It's a draw!")
                            # break
                        player = 1 - player  # Switch players
                    else:
                        print("That Board is full, choose another.")
                else:
                    print("\n", message)
        except Exception as e:
            print("An error occurred:", e)
            client_socket.close()
            break


def client_program():
    host = '192.168.1.219'
    port = 5560
    game = initialize_game()
    player = 0  # Player 1 starts
    moves = 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Start listening thread
    threading.Thread(target=receive_messages, args=(client_socket, game,), daemon=True).start()

    while True:

        try:
            message = input()
            if message.lower().strip() == 'exit':
                break
            client_socket.send(message.encode())
            if message.isdigit():
                print("\n initial Game Board")
                print_game(game)
                if make_move(game, int(message), 0):
                    moves += 1
                    if check_win(game) is not None:
                        print_game(game)
                        print(f"Player {player + 1} wins!")
                        # break
                    if moves == 42:  # Now 42 moves possible in total (7 stacks * 6 slots each)
                        print("It's a draw!")
                        # break
                    player = 1 - player  # Switch players
                    print("\n After Play Game Board")
                    print_game(game)
                else:
                    print("That Board is full, choose another.")
        except Exception as e:
            print("An error occurred:", e)
            break

    client_socket.close()


if __name__ == '__main__':
    i = 0
    client_program()