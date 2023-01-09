import random, math
from .cards import *
from .buff_debuff import *
import pdb

class Attack():
    def __init__(self, axie, target, card, rnd):
        self.axie = axie
        self.target = target
        self.card = card
        self.is_cridical = 0
        self.can_critical = 1
        #!!!!!
        self.critiDamage = min((math.sqrt(axie.roundMoral)*10+axie.roundMoral*0.4-18)/100, 1)
        #!!!
        self.increaceCritiChance = 0
        self.miss = 0
        self.rnd = rnd
        self.cardSkillCoeff = 0
        self.targetCardSkillCoeff = 0
        if self.rnd.hasAxieDie == 0 or card.attack==0:
            card.skill(axie, target, [rnd, self], 'attack')
        self.beforeEveryAttack()
        k, b = self.coeff()
        self.attack = math.floor(k*(card.attack)+b)

    def beforeEveryAttack(self):
        if 'beforeEveryAttack' in self.rnd.cardPosList:
            for team in self.rnd.axieAlive:
                for a in team:
                    for card in a.cardChain:
                        if self.rnd.hasAxieDie == 0 or card.attack==0:
                            card.skill([a, self.axie], self.target, [self.rnd, self], 'beforeEveryAttack')

    def axie_cycle(self):
        cycle = [['reptile', 'plant', 'dusk'], # 0克1，1克2，2克0
                 ['aquatic', 'bird', 'dawn'],
                 ['beast', 'bug', 'mech']]
        axie, target = None, None
        for i in range(3):
            for j in range(3):
                if cycle[i][j] == self.card.cProp:
                    axie = i
                if cycle[i][j] == self.target.aProp:
                    target = i
        if axie-target == -1 or axie-target == 2:
            return 0.15
        elif axie-target == 1 or axie-target == -2:
            return -0.15
        else:
            return 0

    def combo(self):
        if len(self.axie.cardChain)>=2:
            #!!!!!
            return self.card.attack*(self.axie.skill*0.55-12.25)/100
            #!!!
        else:
            return 0

    def match_class(self):
        if self.axie.aProp == self.card.cProp:
            return 0.1
        else:
            return 0

    def critical(self): #morale modifier
        def cal_rate(roundMoral):
            return 0.00125*roundMoral*(1+self.increaceCritiChance)
        if self.is_cridical == 0 and self.can_critical == 1:
            if random.random()<cal_rate(self.axie.roundMoral):
                self.is_cridical = 1
                return self.critiDamage
            else:
                return 0
        else:
            if self.is_cridical == 1 and self.can_critical==1:
                return self.critiDamage
            else:
                return 0

    def buff(self):
        #attackUp 0.2*/0, attackDown, fear, jinx, stun
        buffListAxie = []
        #fragile, lethal
        buffListTarget = []
        buffListAxie.append(attackUp.skill(self.axie))
        buffListAxie.append(attackDown.skill(self.axie))
        buffListAxie.append(fear.skill(self.axie))
        buffListTarget.append(fragile.skill(self.target))
        buffListAxie.append(jinx.skill(self.axie))
        buffListTarget.append(lethal.skill(self.target))
        buffListAxie.append(stun.skill(self.axie))
        if buffListAxie[3] == 0:
            self.can_critical = 0
        if buffListTarget[1] == 1:
            self.is_cridical = 1
        if self.can_critical == 0:
            buffListTarget[1] = 0
        return buffListAxie, buffListTarget

    def coeff(self):
        buffAxie, buffTarget = self.buff()
        if buffAxie[2] == 0 or buffAxie[4] == 0:
            k, b = 0, 0
            self.miss = 1
        else:
            k = (self.axie_cycle()+1)*(self.match_class()+1)*(self.critical()+1)*(self.targetCardSkillCoeff+1)*\
                (buffAxie[0]+1)*(buffAxie[1]+1)*(self.cardSkillCoeff+1) # +buffTarget[0]
            b = self.combo()
        return k, b

class Defend():
    def __init__(self, rnd):
        self.cardSkillCoeff = 0
        self.rnd = rnd
        self.axieAlive = rnd.axieAlive
        self.defend()

    def match_class(self, axie, card):
        if axie.aProp == card.cProp:
            return 0.1
        else:
            return 0

    def cardChain(self, axie, cProp, team):
        import copy
        idx = team.index(axie)
        teamMember = copy.copy(team)
        teamMember.pop(idx)
        for axie in teamMember:
            for card in axie.cardChain:
                if card.cProp == cProp:
                    return 0.05
        return 0

    def defend(self):
        for team in self.axieAlive:
            for axie in team:
                axie.roundDefend = 0
                for card in axie.cardChain:
                    self.cardSkillCoeff = 0
                    card.skill(axie, self, self.rnd, 'defend')
                    matchCoeff = self.match_class(axie, card)
                    chainCoeff = self.cardChain(axie, card.cProp, team)
                    axie.roundDefend += round((1+matchCoeff+chainCoeff+self.cardSkillCoeff)*card.defend) #
        if 'afterDefend' in self.rnd.cardPosList:
            for team in self.axieAlive:
                for axie in team:
                    for card in axie.cardChain:
                        self.cardSkillCoeff = 0
                        card.skill(axie, self, self.rnd, 'afterDefend')

class Speed():
    def __init__(self):
        self.cardSkillCoeff = 0

    def roundSpeed(self, axieAlive, roundTotalCard, roundNum):
        if roundTotalCard != 0 or roundNum==1:
            for team in axieAlive:
                for axie in team:
                    self.speed(axie)

    def speed(self, axie):
        for card in axie.cardChain:
            card.skill(axie, [None, self], None, 'speed')
        speedCoeff = 1+speedDown.skill(axie)+speedUp.skill(axie)+self.cardSkillCoeff
        axie.roundSpeed = round(speedCoeff*axie.speed)
        self.cardSkillCoeff = 0

class Morale():
    def roundMorale(self, axieAlive):
        for team in axieAlive:
            for axie in team:
                self.morale(axie)

    def morale(self, axie):
        moralCoeff = 1+moralDown.skill(axie)+moralUp.skill(axie)
        axie.roundMoral = round(moralCoeff*axie.moral)


