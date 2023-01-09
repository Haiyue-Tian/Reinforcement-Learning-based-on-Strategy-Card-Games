import pandas as pd
import numpy as np
import math
from .cards import *
from .rules import PVP, Round
from .buff_debuff import *
from .attack_defend import Attack, Defend, Speed, Morale


class Team():
    def __init__(self):
        self.axies = []
        self.axieNum = 0
        self.position = np.array([[-1, -2, -1, -2, -1],
                                  [-2, -1, -2, -1, -2],
                                  [-1, -2, -1, -2, -1]])
        self.energy = None
        self.cardsNum = None
        self.sendCardThisRound = None
        self.thisRound = None

    def set_energy_cardsNum(self, state='pvp'):
        self.energy = 3 if state == 'pvp' else 4
        self.cardsNum = 24
        self.sendCardThisRound = 0

    def addAxie(self, newAxie, pos=0):
        '''
        pos = 1-7
        self.position = np.array([[-1, 5,-1, 2,-1],
                                  [ 7,-1, 4,-1, 1],
                                  [-1, 6,-1, 3,-1]]) '''
        if self.axieNum < 3:
            newAxie.axieIdx = self.axieNum
            self.axieNum += 1
            self.axies.append(newAxie)
            coord = self.set_position(newAxie, pos)
            newAxie.team = self
            newAxie.pos = coord
            newAxie.posIdx = pos

    def set_position(self, axie, pos):
        if pos == 1:
            self.position[1, 4], coord = axie.axieIdx, [1, 4]
        elif pos == 2:
            self.position[0, 3], coord = axie.axieIdx, [0, 3]
        elif pos == 3:
            self.position[2, 3], coord = axie.axieIdx, [2, 3]
        elif pos == 4:
            self.position[1, 2], coord = axie.axieIdx, [1, 2]
        elif pos == 5:
            self.position[0, 1], coord = axie.axieIdx, [0, 1]
        elif pos == 6:
            self.position[2, 1], coord = axie.axieIdx, [2, 1]
        elif pos == 7:
            self.position[1, 0], coord = axie.axieIdx, [1, 0]
        return coord if coord else None

    def hand_in_one_card(self, axie, card): #  输入卡
        flagFirstTime = 1
        cnt = 0
        for i in range(4):
            if axie.cards[i] == card and axie.cardsNow[i]>0 and \
                    self.energy>0 and axie.cardsNow[i]>0 and flagFirstTime and \
                    axie.cardsDisable[i] and len(axie.cardChain)<4:
                cnt += 1
                self.addSpecialCard(axie, card.cardName)
                axie.cardChain.append(card)
                axie.cardsNow[i] -= 1
                self.energy -= int(card.cost)
                flagFirstTime = 0
                self.thisRound.roundTotalCard += 1
                if card.pos not in self.thisRound.cardPosList:
                    if type(card.pos) is list:
                        self.thisRound.cardPosList.extend(card.pos)
                    else:
                        self.thisRound.cardPosList.append(card.pos)
                break
            else:
                if cnt == 4:
                    print("查无此卡")

    def addSpecialCard(self, axie, cardName):
        # tirgger once
        if cardName == 'anestheticBait':
            axie.addCardInfo[cardName] = 1
        if cardName == 'carrotHammer':
            axie.addCardInfo[cardName] = 1
        if cardName == 'jarBarrage':
            axie.addCardInfo[cardName] = 1
        if cardName == 'stickyGoo':
            axie.addCardInfo[cardName] = 1
        # others
        elif cardName == 'jugglingBalls':
            axie.addCardInfo[cardName] = 1
        elif cardName == 'tripleThreat':
            axie.addCardInfo[cardName] = 1
        elif cardName == 'twinNeedle':
            axie.addCardInfo[cardName] = 1
        elif cardName == 'ivoryChop':
            axie.addCardInfo[cardName] = 1

    def if_ready_to_go(self):
        if self.axieNum == 3:
            cardsInTotal = 0
            for i in range(3):
                cardsInTotal += len(self.axies[i].cards)
        return self.axieNum == 3 and np.sum(self.position) == -13 and cardsInTotal == 12

