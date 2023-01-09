# -*- coding: utf-8 -*-
''' Implement Doudizhu Judger class
'''
import numpy as np
import pdb
import collections
from itertools import combinations
from bisect import bisect_left


class AxieJudger:
    ''' Determine what cards a player can play
    '''
    def __init__(self, players, np_random):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        self.players = players
        self.np_random = np_random

    @staticmethod
    def judge_game(pvp):
        ''' Judge whether the game is over

        Args:
            players (list): list of DoudizhuPlayer objects
            player_id (int): integer of player's id

        Returns:
            (bool): True if the game is over
        '''
        flag = False
        if len(pvp.rnd.axieAlive[0]) == 0 and len(pvp.rnd.axieAlive[1]) != 0:
            flag = True
        elif len(pvp.rnd.axieAlive[0]) != 0 and len(pvp.rnd.axieAlive[1]) == 0:
            flag = True
        elif len(pvp.rnd.axieAlive[0]) == 0 and len(pvp.rnd.axieAlive[1]) == 0:
            flag = True
        return flag

    @staticmethod
    def judge_winner(pvp):
        if len(pvp.rnd.axieAlive[0]) == 0 and len(pvp.rnd.axieAlive[1]) != 0:
            winner_id = 1
        elif len(pvp.rnd.axieAlive[0]) != 0 and len(pvp.rnd.axieAlive[1]) == 0:
            winner_id = 0
        elif len(pvp.rnd.axieAlive[0]) == 0 and len(pvp.rnd.axieAlive[1]) == 0:
            winner_id = -1
        return winner_id

    @staticmethod
    def judge_payoffs(winner_id):
        payoffs = np.array([0, 0])
        if winner_id == 0:
            payoffs[0] = 1
            payoffs[1] = -1
        elif winner_id == 1:
            payoffs[1] = 1
            payoffs[0] = -1
        return payoffs
