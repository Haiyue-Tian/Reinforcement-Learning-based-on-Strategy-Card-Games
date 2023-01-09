# -*- coding: utf-8 -*-
''' Implement Doudizhu Player class
'''
import functools
import copy, pdb
from .generate import generateTeam


class AxiePlayer:
    ''' Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom corresponding action
    '''
    def __init__(self, player_id, np_random):
        ''' Give the player an id in one game

        Args:
            player_id (int): the player_id of a player

        Notes:
            # 1. role: A player's temporary role in one game(landlord or peasant)
            2. played_cards: The cards played in one round
            # 3. hand: Initial cards
            # 4. _current_hand: The rest of the cards after playing some of them
        '''

        self.team = generateTeam()
        self.np_random = np_random
        self.player_id = player_id

    @property
    def current_hand(self):
        return self._current_hand

    def set_current_hand(self, value):
        self._current_hand = value

    def get_state(self, public, actions):
        def axieInfo(axie, isMyAxie, history=None, axieIdx=None):
            aClass = ['reptile', 'plant', 'dusk',
                      'aquatic', 'bird', 'dawn',
                      'beast', 'bug', 'mech']
            attackType = ['melee', 'ranged', 'support']
            part = ['mouth', 'horn', 'back', 'tail']
            buff = ['attackUp', 'moralUp', 'speedUp', 'attackDown',
                    'moralDown', 'speedDown', 'aroma', 'chill',
                    'fear', 'fragile', 'jinx', 'lethal', 'poison',
                    'sleep', 'stench', 'stun']

            info = []
            info.append(axie.IDIdx)
            info.append(axie.lv)
            info.append(axie.posIdx)
            info.append(aClass.index(axie.aProp))
            info.extend([axie.health, axie.speed, axie.skill, axie.moral])
            info.append(axie.maxHp)
            for i in range(4):
                card = axie.cards[i]
                info.extend([card.idx, aClass.index(card.cProp),
                             card.cost, card.attack, card.defend,
                             attackType.index(card.attackType),
                             part.index(card.bodyPart)])
            info.append(axie.hp)
            info.append(axie.lastStand)
            info.append(axie.lastStandTicks)
            for i in range(16):
                if buff[i] in axie.buff:
                    info.append(len(axie.buff[buff[i]]))
                elif buff[i] in axie.debuff:
                    if type(axie.debuff[buff[i]]) is list:
                        info.append(len(axie.debuff[buff[i]]))
                    else:
                        if buff[i] == 'poison':
                            info.append(axie.debuff[buff[i]])
                        else:
                            info.append(1)
                else:
                    info.append(0)
            if isMyAxie:
                info.extend(axie.cardsNow)
                info.extend(axie.cardsNum)
            else:
                for hist in history:
                    info.extend(hist[axieIdx])
            return info

        def actionsInfo(actions):
            aClass = ['reptile', 'plant', 'dusk',
                      'aquatic', 'bird', 'dawn',
                      'beast', 'bug', 'mech']
            attackType = ['melee', 'ranged', 'support']
            part = ['mouth', 'horn', 'back', 'tail']
            info = []
            for acts in actions:
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

        state = {}
        state['roundNum'] = public['roundNum']
        state['order'] = public['order']
        state['myTeamCardsNum'] = self.team.cardsNum
        state['myTeamEnergy'] = self.team.energy
        enemy_id = 0 if self.player_id else 1
        ID = [self.team.axies[0].ID,
              self.team.axies[1].ID,
              self.team.axies[2].ID,
              public['team'][enemy_id].axies[0].ID,
              public['team'][enemy_id].axies[1].ID,
              public['team'][enemy_id].axies[2].ID]
        state['enemyCardsNum'] = public['cardsNum'][enemy_id]
        state['enemyEnergy'] = public['energy'][enemy_id]
        state['self'] = self.player_id  # myTeam 0, enemy 1
        state['axie0'] = axieInfo(self.team.axies[0], 1)
        state['axie1'] = axieInfo(self.team.axies[1], 1)
        state['axie2'] = axieInfo(self.team.axies[2], 1)
        state['enemyAxie0'] = axieInfo(public['team'][enemy_id].axies[0],
                                       0, public['history'][enemy_id], 0)
        state['enemyAxie1'] = axieInfo(public['team'][enemy_id].axies[1],
                                       0, public['history'][enemy_id], 1)
        state['enemyAxie2'] = axieInfo(public['team'][enemy_id].axies[2],
                                       0, public['history'][enemy_id], 2)
        # state['actions'] = actionsInfo(actions['actions'])
        if actions != []:
            state['actions'] = actions['actions']
            state['actionsIdx'] = actions['actionsIdx']
        else:
            state['actions'] = [[[], [], []]]
            state['actionsIdx'] = [[[], [], []]]

        return state

    def available_actions(self):
        ''' Get the actions can be made based on the rules

        Args:
            greater_player (DoudizhuPlayer object): player who played
        current biggest cards.
            judger (DoudizhuJudger object): object of DoudizhuJudger

        Returns:
            list: list of string of actions. Eg: ['pass', '8', '9', 'T', 'J']
        '''
        def axieProbAct(maxCard, cards):
            cardsNow, card = cards[0], cards[1]
            actions = [[]]
            actionsIdx = [[]]
            if maxCard >= 1:
                for i in range(4):
                    tmp = []
                    tmpIdx = []
                    if cardsNow[i] > 0:
                        tmp.append(card[i])
                        actions.append(tmp)
                        tmpIdx.append(i)
                        actionsIdx.append(tmpIdx)

            if maxCard >= 2:
                for i in range(4):
                    tmp = []
                    tmpIdx = []
                    if cardsNow[i] > 0:
                        tmp.append(card[i])
                        tmpIdx.append(i)
                        cardsNow1 = copy.copy(cardsNow)
                        cardsNow1[i] = cardsNow1[i] - 1
                        for j in range(4):
                            tmp1 = copy.copy(tmp)
                            tmpIdx1 = copy.copy(tmpIdx)
                            if cardsNow1[j] > 0:
                                tmp1.append(card[j])
                                actions.append(tmp1)
                                tmpIdx1.append(j)
                                actionsIdx.append(tmpIdx1)

            if maxCard >= 3:
                for i in range(4):
                    tmp = []
                    tmpIdx = []
                    if cardsNow[i] > 0:
                        tmp.append(card[i])
                        tmpIdx.append(i)
                        cardsNow1 = copy.copy(cardsNow)
                        cardsNow1[i] = cardsNow1[i] - 1
                        for j in range(4):
                            tmp1 = copy.copy(tmp)
                            tmpIdx1 = copy.copy(tmpIdx)
                            if cardsNow1[j] > 0:
                                tmp1.append(card[j])
                                tmpIdx1.append(j)
                                cardsNow2 = copy.copy(cardsNow1)
                                cardsNow2[j] = cardsNow2[j] - 1
                                for k in range(4):
                                    tmp2 = copy.copy(tmp1)
                                    tmpIdx2 = copy.copy(tmpIdx1)
                                    if cardsNow2[k] > 0:
                                        tmp2.append(card[k])
                                        actions.append(tmp2)
                                        tmpIdx2.append(k)
                                        actionsIdx.append(tmpIdx2)

            if maxCard >= 4:
                for i in range(4):
                    tmp = []
                    tmpIdx = []
                    if cardsNow[i] > 0:
                        tmp.append(card[i])
                        tmpIdx.append(i)
                        cardsNow1 = copy.copy(cardsNow)
                        cardsNow1[i] = cardsNow1[i] - 1
                        for j in range(4):
                            tmp1 = copy.copy(tmp)
                            tmpIdx1 = copy.copy(tmpIdx)
                            if cardsNow1[j] > 0:
                                tmp1.append(card[j])
                                tmpIdx1.append(j)
                                cardsNow2 = copy.copy(cardsNow1)
                                cardsNow2[j] = cardsNow2[j] - 1
                                for k in range(4):
                                    tmp2 = copy.copy(tmp1)
                                    tmpIdx2 = copy.copy(tmpIdx1)
                                    if cardsNow2[k] > 0:
                                        tmp2.append(card[k])
                                        tmpIdx2.append(k)
                                        cardsNow3 = copy.copy(cardsNow2)
                                        cardsNow3[k] = cardsNow3[k] - 1
                                        for m in range(4):
                                            tmp3 = copy.copy(tmp2)
                                            tmpIdx3 = copy.copy(tmpIdx2)
                                            if cardsNow3[m] > 0:
                                                tmp3.append(card[m])
                                                actions.append(tmp3)
                                                tmpIdx3.append(m)
                                                actionsIdx.append(tmpIdx3)
            return {'actions': actions, 'actionsIdx': actionsIdx}

        def combineActions(axieAct, energy):
            axie1, axie2, axie3 = axieAct
            actions, actionsIdx = [], []
            lenAxie1, lenAxie2 = len(axie1['actions']), len(axie2['actions'])
            lenAxie3 = len(axie3['actions'])
            for i in range(lenAxie1):
                eng = energy
                tmpActions, tmpActionsIdx = [], []
                tmpActions.append(axie1['actions'][i])
                tmpActionsIdx.append(axie1['actionsIdx'][i])
                eng -= len(axie1['actions'][i])
                flag1 = 1
                for j in range(lenAxie2):
                    eng1 = eng
                    tmpActions1 = copy.copy(tmpActions)
                    tmpActionsIdx1 = copy.copy(tmpActionsIdx)
                    flag11 = 0
                    if len(axie2['actions'][j]) <= eng:
                        tmpActions1.append(axie2['actions'][j])
                        tmpActionsIdx1.append(axie2['actionsIdx'][j])
                        eng1 -= len(axie2['actions'][j])
                        flag11 = 1
                    else:
                        if flag1:
                            tmpActions1.append([])
                            tmpActionsIdx1.append([])
                            flag1 = 0
                            flag11 = 1
                    if flag11:
                        flag2 = 1
                        for k in range(lenAxie3):
                            eng2 = eng1
                            tmpActions2 = copy.copy(tmpActions1)
                            tmpActionsIdx2 = copy.copy(tmpActionsIdx1)
                            flag22 = 0
                            if len(axie3['actions'][k]) <= eng2:
                                tmpActions2.append(axie3['actions'][k])
                                tmpActionsIdx2.append(axie3['actionsIdx'][k])
                                eng2 -= len(axie3['actions'][k])
                                flag22 = 1
                            else:
                                if flag2:
                                    tmpActions2.append([])
                                    tmpActionsIdx2.append([])
                                    flag2 = 0
                                    flag22 = 1
                            if flag22:
                                flag = 1
                                if tmpActions2 in actions:
                                    flag = 0
                                if flag:
                                    actions.append(tmpActions2)
                                    actionsIdx.append(tmpActionsIdx2)
            return {'actions': actions, 'actionsIdx': actionsIdx}

        cards = []
        actions = []
        for axie in self.team.axies:
            cards.append((axie.cardsNow, axie.cards))
        energy = self.team.energy
        axieAct = []
        for i in range(3):
            axie = self.team.axies[i]
            if axie.hp > 0 or axie.lastStand == 1:
                maxCard = min(energy, sum(axie.cardsNow), 4)
                axieAct.append(axieProbAct(maxCard, cards[i]))
            else:
                axieAct.append({'actions': [[], [], []], 'actionsIdx': [[], [], []]})
        actions = combineActions(axieAct, energy)
        return actions
