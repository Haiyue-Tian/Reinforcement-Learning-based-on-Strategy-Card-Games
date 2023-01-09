import random, math, pdb, copy
import numpy as np
from rlcard.games.axie import attack_defend as attDefend
from .printInfo import *
from .dataOp import inputSendCards, inputDiscardCards
from rlcard.games.axie import buff_debuff as bd


class PVP():
    def __init__(self, teamLeft, teamRight, sendCardNotSpecify=False, isTestBattle=False, isRl=1):
        self.teamLeft, self.teamRight = teamLeft, teamRight
        self.set_hp_for_all_axies()
        self.teamLeft.set_energy_cardsNum()
        self.teamRight.set_energy_cardsNum()

        self.rnd = Round(teamLeft, teamRight, sendCardNotSpecify, isTestBattle, isRl)
        teamLeft.thisRound, self.teamRight.thisRound = self.rnd, self.rnd
        self.sortID()
        self.sendCardNotSpecify = sendCardNotSpecify
        self.isTestBattle = isTestBattle

    def sortID(self):
        ID = [self.teamLeft.axies[i].ID for i in range(3)]
        ID.extend([self.teamRight.axies[i].ID for i in range(3)])
        sortedID = sorted(ID)
        for axie in self.teamLeft.axies:
            axie.IDIdx = sortedID.index(axie.ID)
        for axie in self.teamRight.axies:
            axie.IDIdx = sortedID.index(axie.ID)

    def set_hp_for_all_axies(self):
        for axie in self.teamLeft.axies:
            axie.cal_health()
        for axie in self.teamRight.axies:
            axie.cal_health()


