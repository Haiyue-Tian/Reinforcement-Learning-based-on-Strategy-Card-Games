from .team import Team, Axie
from .rules import PVP, Round
import pdb
import copy


class Public:
    def __init__(self, pvp):
        self.pvp = pvp
        self.rnd = self.pvp.rnd
        self.histCnt = 0
        self.public = {'roundNum': self.rnd.roundNum+1,
                       'cardsNum': [self.rnd.teamLeft.cardsNum,
                                    self.rnd.teamRight.cardsNum],
                       'energy': [self.rnd.teamLeft.energy,
                                  self.rnd.teamRight.energy],
                       'history': [[[[-1]*4]*3]*8, [[[-1]*4]*3]*8],
                       'team': [pvp.teamLeft, pvp.teamRight]}
        if pvp.rnd.attOrder is None:
            attOrder = [-1, -1, -1, -1, -1, -1]
        else:
            attOrder = [-1, -1, -1, -1, -1, -1]
            for i in range(len(pvp.rnd.attOrder)):
                attOrder[i] = pvp.rnd.attOrder[i][0].IDIdx
        self.public['order'] = attOrder
        self.stateCnt = -1
        self.state_history = []
        self.saveRound = {}

    def update(self, pvp):
        if pvp.rnd.attOrder is None:
            attOrder = [-1, -1, -1, -1, -1, -1]
        else:
            attOrder = [-1, -1, -1, -1, -1, -1]
            for i in range(len(pvp.rnd.attOrder)):
                attOrder[i] = pvp.rnd.attOrder[i][0].IDIdx
        self.public['roundNum'] = pvp.rnd.roundNum+1
        self.public['order'] = attOrder
        self.public['cardsNum'] = [pvp.rnd.teamLeft.cardsNum,
                                   pvp.rnd.teamRight.cardsNum]
        self.public['energy'] = [pvp.rnd.teamLeft.energy,
                                 pvp.rnd.teamRight.energy]
        self.public['team'] = [pvp.teamLeft, pvp.teamRight]

    def update_history(self, actions0, actions1):
        act0 = [[-1, -1, -1, -1],
                [-1, -1, -1, -1],
                [-1, -1, -1, -1]]
        act1 = [[-1, -1, -1, -1],
                [-1, -1, -1, -1],
                [-1, -1, -1, -1]]
        for i in range(3):
            for j in range(len(actions0[i])):
                act0[i][j] = actions0[i][j]
        for i in range(3):
            for j in range(len(actions1[i])):
                act1[i][j] = actions1[i][j]

        if self.histCnt+1 != 9:
            self.public['history'][0][self.histCnt] = act0
            self.public['history'][1][self.histCnt] = act1
            self.histCnt += 1
        else:
            self.public['history'][0].append(act0)
            self.public['history'][1].append(act1)
            self.public['history'][0].pop(0)
            self.public['history'][1].pop(0)

    def update_state(self, state, pvp):
        self.stateCnt += 1
        copyPvp = self.copy_pvp(pvp)
        self.state_history.append((state, copyPvp))

    def save_round(self, pvp):
        copyPvp = self.copy_pvp(pvp)
        self.saveRound[pvp.rnd.roundNum] = copyPvp

    def copy_pvp(self, pvp):
        def findAxie(copyPvp, oldAxie):
            if type(oldAxie) is Axie:
                for axie in copyPvp.teamLeft.axies:
                    if axie.ID == oldAxie.ID:
                        return axie
                for axie in copyPvp.teamRight.axies:
                    if axie.ID == oldAxie.ID:
                        return axie

        axie00 = Axie(pvp.teamLeft.axies[0].aProp,
                      pvp.teamLeft.axies[0].bodyParts,
                      pvp.teamLeft.axies[0].ID)
        axie01 = Axie(pvp.teamLeft.axies[1].aProp,
                      pvp.teamLeft.axies[1].bodyParts,
                      pvp.teamLeft.axies[1].ID)
        axie02 = Axie(pvp.teamLeft.axies[2].aProp,
                      pvp.teamLeft.axies[2].bodyParts,
                      pvp.teamLeft.axies[2].ID)
        axie10 = Axie(pvp.teamRight.axies[0].aProp,
                      pvp.teamRight.axies[0].bodyParts,
                      pvp.teamRight.axies[0].ID)
        axie11 = Axie(pvp.teamRight.axies[1].aProp,
                      pvp.teamRight.axies[1].bodyParts,
                      pvp.teamRight.axies[1].ID)
        axie12 = Axie(pvp.teamRight.axies[2].aProp,
                      pvp.teamRight.axies[2].bodyParts,
                      pvp.teamRight.axies[2].ID)

        team0, team1 = Team(), Team()
        team0.addAxie(axie00, pvp.teamLeft.axies[0].posIdx)
        team0.addAxie(axie01, pvp.teamLeft.axies[1].posIdx)
        team0.addAxie(axie02, pvp.teamLeft.axies[2].posIdx)
        team1.addAxie(axie10, pvp.teamRight.axies[0].posIdx)
        team1.addAxie(axie11, pvp.teamRight.axies[1].posIdx)
        team1.addAxie(axie12, pvp.teamRight.axies[2].posIdx)
        copyPvp = PVP(team0, team1, pvp.sendCardNotSpecify, pvp.isTestBattle)
        teams = [copyPvp.teamLeft, copyPvp.teamRight]
        for i in range(2):
            if i == 0:
                pvpTeam = pvp.teamLeft
            else:
                pvpTeam = pvp.teamRight
            teams[i].energy = pvpTeam.energy
            teams[i].cardsNum = pvpTeam.cardsNum
            teams[i].sendCardThisRound = pvpTeam.sendCardThisRound
            for j in range(3):
                teams[i].axies[j].cardChain = copy.deepcopy(pvpTeam.axies[j].cardChain)
                teams[i].axies[j].cardsNum = copy.deepcopy(pvpTeam.axies[j].cardsNum)
                teams[i].axies[j].cardsNow = copy.deepcopy(pvpTeam.axies[j].cardsNow)
                teams[i].axies[j].avaiableCards = copy.deepcopy(pvpTeam.axies[j].avaiableCards)
                teams[i].axies[j].cardsDisable = copy.deepcopy(pvpTeam.axies[j].cardsDisable)
                teams[i].axies[j].addCardInfo = copy.deepcopy(pvpTeam.axies[j].addCardInfo)
                teams[i].axies[j].roundDefend = pvpTeam.axies[j].roundDefend
                teams[i].axies[j].roundSpeed = pvpTeam.axies[j].roundSpeed
                teams[i].axies[j].roundMoral = pvpTeam.axies[j].roundMoral
                teams[i].axies[j].hp = pvpTeam.axies[j].hp
                teams[i].axies[j].maxHp = pvpTeam.axies[j].maxHp
                teams[i].axies[j].canHeal = pvpTeam.axies[j].canHeal
                teams[i].axies[j].lastStand = pvpTeam.axies[j].lastStand
                teams[i].axies[j].lastStandTicks = pvpTeam.axies[j].lastStandTicks
                teams[i].axies[j].buff = copy.deepcopy(pvpTeam.axies[j].buff)
                teams[i].axies[j].debuff = copy.deepcopy(pvpTeam.axies[j].debuff)
                teams[i].axies[j].cardFlagForBuff = pvpTeam.axies[j].cardFlagForBuff
                teams[i].axies[j].posInfo = pvpTeam.axies[j].posInfo
                teams[i].axies[j].roundNum = pvpTeam.axies[j].roundNum
        copyPvp.rnd.roundNum = pvp.rnd.roundNum
        copyPvp.rnd.pos = pvp.rnd.pos
        copyPvp.rnd.isRl = pvp.rnd.isRl

        copyPvp.rnd.canAddLastStand = pvp.rnd.canAddLastStand
        copyPvp.rnd.roundTotalCard = pvp.rnd.roundTotalCard
        copyPvp.rnd.noAxieAttackRound = pvp.rnd.noAxieAttackRound
        copyPvp.rnd.ATT = pvp.rnd.ATT
        copyPvp.rnd.isAxieLastCard = pvp.rnd.isAxieLastCard
        copyPvp.rnd.isRoundLastCard = pvp.rnd.isRoundLastCard
        copyPvp.rnd.remain = pvp.rnd.remain
        copyPvp.rnd.miss = pvp.rnd.miss
        copyPvp.rnd.cardPosList = pvp.rnd.cardPosList
        copyPvp.rnd.card = pvp.rnd.card
        copyPvp.rnd.hasAxieDie = pvp.rnd.hasAxieDie
        copyPvp.rnd.firstAttack = pvp.rnd.firstAttack
        axieAlive = []
        for i in range(2):
            axieAlive.append([findAxie(copyPvp, oldAxie) for oldAxie in pvp.rnd.axieAlive[i]])
        copyPvp.rnd.axieAlive = axieAlive
        copyPvp.rnd.lastStand = [findAxie(copyPvp, oldAxie) for oldAxie in pvp.rnd.lastStand]
        copyPvp.rnd.newLastStand = [findAxie(copyPvp, oldAxie) for oldAxie in pvp.rnd.newLastStand]
        copyPvp.rnd.attackAxie = findAxie(copyPvp, pvp.rnd.attackAxie)
        copyPvp.rnd.defendAxie = findAxie(copyPvp, pvp.rnd.defendAxie)
        if pvp.rnd.attOrder is not None:
            attOrder = []
            for axieTuple in pvp.rnd.attOrder:
                tmp = ()
                tmp += (findAxie(copyPvp, axieTuple[0]), )
                tmp += axieTuple[1:]
                attOrder.append(tmp)
        else:
            attOrder = None
        copyPvp.rnd.attOrder = attOrder
        return copyPvp
