from collections import Counter, OrderedDict
import numpy as np
import pdb

from rlcard.envs import Env


class AxieEnv(Env):
    ''' axie Environment
    '''

    def __init__(self, config):
        from rlcard.games.axie import Game

        self.name = 'axie'
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[467], [467]]
        self.action_shape = [[84] for _ in range(self.num_players)]

    def _extract_state(self, state):
        ''' Encode state

        Args:
            state (dict): dict of original state
        '''
        obs = np.concatenate(([state['roundNum']],
                              state['order'],
                              [state['myTeamCardsNum']],
                              [state['myTeamEnergy']],
                              [state['enemyCardsNum']],
                              [state['enemyEnergy']],
                              state['axie0'],
                              state['axie1'],
                              state['axie2'],
                              state['enemyAxie0'],
                              state['enemyAxie1'],
                              state['enemyAxie2'],
                              ))

        legal_actions = OrderedDict({i: None for i in range(len(state['actions']))})
        extracted_state = OrderedDict({'obs': obs, 'legal_actions': legal_actions})
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = [i for i in range(len(state['actions']))]
        extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        return self.game.judger.judge_payoffs(self.game.winner_id)

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (string): The action that will be passed to the game engine.

        Note: Must be implemented in the child class.
        '''
        aClass = ['reptile', 'plant', 'dusk',
                  'aquatic', 'bird', 'dawn',
                  'beast', 'bug', 'mech']
        attackType = ['melee', 'ranged', 'support']
        part = ['mouth', 'horn', 'back', 'tail']
        info = []
        for acts in action_id:
            tmp = []
            for i in range(4):
                if len(acts) >= i+1:
                    card = acts[i]
                    tmp = [card.idx, aClass.index(card.cProp),
                           card.cost, card.attack, card.defend,
                           attackType.index(card.attackType),
                           part.index(card.bodyPart)]
                else:
                    tmp = [-1]*7
                info.extend(tmp)
        return info

    def _get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        actions = self.game.state[0]['actions']['actions']
        legal_actions0 = []
        for acts in actions:
            actsTmp = []
            for axieAct in acts:
                axieTmp = []
                for act in axieAct:
                    axieTmp.append(act.idx)
                actsTmp.append(axieTmp)
            legal_actions0.append(actsTmp)
        actions = self.game.state[1]['actions']['actions']
        legal_actions1 = []
        for acts in actions:
            actsTmp = []
            for axieAct in acts:
                axieTmp = []
                for act in axieAct:
                    axieTmp.append(act.idx)
                actsTmp.append(axieTmp)
            legal_actions1.append(actsTmp)
        legal_actions = [legal_actions0, legal_actions1]
        return legal_actions