class Round():
    '''每一轮轮数更新，出牌顺序计算，击打目标计算'''
    def __init__(self, teamLeft, teamRight, sendCardNotSpecify=True, isTestBattle=False, isRl=1):
        self.roundNum = 0
        self.teamLeft = teamLeft
        self.teamRight = teamRight
        self.sendCardNotSpecify = sendCardNotSpecify
        self.isTestBattle = isTestBattle
        self.isRl = isRl
        self.ready_to_fight = self.teamLeft.if_ready_to_go() and self.teamRight.if_ready_to_go()
        self.pos = None
        self.posInfo = None
        self.roundPosInfo = None
        self.set_position()
        self.axieAlive = [copy.copy(self.teamLeft.axies),
                          copy.copy(self.teamRight.axies)]
        self.avaiable_cards()
        self.lastStand = []
        self.newLastStand = []
        self.canAddLastStand = 1
        self.roundTotalCard = 0
        self.noAxieAttackRound = None
        self.ATT = None
        self.isAxieLastCard = False
        self.isRoundLastCard = False
        self.attOrder = self.order()
        self.remain = None
        self.miss = 1
        self.cardPosList = []
        self.card = None
        self.attackAxie, self.defendAxie = None, None
        self.send_card(self.teamLeft, 6)
        self.send_card(self.teamRight, 6)
        self.hasAxieDie = 0
        self.firstAttack = 1

    def avaiable_cards(self):
        for team in self.axieAlive:
            for axie in team:
                axie.avaiable_cards()

    def mirror_for_right(self, pos):
        # 1,4-1,0|0,3-0,1|2,3-2,1|1,2-1,2
        if pos == [1,4]: pos=[1,0+5]
        elif pos == [1,0]: pos=[1,4+5]
        elif pos == [0,3]: pos=[0,1+5]
        elif pos == [0,1]: pos=[0,3+5]
        elif pos == [2,3]: pos=[2,1+5]
        elif pos == [2,1]: pos=[2,3+5]
        elif pos == [1,2]: pos=[1,2+5]
        return pos

    def set_position(self):
        teamRightPos = np.array([np.flipud(self.teamRight.position[0]),
                                 np.flipud(self.teamRight.position[1]),
                                 np.flipud(self.teamRight.position[2])])
        self.pos = np.hstack((self.teamLeft.position, teamRightPos))
        self.posInfo = []
        for i in range(3):
            for j in range(3):
                curLeftPos, curRightPos = self.teamLeft.axies[i].pos, self.mirror_for_right(self.teamRight.axies[j].pos)
                dis = (curLeftPos[0]-curRightPos[0])**2+(curLeftPos[1]-curRightPos[1])**2
                self.posInfo.append([self.teamLeft.axies[i], self.teamRight.axies[j], dis])

    def nextRound(self):
        '''teamLeftCards = axie.card'''
        if (self.roundNum == 0 and self.ready_to_fight) or self.roundNum>0:
            self.roundNum += 1
            self.noAxieAttackRound = 1
            #cards enable
            self.cards_enable()
            #round morale
            morale = attDefend.Morale()
            morale.roundMorale(self.axieAlive)
            #defend
            defend = attDefend.Defend(self)
            self.roundPosInfo = [copy.copy(item) for item in self.posInfo]
            #order
            attOrder = self.order()
            #attack
            self.attack(attOrder) #对着一个target输出
            #nextRound
            self.readyForNextRound()

    def cards_enable(self):
        for team in self.axieAlive:
            for axie in team:
                axie.cards_enable()

    def order(self):
        attOrder = []
        speed = attDefend.Speed()
        speed.roundSpeed(self.axieAlive, self.roundTotalCard, self.roundNum)
        for i in range(3):
            if self.teamLeft.axies[i] in self.axieAlive[0]:
                attOrder.append((self.teamLeft.axies[i], 'left', self.teamLeft.axies[i].roundSpeed,
                                 self.teamLeft.axies[i].hp, self.teamLeft.axies[i].skill,
                                 self.teamLeft.axies[i].moral, self.teamLeft.axies[i].ID))
        for i in range(3):
            if self.teamRight.axies[i] in self.axieAlive[1]:
                attOrder.append((self.teamRight.axies[i], 'right', self.teamRight.axies[i].roundSpeed,
                                 self.teamRight.axies[i].hp, self.teamRight.axies[i].skill,
                                 self.teamRight.axies[i].moral, self.teamRight.axies[i].ID))
        attOrder = sorted(attOrder, key=lambda x:(-x[2], x[3], -x[4], -x[5], x[6]))
        self.attOrder = attOrder
        return attOrder

    def card_skill_multiTimesAttack(self):
        if 'multiTimesAttack' in self.cardPosList:
            for team in self.axieAlive:
                for axie in team:
                    for card in axie.cardChain:
                        card.skill(axie, None, self, 'multiTimesAttack')

    def attack(self, attOrder):
        printInfo(self)
        self.card_skill_multiTimesAttack()
        for axieTuple in attOrder:
            if axieTuple[0] in self.axieAlive[0] or axieTuple[0] in self.axieAlive[1]:
                target = self.selectTarget(axieTuple)
                if target is not None:
                    for i in range(len(axieTuple[0].cardChain)):
                        if self.is_alive(axieTuple[0]):
                            self.card = axieTuple[0].cardChain[i]
                            if self.is_alive(target) or self.card.attack == 0:
                                self.attackAxie, self.defendAxie = axieTuple[0], target
                                RndDefBeforeAtt = target.roundDefend>0
                                self.noAxieAttackRound = 0
                                self.isAxieLastCard = i == len(axieTuple[0].cardChain)
                                card = axieTuple[0].cardChain[i]
                                self.damage(axieTuple[0], target, card)
                                poisonAxie = self.other_op()
                                RndDefAfterAtt = target.roundDefend==0
                                isSheildBreak = RndDefBeforeAtt and RndDefAfterAtt
                                if self.is_alive(target):
                                    self.last_stand_ticks_minus()
                                if self.hasAxieDie == 0 or card.attack == 0:
                                    card.skill(axieTuple[0], target, self, 'afterAttack')
                                self.card_skill_after_every_attack(target, axieTuple[0], card, isSheildBreak)
                                printInfo(self)
                                self.card = None
                                self.axie_die(poisonAxie)
                                self.attackAxie, self.defendAxie = None, None
                                self.firstAttack = 0
                    self.hasAxieDie = 0
        self.isRoundLastCard = True

    def card_skill_final_clearRoundInfo(self):
        for team in self.axieAlive:
            for axie in team:
                for card in axie.cardChain:
                    card.skill(axie, None, self, 'final')
                axie.cardChain = []
                axie.roundDefend = 0
                axie.avaiable_cards()

    def card_skill_after_every_attack(self, target, axie, attackCard, isSheildBreak):
        if 'beingAttacked' in self.cardPosList:
            for card in target.cardChain:
                card.skill(target, [axie, attackCard, isSheildBreak], self, 'beingAttacked')
        if 'afterAnyAttack' in self.cardPosList:
            for card in axie.cardChain:
                card.skill(axie, self.ATT.is_cridical, self, 'afterAnyAttack')
        if 'afterAnyAttackSearchAll' in self.cardPosList:
            for team in self.axieAlive:
                for a in team:
                    for card in a.cardChain:
                        card.skill(a, None, self, 'afterAnyAttackSearchAll')


    def other_op(self):
        poisonAxie = bd.poison.skill(self.axieAlive)
        for team in self.axieAlive:
            for axie in team:
                bd.fear.skill(axie)
        return poisonAxie


    def axie_die(self, poisonAxie=None):
        for i in range(len(self.axieAlive)):
            team = copy.copy(self.axieAlive[i])
            for j in range(len(team)):
                target = team[j]
                if target.hp == 0 and target.lastStand == 0:
                    idx = self.axieAlive[i].index(target)
                    target.team.sendCardThisRound += sum(target.cardsNum)
                    self.axieAlive[i][idx].cardsNow= [0,0,0,0]
                    self.axieAlive[i][idx].cardsNum= [2,2,2,2]
                    self.axieAlive[i][idx].debuff = {}
                    self.axieAlive[i][idx].buff = {}
                    self.axieAlive[i][idx].cardChain = []
                    self.axieAlive[i].pop(idx)
                    self.hasAxieDie = 1
                    if target in self.lastStand:
                        popAxie = []
                        for i in range(len(self.lastStand)):
                            if target == self.lastStand[i]:
                                popAxie.append(self.lastStand[i])
                        for pAxie in popAxie:
                            self.lastStand.remove(pAxie)

        if poisonAxie!=None:
            for axie in poisonAxie:
                if axie.hp == 0 and axie.lastStand == 0:
                    for i in range(2):
                        if axie in self.axieAlive[i]:
                            idx = self.axieAlive[i].index(axie)
                            target.team.sendCardThisRound += sum(target.cardsNum)
                            self.axieAlive[i][idx].cardsNow= [0,0,0,0]
                            self.axieAlive[i][idx].cardsNum= [2,2,2,2]
                            self.axieAlive[i][idx].debuff = {}
                            self.axieAlive[i][idx].buff = {}
                            self.axieAlive[i][idx].cardChain = []
                            self.axieAlive[i].pop(idx)
                            self.hasAxieDie = 1
                            if axie in self.lastStand:
                                idx = self.lastStand.index(axie)
                                self.lastStand.pop(idx)
        # pdb.set_trace()
        printInfo(self)

    def damage(self, axie, target, card):
        def is_miss_defend(axie, target, card, att):
            if att != 0:
                is_stun = bd.stun.skill(target)
                is_sleep = bd.sleep.skill(target)
                card.skill(axie, target, self, 'missDefend')
                if is_stun == 0 or is_sleep == 0 or self.miss == 0:
                    return True
                else:
                    return False
            else: return False

        ATT = attDefend.Attack(axie, target, card, self)
        att = ATT.attack
        self.ATT = ATT
        if target.lastStand == 1:
            target.lastStandTicks -= 1
        else:
            missSheild = is_miss_defend(axie, target, card, att)
            if missSheild:
                self.remain = -att
            else:
                beforeAttack = target.roundDefend>0
                self.remain = target.roundDefend - att
                afterAttack = self.remain<=0
                self.card_skill_no_more_damage(axie, target, beforeAttack and afterAttack)
                target.roundDefend = self.remain if self.remain>=0 else 0
            if (target.roundDefend == 0 and target.lastStand == 0) or missSheild:
                targetBeforeHp = target.hp
                target.hp = target.hp+self.remain
                card.skill(axie, target, self, 'lastStandEnd')
                self.add_last_stand(target, targetBeforeHp)
        self.miss = 1

    def card_skill_no_more_damage(self, axie, target, isSheildBreak):
        if 'noMoreDamage' in self.cardPosList:
            for card in target.cardChain:
                card.skill(axie, target, [self, isSheildBreak], 'noMoreDamage')


    def add_last_stand(self, target, targetRemainHp):
        if target.hp<0:
            excessDamage = 0-target.hp
            target.hp = 0
            if self.canAddLastStand == 1:
                target.last_stand(targetRemainHp, excessDamage)
                if target.lastStand == 1:
                    self.lastStand.append(target)
                    self.newLastStand.append(target)
        self.canAddLastStand = 1

    def last_stand_ticks_minus(self):
        for axie in self.lastStand: #扣血
            if axie in self.newLastStand:
                idx = self.newLastStand.index(axie)
                self.newLastStand.pop(idx)
            else:
                axie.lastStandTicks -= 1
                if axie.lastStandTicks <= 0:
                    axie.lastStand = 0
                    axie.lastStandTicks = 0
                    popAxie = []
                    for i in range(len(self.lastStand)):
                        if self.lastStand[i] == axie:
                            popAxie.append(self.lastStand[i])
                    for axie in popAxie:
                        self.lastStand.remove(axie)


    def selectTarget(self, axieTuple):
        def input_posInfo_from_axie(roundPosInfo, teamIdx):
            for axie in self.axieAlive[teamIdx]:
                if axie.posInfo != []:
                    for line in axie.posInfo:
                        for i in range(len(roundPosInfo)):
                            lineRpi = roundPosInfo[i]
                            if line[0] in lineRpi and line[1] in lineRpi:
                                roundPosInfo[i][2] = line[2]
            return roundPosInfo

        targetCandi, minDis = [], 100
        roundPosInfo = [ copy.copy(item) for item in self.roundPosInfo]
        try:
            axieTuple[0].cardChain[0].skill(axieTuple[0], None, self, 'target')
        except:
            pass
        self.card_skill_defend_target(axieTuple[0])
        if axieTuple[1] == 'left':
            roundPosInfo = input_posInfo_from_axie(roundPosInfo, 1)
            for i in range(3):
                if self.teamLeft.axies[i] == axieTuple[0]:
                    break
            for j in range(3):
                idx = i*3+j
                if roundPosInfo[idx][2]<minDis and self.is_alive(roundPosInfo[idx][1]):
                    minDis = roundPosInfo[idx][2]
                    targetCandi = [roundPosInfo[idx][1]]
                elif roundPosInfo[idx][2]==minDis and self.is_alive(roundPosInfo[idx][1]):
                    targetCandi.append(roundPosInfo[idx][1])
        else:
            roundPosInfo = input_posInfo_from_axie(roundPosInfo, 0)
            for i in range(3):
                if self.teamRight.axies[i] == axieTuple[0]:
                    break
            for j in range(3):
                idx = i+j*3
                if roundPosInfo[idx][2]<minDis and self.is_alive(roundPosInfo[idx][0]):
                    minDis = roundPosInfo[idx][2]
                    targetCandi = [roundPosInfo[idx][0]]
                elif roundPosInfo[idx][2]==minDis and self.is_alive(roundPosInfo[idx][0]):
                    targetCandi.append(roundPosInfo[idx][0])
        rand = 0 if random.random()<0.5 else 1
        try:
            target = targetCandi[rand] if len(targetCandi)==2 else targetCandi[0]
        except:
            target = None
        return target

    def card_skill_defend_target(self, target):
        if 'defendTarget' in self.cardPosList:
            for i in range(len(self.axieAlive)):
                team = self.axieAlive[i]
                for j in range(len(team)):
                    axie = team[j]
                    for card in axie.cardChain:
                        card.skill(axie, target, self, 'defendTarget')

    def if_discard_card(self, team):
        cnt = 0
        for axie in team.axies:
            cnt += sum(axie.cardsNow)
        if cnt > 9:
            self.discard_card(team, cnt-9)

    def readyForNextRound(self, state='pvp'):
        if state=='pvp':
            self.teamLeft.energy = self.teamLeft.energy+2 if self.teamLeft.energy+2<10 else 10
            self.teamRight.energy = self.teamRight.energy+2 if self.teamRight.energy+2<10 else 10

            self.teamLeft.cardsNum -= self.teamLeft.sendCardThisRound
            self.teamRight.cardsNum -= self.teamRight.sendCardThisRound
            self.teamLeft.sendCardThisRound = 0
            self.teamRight.sendCardThisRound = 0
            self.send_card(self.teamLeft, 3)
            self.send_card(self.teamRight, 3)
            self.if_discard_card(self.teamLeft)
            self.if_discard_card(self.teamRight)

            #动态特性清零
            #Axie
            self.card_skill_final_clearRoundInfo()
            printInfo(self, False)
            if self.roundNum>=10:
                for team in self.axieAlive:
                    for axie in team:
                            damage = (self.roundNum-10)*30+50
                            tmp = axie.hp - damage
                            axie.hp = tmp if tmp>0 else 0
                self.axie_die()
            if self.isRl == 0:
                pdb.set_trace()
        else:#pve
            pass
        self.isAxieLastCard = False
        self.isRoundLastCard = False
        self.canAddLastStand = 1
        self.cardPosList = []
        self.firstAttack = 1
        self.roundTotalCard = 0
        for team in self.axieAlive:
            for axie in team:
                axie.addCardInfo = {}
                if axie.roundNum is not None:
                    if self.roundNum - axie.roundNum == 1:
                        axie.canHeal = 1
                        axie.roundNum = None
                axie.posInfo = []
                if self.noAxieAttackRound == 0:
                    bd.speedUp.skill(axie, 1)
                    bd.speedDown.skill(axie, 1)
                    bd.attackUp.skill(axie, 1)
                    bd.attackDown.skill(axie, 1)
                    bd.moralUp.skill(axie, 1)
                    bd.moralDown.skill(axie, 1)
                    bd.chill.skill(axie, 1)
                    bd.jinx.skill(axie, 1)
                    bd.stench.skill(axie, self, 1)
                    bd.aroma.skill(axie, self, 1)
        printInfo(self)

    def send_card(self, team, num):
        def randomSendCard(team, num):
            axieAlive, countAxie = [], 0
            for j in range(3):
                if self.is_alive(team.axies[j]):
                    axieAlive.append(team.axies[j])
                    countAxie += 1
            items = []
            for i in range(len(axieAlive)):
                if sum(axieAlive[i].cardsNum) == 0:
                    items.append(axieAlive[i])
                    countAxie -= 1
            for item in items:
                axieAlive.remove(item)
            for i in range(num):
                if axieAlive != []:
                    axieRand = math.floor(countAxie*random.random())
                    cardsExist, countCards = [], 0
                    for j in range(4):
                        if axieAlive[axieRand].cardsNum[j]>0:
                            cardsExist.append(axieAlive[axieRand].cards[j])
                            countCards += 1
                    cardRand = math.floor(countCards*random.random())
                    idx = axieAlive[axieRand].cards.index(cardsExist[cardRand])
                    axieAlive[axieRand].cardsNow[idx] += 1
                    axieAlive[axieRand].team.sendCardThisRound += 1
                    axieAlive[axieRand].cardsNum[idx] -= 1
                    if sum(axieAlive[axieRand].cardsNum) == 0:
                        axieAlive.pop(axieRand)
                        countAxie -= 1

        def mustSendCard(team, num):
            cnt = 0
            idx = 0 if self.teamLeft == team else 1
            card = []
            for axie in self.axieAlive[idx]:
                cnt += sum(axie.cardsNum)
            if cnt<=num:
                for axie in self.axieAlive[idx]:
                    if len(axie.cardsNum)>0:
                        for i in range(4):
                            cardNum = axie.cardsNum[i]
                            if cardNum>0:
                                axie.cardsNow[i] += cardNum
                                team.sendCardThisRound += 1
                                axie.cardsNum[i] -= cardNum
                                num -= cardNum
                                card.append([axie, i, cardNum])
                for axie in self.axieAlive[idx]:
                    for axie in self.axieAlive[idx]:
                        for i in range(4):
                            axie.cardsNum[i] = 2 - axie.cardsNow[i]
                            team.sendCardThisRound -= axie.cardsNum[i]
            return num, card

        printInfo(self, False)
        numOri = num
        num, card = mustSendCard(team, num)
        if self.isRl == 0:
            num = inputSendCards(self, team, num, card, self.sendCardNotSpecify, self.isTestBattle, numOri)
        randomSendCard(team, num)


    def discard_card(self, team, num):
        def randomDiscardCard(team, num):
            axieAlive, countAxie = [], 0
            for j in range(3):
                if self.is_alive(team.axies[j]):
                    axieAlive.append(team.axies[j])
                    countAxie += 1
            items = []
            for i in range(len(axieAlive)):
                if sum(axieAlive[i].cardsNow) == 0:
                    items.append(axieAlive[i])
                    countAxie -= 1
            for item in items:
                axieAlive.remove(item)
            for i in range(num):
                if axieAlive != []:
                    axieRand = math.floor(countAxie*random.random())
                    cardsExist, countCards = [], 0
                    for j in range(4):
                        if axieAlive[axieRand].cardsNow[j]>0:
                            cardsExist.append(axieAlive[axieRand].cards[j])
                            countCards += 1
                    cardRand = math.floor(countCards*random.random())
                    idx = axieAlive[axieRand].cards.index(cardsExist[cardRand])
                    axieAlive[axieRand].cardsNow[idx] -= 1
                    if sum(axieAlive[axieRand].cardsNow) == 0:
                        axieAlive.pop(axieRand)
                        countAxie -= 1

        printInfo(self, False)
        if self.isRl == 0:
            num = inputDiscardCards(self, team, num, self.sendCardNotSpecify)
        randomDiscardCard(team, num)

    def is_alive(self, axie):
        return axie.hp>0 or axie.lastStand
