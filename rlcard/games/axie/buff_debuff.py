import copy, pdb

'''
buff and debuff
'''

class Buff():
    def __init__(self):
        self.typeBuff = 'buff'
        self.buffName = None

    def skill(self, axie, isLastCard=0):
        cnt = 0
        if isLastCard == 0:
            axie.cardFlagForBuff = 1
        if self.buffName in axie.buff.keys():
            idx0, idx1 = 0, 0
            for i in range(len(axie.buff[self.buffName])):
                cnt += 1
                if axie.cardFlagForBuff:
                    for j in range(len(axie.buff[self.buffName])):
                        if axie.buff[self.buffName][j] == 0:
                            idx0 += 1
                    axie.cardFlagForBuff = 0
                elif axie.buff[self.buffName][i] == 1:
                    if isLastCard == 1:
                        idx1 += 1
                elif axie.buff[self.buffName][i] == 2:
                    if isLastCard == 1:
                        axie.buff[self.buffName][i] = 1
            for i in range(idx0):
                axie.buff[self.buffName].remove(0)
            for i in range(idx1):
                axie.buff[self.buffName].remove(1)
            if len(axie.buff[self.buffName]) == 0:
                del axie.buff[self.buffName]
            return 0.2*cnt
        else:
            axie.cardFlagForBuff = 0
            return 0

    def add_axie(self, axie, flag):
        speed = ['speedUp', 'speedDown']
        moral = ['moralUp', 'moralDown']
        attack = ['attackUp', 'attackDown']
        if self.buffName in axie.buff.keys():
            if len(axie.buff[self.buffName]) < 5:
                for item in [speed, moral, attack]:
                    if self.buffName in item:
                        if item[1] in axie.debuff.keys():
                            minimum = min(axie.debuff[item[1]])
                            axie.debuff[item[1]].remove(minimum)
                        else:
                            axie.buff[self.buffName].append(flag)#0, 1, 2
        else:
            for item in [speed, moral, attack]:
                if self.buffName in item:
                    if item[1] in axie.debuff.keys():
                        minimum = min(axie.debuff[item[1]])
                        axie.debuff[item[1]].remove(minimum)
                        if axie.debuff[item[1]] == []:
                            del axie.debuff[item[1]]
                    else:
                        axie.buff[self.buffName] = [flag] #0, 1, 2
        if flag == 0:
            axie.cardFlagForBuff = 1

class Debuff():
    def __init__(self):
        self.typebuff = 'debuff'
        self.debuffName = None

    def skill(self, axie, isLastCard=0):
        cnt = 0
        if isLastCard == 0:
            axie.cardFlagForBuff = 1
        if self.debuffName in axie.debuff.keys():
            idx0, idx1 = 0, 0
            for i in range(len(axie.debuff[self.debuffName])):
                cnt += 1
                if axie.cardFlagForBuff:
                    for j in range(len(axie.debuff[self.debuffName])):
                        if axie.debuff[self.debuffName][j] == 0:
                            idx0 += 1
                    axie.cardFlagForBuff = 0
                elif axie.debuff[self.debuffName][i] == 1:
                    if isLastCard == 1:
                        idx1 += 1
                elif axie.debuff[self.debuffName][i] == 2:
                    if isLastCard == 1:
                        axie.debuff[self.debuffName][i] = 1
            for i in range(idx0):
                axie.debuff[self.debuffName].remove(0)
            for i in range(idx1):
                axie.debuff[self.debuffName].remove(1)
            if len(axie.debuff[self.debuffName]) == 0:
                del axie.debuff[self.debuffName]
            return -0.2*cnt
        else:
            axie.cardFlagForBuff = 0
            return 0

    def add_axie(self, axie, flag):
        speed = ['speedUp', 'speedDown']
        moral = ['moralUp', 'moralDown']
        attack = ['attackUp', 'attackDown']
        if self.debuffName in axie.debuff.keys():
            if len(axie.debuff[self.debuffName]) < 5 or self.debuffName == 'poison':
                for item in [speed, moral, attack]:
                    if self.debuffName in item:
                        if item[0] in axie.buff.keys():
                            minimum = min(axie.buff[item[0]])
                            axie.buff[item[0]].remove(minimum)
                        else:
                            axie.debuff[self.debuffName].append(flag)#0, 1, 2
        else:
            for item in [speed, moral, attack]:
                if self.debuffName in item:
                    if item[0] in axie.buff.keys():
                        minimum = min(axie.buff[item[0]])
                        axie.buff[item[0]].remove(minimum)
                        if axie.buff[item[0]] == []:
                            del axie.buff[item[0]]
                    else:
                        axie.debuff[self.debuffName] = [flag] #0, 1, 2
        if flag == 0:
            axie.cardFlagForBuff = 1

class DebuffNotStackable():
    def __init__(self):
        self.typebuff = 'debuff'
        self.debuffName = None

    def add_axie(self, axie, flag):
        axie.debuff[self.debuffName] = flag #0, 1, 2

class AttackUp(Buff):
    def __init__(self):
        super().__init__()
        self.buffName = 'attackUp'

class MoraleUp(Buff):
    def __init__(self):
        super().__init__()
        self.buffName = 'moraleUp'

class SpeedUp(Buff):
    def __init__(self):
        super().__init__()
        self.buffName = 'speedUp'

class AttackDown(Debuff):
    def __init__(self):
        super().__init__()
        self.debuffName = 'attackDown'

class MoraleDown(Debuff):
    def __init__(self):
        super().__init__()
        self.debuffName = 'moraleDown'

class SpeedDown(Debuff):
    def __init__(self):
        super().__init__()
        self.debuffName = 'speedDown'

