# -*- coding: utf-8 -*-
''' Implement Doudizhu Game class
'''
import functools
from heapq import merge
import numpy as np
import pdb

from .public import Public
from rlcard.games.axie import Player
from .rules import PVP, Round
from rlcard.games.axie import Judger
from .dataOp import inputHandInCards
import pickle


class AxieGame:
    ''' Provide game APIs for env to run axie and get corresponding state
    information.
    '''
    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = 2
        list_file = open('./csv/actions.pickle', 'rb')
        self.actions_data = pickle.load(list_file)

    def init_game(self):
        ''' Initialize players and state.

        Returns:
            dict: first state in one game
            int: current player's id
        '''
        # initialize public variables
        self.winner_id = None
        self.history = []

        # initialize players
        self.players = [Player(num, self.np_random)
                        for num in range(self.num_players)]
        # initialize round to deal cards and determine landlord
        self.pvp = PVP(self.players[0].team, self.players[1].team)

        # initialize judger
        self.judger = Judger(self.players, self.np_random)

        # get state of first player
        self.public = Public(self.pvp)
        self.state = [self.get_state(num) for num in range(self.num_players)]
        player_id = [i for i in range(self.num_players)]

        return self.state, player_id

    def step(self, actions):
        ''' Perform one draw of the game

        Args:
            action (str): specific action of doudizhu. Eg: '33344'

        Returns:
            dict: next player's state
            int: next player's id
        '''
        if self.allow_step_back:
            # TODO: don't record game.round, game.players, game.judger if allow_step_back not set
            pass

        # perfrom action
        teamAct0, teamAct1 = actions  # actions is alive
        for i in range(3):
            if teamAct0[i] != []:
                axieIdx = 'l'+str(i+1)
                axieChain = (axieIdx, teamAct0[i])
                inputHandInCards(self.pvp, isRl=True, axieChain=axieChain)
        for i in range(3):
            if teamAct1[i] != []:
                axieIdx = 'r'+str(i+1)
                axieChain = (axieIdx, teamAct1[i])
                inputHandInCards(self.pvp, isRl=True, axieChain=axieChain)

        # update history
        self.public.update_history(teamAct0, teamAct1)

        # nextRound
        self.pvp.rnd.nextRound()

        # judge game
        if self.judger.judge_game(self.pvp):
            self.winner_id = self.judger.judge_winner(self.pvp)
            self.pvp.rnd.order()

        # get next state
        state = [self.get_state(num) for num in range(self.num_players)]
        self.state = state
        player_id = [0, 1]

        return state, player_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        # winner_id will be always None no matter step_back from any case
        self.winner_id = None

        # reverse round
        self.pvp = self.public.saveRound[self.pvp.rnd.roundNum-1]

        self.state = [self.get_state(num) for num in range(self.num_players)]
        return True

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        player = self.players[player_id]
        public = self.public.update(self.pvp)
        if self.is_over():
            actions = []
        else:
            actions = player.available_actions()
        state = player.get_state(self.public.public, actions)

        return state

    @staticmethod
    def get_num_actions():
        ''' Return the total number of abstract acitons

        Returns:
            int: the total number of abstract actions of doudizhu
        '''
        return 2967813

    def get_num_players(self):
        ''' Return the number of players in doudizhu

        Returns:
            int: the number of players in doudizhu
        '''
        return self.num_players

    def is_over(self):
        ''' Judge whether a game is over

        Returns:
            Bool: True(over) / False(not over)
        '''
        return self.judger.judge_game(self.pvp)

    def copy_game(self, pvp):
        pvp = self.public.copy_pvp(pvp)
        self.players[0].team = pvp.teamLeft
        self.players[1].team = pvp.teamRight
        return pvp
