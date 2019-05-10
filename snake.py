
from os import system, name
# from time import sleep
import msvcrt
import time
# import sys
import random
import copy
import pandas as pd

import numpy as np
# import tflearn
import math
# from tflearn.layers.core import input_data, fully_connected
# from tflearn.layers.estimator import regression

# clear the board


def clear():
    # Windows
    if name == 'nt':
        _ = system('cls')
    # Mac, Linux
    else:
        _ = system('clear')

# snakes imput funktion


class TimeoutExpired(Exception):
    pass


def input_with_timeout(prompt, timeout, timer=time.monotonic):
    # sys.stdout.write(prompt)
    # sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwch())  # XXX can it block on multibyte characters?
            # if result[-1] == '\n':  # XXX check what Windows returns here
            #     return ''.join(result[:-1])
        time.sleep(0.04)  # just to yield to other processes/threads
    if result != []:
        # print(result)
        return result[-1]
    raise TimeoutExpired


def KI_move(input_vec):
    # print(input_vec)
    return model_eval(input_vec)


def model_eval(input_vec):

    #     network = input_data(shape=[None, 4, 1], name='input')
    #     network = fully_connected(network, 1, activation='linear')
    #     network = regression(network, optimizer='adam', learning_rate=1e-2, loss='mean_square', name='target')
    #     model = tflearn.DNN(network)

    return random.choice([(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)])