class Aroma(DebuffNotStackable):
    def __init__(self):
        super().__init__()
        self.debuffName = 'aroma'

    def minusDis(self, axie, thisRound):
        minDis, idx = 1000, None
        flag = 1
        for i in range(len(thisRound.roundPosInfo)):
            line = thisRound.roundPosInfo[i]
            if minDis>line[2]:
                minDis = line[2]
        for i in range(len(thisRound.roundPosInfo)):
            line = thisRound.roundPosInfo[i]
            if axie in line:
                pos, roundPos = thisRound.posInfo, thisRound.roundPosInfo
                if flag:
                    axie.posInfo.append([line[0], line[1], minDis-1])
                    minDis = minDis-1
                    flag = 0
                else:
                    axie.posInfo.append([line[0], line[1], minDis])

    def skill(self, axie, thisRound, isLastCard=0):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                if isLastCard:
                    del axie.debuff[self.debuffName]
                else:
                    self.minusDis(axie, thisRound)

class Chill(DebuffNotStackable):#不能进last stand
    def __init__(self):
        super().__init__()
        self.debuffName = 'chill'

    def skill(self, axie, isLastCard=0):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            elif axie.debuff[self.debuffName] == 1:
                if isLastCard == 1:
                    del axie.debuff[self.debuffName]
            elif axie.debuff[self.debuffName] == 2:
                if isLastCard == 1:
                    axie.debuff[self.debuffName] = 1
            return 0
        else:
            return 1

class Fear(DebuffNotStackable):#Axie cannot attack 不确定
    def __init__(self):
        super().__init__()
        self.debuffName = 'fear'

    def skill(self, axie):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            elif axie.debuff[self.debuffName] == 1:
                axie.debuff[self.debuffName] = 0
            return 0
        else:
            return 1

class Fragile(DebuffNotStackable):#Axie receive double damage when has sheild
    def __init__(self):
        super().__init__()
        self.debuffName = 'fragile'

    def skill(self, axie):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            if axie.roundDefend > 0:
                return 1
        return 0

class Jinx(DebuffNotStackable):#Affected Axie cannot land critical hits for the next round
    def __init__(self):
        super().__init__()
        self.debuffName = 'jinx'

    def skill(self, axie, isLastCard=0):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            elif axie.debuff[self.debuffName] == 1:
                if isLastCard == 1:
                    del axie.debuff[self.debuffName]
            elif axie.debuff[self.debuffName] == 2:
                if isLastCard == 1:
                    axie.debuff[self.debuffName] = 1
            return 0
        else:
            return 1

class Lethal(DebuffNotStackable):#Next hit against affected Axie is critical
    def __init__(self):
        super().__init__()
        self.debuffName = 'lethal'

    def skill(self, axie):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            return 1
        else:
            return 0

class Poison(Debuff):
    def __init__(self):
        super().__init__()
        self.debuffName = 'poison'

    def skill(self, alive):
        poisonAxie = []
        axieAlive = copy.copy(alive[0])
        axieAlive.extend(copy.copy(alive[1]))
        for axie in axieAlive:
            if self.debuffName in axie.debuff.keys():
                if axie.lastStand == 1:
                    axie.lastStandTicks -= 1
                else:
                    axie.hp -= axie.debuff[self.debuffName]*2 #没考虑lastStand
                    if axie.hp < 0:
                        axie.hp = 0
                poisonAxie.append(axie)
        return poisonAxie

    def add_axie(self, axie):
        if self.debuffName in axie.debuff.keys():
            axie.debuff[self.debuffName] += 1
        else:
            axie.debuff[self.debuffName] = 1

class Sleep(DebuffNotStackable):
    def __init__(self):
        super().__init__()
        self.debuffName = 'sleep'

    def skill(self, axie):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            return 0
        else:
            return 1

class Stench(DebuffNotStackable):
    def __init__(self):
        super().__init__()
        self.debuffName = 'stench'

    def plusDis(self, axie, thisRound):
        maxDis, idx = -1000, None
        flag = 1
        for i in range(len(thisRound.roundPosInfo)):
            line = thisRound.roundPosInfo[i]
            if maxDis<line[2]:
                maxDis= line[2]
        for i in range(len(thisRound.roundPosInfo)):
            line = thisRound.roundPosInfo[i]
            if axie in line:
                pos, roundPos = thisRound.posInfo, thisRound.roundPosInfo
                if flag:
                    axie.posInfo.append([line[0], line[1], maxDis+1])
                    maxDis = maxDis+1
                    flag = 0
                else:
                    axie.posInfo.append([line[0], line[1], maxDis])

    def skill(self, axie, thisRound, isLastCard=0):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                if isLastCard:
                    del axie.debuff[self.debuffName]
                else:
                    self.plusDis(axie, thisRound)

class Stun(DebuffNotStackable):
    def __init__(self):
        super().__init__()
        self.debuffName = 'stun'

    def skill(self, axie):
        if self.debuffName in axie.debuff.keys():
            if axie.debuff[self.debuffName] == 0:
                del axie.debuff[self.debuffName]
            return 0
        else:
            return 1

attackUp = AttackUp() #
moralUp = MoraleUp()
speedUp = SpeedUp() #
attackDown = AttackDown() #
moralDown = MoraleDown()
speedDown = SpeedDown() #
aroma = Aroma()
chill = Chill() #
fear = Fear() #double check
fragile = Fragile() #
jinx = Jinx() #
lethal = Lethal() #
poison = Poison() #except lastStand
sleep = Sleep() #except defend
stench = Stench()
stun = Stun() #