class Axie():
    # Mouth, Horn, Back, Tail, Eyes & Ears, .
    def __init__(self, aProp, bodyParts, ID, lv = 1):
        #basic
        self.ID = ID
        self.lv = lv
        self.aProp = aProp
        self.bodyParts = bodyParts
        self.health = 0
        self.speed = 0
        self.skill = 0
        self.moral = 0
        self.cards = [] #  自己的卡牌
        self.team = None
        self.axieIdx = None
        self.pos = None
        self.posIdx = None
        self.prop()
        #dynamic
        self.IDIdx = None
        self.cardChain = [] #出的牌
        self.cardsNum = [2, 2, 2, 2] #剩余各种卡的数量
        self.cardsNow = [0, 0, 0, 0]
        self.avaiableCards = [0, 0, 0, 0]
        self.cardsDisable = [1, 1, 1, 1]
        self.addCardInfo = {}
        self.roundDefend = 0
        self.roundSpeed = self.speed
        self.roundMoral = self.moral
        self.hp = 0
        self.maxHp = 0
        self.canHeal = 1
        self.lastStand = 0
        self.lastStandTicks = 0
        self.buff = {} #{'attackUp':[0/1/2]} 0 一次攻击，1一轮攻击，2下一轮
        self.debuff = {} #
        self.cardFlagForBuff = 0
        self.posInfo = []
        self.roundNum = None

    def prop(self):
        basicProp = pd.read_csv('./csv/basicProp.csv', index_col='class')
        cardProp = pd.read_csv('./csv/cardProp.csv', index_col='class')
        axieSkill = pd.read_csv('./csv/cardSkill.csv')
        self.health += basicProp.loc[self.aProp]['health']
        self.speed += basicProp.loc[self.aProp]['speed']
        self.skill += basicProp.loc[self.aProp]['skill']
        self.moral += basicProp.loc[self.aProp]['morale']
        for i in range(6):
            try:
                card = self.bodyParts[i]
                cardClass = axieSkill[axieSkill.card == card].iloc[0, 3]
                self.health += cardProp.loc[cardClass]['health']
                self.speed += cardProp.loc[cardClass]['speed']
                self.skill += cardProp.loc[cardClass]['skill']
                self.moral += cardProp.loc[cardClass]['morale']
                if i <= 3:
                    eval('self.addCard('+card+')')
            except:
                part = self.bodyParts[i]
                try:
                    cardClass = axieSkill[axieSkill.part == part].iloc[0, 3]
                except:
                    pdb.set_trace()
                self.health += cardProp.loc[cardClass]['health']
                self.speed += cardProp.loc[cardClass]['speed']
                self.skill += cardProp.loc[cardClass]['skill']
                self.moral += cardProp.loc[cardClass]['morale']
                if i <= 3:
                    card = axieSkill[axieSkill.part == part].iloc[0, 1]
                    eval('self.addCard('+card+')')

    def if_vaild_axie(self):
        return self.speed+self.skill+self.moral+self.health == 164

    def addCard(self, card):
        self.cards.append(card)

    def cal_health(self, state='pvp'):
        if state=='pvp':
            self.hp = self.health*6+150
            self.maxHp = self.health*6+150

    def last_stand(self, remain, excessDamage):
        moraleModifier = (remain*self.roundMoral)/100
        if excessDamage<moraleModifier and chill.skill(self):
            self.lastStand = 1
            self.lastStandTicks = math.floor(self.moral/20)

    def cards_disable(self, card):
        idx = self.cards.index(card)
        self.cardsDisable[idx] = 0

    def cards_enable(self):
        self.cardsDisable = [1, 1, 1, 1]

    def avaiable_cards(self):
        for idx, item in enumerate(self.cardsNow):
            if item > 0 and self.cardsDisable[idx]:
                self.avaiableCards[idx] = 1
            else:
                self.avaiableCards[idx] = 0