class Board(object):
    def __init__(self, position_list=[(5, 5)], move_index=(0, 1), board_size=(8, 26), game_over=False, score=0):
        self.position_list = position_list
        self.move_index = move_index
        self.save_init = (copy.copy(position_list), copy.copy(move_index), copy.copy(board_size), copy.copy(game_over), copy.copy(score))
        self.board_size = board_size
        self.game_over = game_over
        self.pi_position = (random.choice([i for i in range(2, board_size[0] + 2)]), random.choice([i for i in range(2, board_size[1] + 2)]))
        self.score = score

    @property
    def possible_next_move(self):
        if len(self.position_list) == 1:
            return [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:
            return list(filter(lambda move: move != (- self.move_index[0], - self.move_index[1]), [(1, 0), (-1, 0), (0, 1), (0, -1)]))

    @property
    def possible_next_position(self):
        return list(map(lambda move_index: (self.position_list[-1][0] + move_index[0], self.position_list[-1][1] + move_index[1]), self.possible_next_move))

    def move(self, key, board):
        if key == 'w':
            temp_move_index = (-1, 0)
        elif key == 'a':
            temp_move_index = (0, -1)
        elif key == 's':
            temp_move_index = (1, 0)
        elif key == 'd':
            temp_move_index = (0, 1)
        else:
            temp_move_index = (0, 0)
        # else:
        #     move_index = (- self.position_list[-1][1], 0)
        #     next_position = (- self.position_list[-1][1], - self.position_list[-1][0])

        if temp_move_index in self.possible_next_move:
            self.move_index = temp_move_index

        next_position = (self.position_list[-1][0] + self.move_index[0], self.position_list[-1][1] + self.move_index[1])

        # if board[next_position] == ' ':
        #     self.position_list.append(next_position)
        delete = True
        if board[next_position] == '#':
            next_position = (next_position[0] - self.move_index[0], next_position[1] - self.move_index[1])
            while board[next_position] != '#':
                next_position = (next_position[0] - self.move_index[0], next_position[1] - self.move_index[1])
            next_position = (next_position[0] + self.move_index[0], next_position[1] + self.move_index[1])
        elif board[next_position] == 'S':
            return board[next_position]
        elif board[next_position] == 'O':
            delete = False

        self.position_list.append(next_position)
        if delete:
            del self.position_list[0]
        return board[next_position]

    @property
    def board(self):
        out = dict()
        for n in range(1, self.board_size[0] + 3):
            for m in range(1, self.board_size[1] + 3):
                if n == 1 or m == 1:
                    out[(n, m)] = '#'
                elif n == self.board_size[0] + 2 or m == self.board_size[1] + 2:
                    out[(n, m)] = '#'
                elif (n, m) in self.position_list:
                    out[(n, m)] = 'S'
                else:
                    out[(n, m)] = ' '
        out[self.pi_position] = 'O'
        return out

    @property
    def place_pi(self):
        possible_pi_positions = []
        save_board = self.board
        for n in range(2, self.board_size[0] + 2):
            for m in range(2, self.board_size[1] + 2):
                if save_board[(n, m)] == ' ':
                    possible_pi_positions.append((n, m))
        pi_position = random.choice(possible_pi_positions)
        self.pi_position = pi_position
        return pi_position

    @property
    def input_vec(self):
        _input_list = list()
        for move_index in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if move_index == self.move_index:
                _input_list.append(1)
            else:
                _input_list.append(0)

        def fill(num):
            out = list()
            for i in range(len(bin(num)[2:])):
                out.append(bin(num)[2:][i])
            out.reverse()
            while len(out) != 7:
                out.append(0)
            out.reverse()
            return out

        def fill_tuple(x):
            return fill(x[0]) + fill(x[1])

        _input_list += fill_tuple(self.position_list[0])
        _input_list += fill_tuple(self.position_list[-1])
        _input_list += fill_tuple(self.pi_position)

        for n in range(2, self.board_size[0] + 2):
            for m in range(2, self.board_size[1] + 2):
                if self.board[(n, m)] == 'S':
                    _input_list += [1]
                else:
                    _input_list += [0]
        _input_vec = tuple(_input_list)
        return _input_vec

    @property
    def reset(self):
        self.position_list = copy.copy(self.save_init[0])
        self.move_index = copy.copy(self.save_init[1])
        self.board_size = copy.copy(self.save_init[2])
        self.game_over = copy.copy(self.save_init[3])
        self.score = copy.copy(self.save_init[4])

    def play(self, snake_list=[(5, 5)], snake_move_index=(0, 1), KI=False, print_game=True, KI_model=KI_move):
        # self.position_list = snake_list
        # self.move_index = snake_move_index
        key = 't'

        if print_game:
            clear()
            print(self)
            while not self.game_over:
                if not KI:
                    try:
                        key = input_with_timeout('', 0.14)
                    except TimeoutExpired:
                        key = 'q'
                else:
                    temp_key = KI_model(self.input_vec)

                    time.sleep(0.14)

                    for x in (('w', (1, 0, 0, 0)), ('d', (0, 1, 0, 0)), ('s', (0, 0, 1, 0)), ('a', (0, 0, 0, 1))):
                        if x[1] == temp_key:
                            key = x[0]

                snake_new_head = self.move(key, self.board)
                if snake_new_head == 'S':
                    self.game_over = True
                elif snake_new_head == 'O':
                    self.score += 1
                    self.place_pi
                clear()
                print(self)
        else:
            for i in range(100):
                if not self.game_over:
                    temp_key = KI_model(self.input_vec)
                    for x in (('w', (1, 0, 0, 0)), ('d', (0, 1, 0, 0)), ('s', (0, 0, 1, 0)), ('a', (0, 0, 0, 1))):
                        if x[1] == temp_key:
                            key = x[0]

                    snake_new_head = self.move(key, self.board)
                    if snake_new_head == 'S':
                        self.game_over = True
                    elif snake_new_head == 'O':
                        self.score += 1
                        self.place_pi
                else:
                    print(self)
                    print(i)
                    return (i / 100) + self.score
            return (i / 100) + self.score

    # @property
    # def play_interface(self):
    #     def save_player

    #     playing = True
    #     while playing:
    #         self.game_over = False
    #         self.score = 0
    #         self.position_list = [(5, 5)]
    #         self.move_index = (0, 1)
    #         self.play()
    #         if input('Do you want to play a nother game?(y / n): ') == 'n':
    #             playing = False

    def KI_index(self, iterate=10):
        L = list()
        board = Board()
        for i in range(iterate):
            board.reset
            score = board.play(KI=True, print_game=False)
            L.append(score)
        return sum(L) / iterate

    def __repr__(self):
        return('snake_list = {}, snake_last = {}, board = {}, game_over = {}'.format(self.position_list, self.move_index, self.board_size, self.game_over))

    def __str__(self):
        save_dict = self.board
        if self.game_over:
            num_space = self.board_size[1] - 4
            if num_space < 0:
                num_space = 0
            out = num_space * ' ' + '{} Game Over!\n'.format(self.score)
        else:
            out = '\n'
        for n in range(1, self.board_size[0] + 3):
            for m in range(1, self.board_size[1] + 3):
                out += save_dict[(n, m)] + ' '
            out = out[:-1]
            out += '\n'
        out = out[:-1]
        return out


def play_snake(position_list=[(5, 5)], move_index=(0, 1), board_size=(8, 26), game_over=False, score=0):
    game_data_rep = 'game_data\\snake.xlsx'

    data = pd.read_excel(io=game_data_rep, index_col=0)
    board = Board()

    print('Leaderboard:\n' + str(data.max().sort_values(ascending=False)).strip('\ndtype: float64') + '\n')

    gamer_name = input('Input your Name: ')
    if not gamer_name in data:
        data[gamer_name] = np.nan

    playing = True
    while playing:
        board.reset
        board.play()

        for i in range(len(data[gamer_name])):
            if data[gamer_name].isna()[i]:
                data.at[i, gamer_name] = board.score
                break
            if i == len(data[gamer_name]) - 1:
                data.at[len(data[gamer_name]), gamer_name] = board.score

        print('Leaderboard:\n', str(data.max().sort_values(ascending=False)).strip('\ndtype: float64'))

        if input('Do you want to play a nother game?(y / n): ') == 'n':
            playing = False

    data.to_excel(excel_writer=game_data_rep)


if __name__ == '__main__':
    Board().game_over = True
    print(Board().game_over)
else:

    # def save_player():
    #     gaming_name = input('What is your gaming name?: ')
    #     with open('C:\\Users\\lol--\\Documents\\python\\Games\\game_data\\snake.txt', 'r') as f:
    #         lines = f.readlines()
    #         gaming_names = list(map(lambda x: x[:-1], lines[:-1])) + lines[-1:]

    #     with open('C:\\Users\\lol--\\Documents\\python\\Games\\game_data\\snake.txt', 'w') as f:
    #         if lines != []:
    #             if not gaming_name in gaming_names:
    #                 lines[-1] += '\n'
    #         lines.append(gaming_name)
    #         for elem in lines:
    #             f.write(elem)

    # save_player()

    # playing = True
    # while playing:
    #     Board(position_list=[(5, 5)], move_index=(0, 1)).play()
    #     if input('Do you want to play a nother game?(y / n): ') == 'n':
    #         playing = False

    play_snake()
