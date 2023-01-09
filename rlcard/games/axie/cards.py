import numpy as np
import pandas as pd
from .dataOp import *
from .buff_debuff import *
from rlcard.games.axie import attack_defend as attDef
import copy

totalCard = 132
'''
Pos: afterAttack, beingAttacked, afterAnyAttack, beforeEveryAttack, speed,
     lastStandEnd, target, final, defendTarget, defend, afterDefend, missDefend,
     afterAnyAttackSearchAll, noMoreDamage, multiTimesAttack
'''

# 暴击can_critical要改, buff skill
class Index():
    def __init__(self):
        self.index = 0

    def addIndex(self):
        self.index += 1
        return self.index
cardNum = Index()

class CardSkill():
    def __init__(self):
        self.cardSkill = pd.read_csv('./csv/cardSkill.csv', index_col='index')

cardSkill = CardSkill()

class Card():
    def __init__(self, idx, pos):
        curCard = cardSkill.cardSkill.loc[idx]
        self.cardName = curCard.card
        self.partName = curCard.part
        self.cProp = curCard.prop
        self.bodyPart = curCard.body
        self.cost = curCard.cost
        self.attack = curCard.attack
        self.defend = curCard.defend
        self.attackType = curCard.attackType
        self.effectDiscription = curCard.effect
        self.idx = idx
        self.pos = pos #before/after attack/defend, final
        self.encode = None

    def in_chain(self, axie, thisRound, chainedCard, is_card=True):
        for team in thisRound.axieAlive:
            if axie in team:
                t = copy.copy(team)
                idx = t.index(axie)
                t.pop(idx)
                for a in t:
                    for card in a.cardChain:
                        if is_card: # same card
                            if card.cardName == chainedCard:
                                return True
                        else: # same cProp
                            if card.cProp == chainedCard:
                                return True
        return False

    def combo(self, axie, chainedCard, is_card=True, comboNum=1):
        cardChain = copy.copy(axie.cardChain)
        idx = cardChain.index(self)
        cardChain.pop(idx)
        if comboNum == 1:
            for card in cardChain:
                if is_card: # same card
                    if card.cardName == chainedCard:
                        return True
                else: # same cProp
                    if card.cProp == chainedCard:
                        return True
            return False
        else:
            boolList = []
            for _ in range(comboNum):
                for card in cardChain:
                    if is_card: # same card
                        if card.cardName == chainedCard:
                            boolList.append(True)
                    else: # same cProp
                        if card.cProp == chainedCard:
                            boolList.append(True)
            if len(boolList) == comboNum:
                return True
            return False

class TargetCard():
    def minusDis(self, axie, thisRound, lineIdx, must=False):
        minDis, idx = 1000, None
        for i in range(len(thisRound.roundPosInfo)):
            line = thisRound.roundPosInfo[i]
            if axie in line:
                if minDis>line[2]:
                    minDis, idx = line[2], i
        pos, roundPos = thisRound.posInfo, thisRound.roundPosInfo
        targetIdx = 1 if roundPos[lineIdx].index(axie)==0 else 0
        target = roundPos[lineIdx][targetIdx]
        if pos[idx][2] == roundPos[idx][2] or must:
            target.posInfo.append([roundPos[lineIdx][0], roundPos[lineIdx][1], minDis-1])
        else :
            if pos[idx][2]>pos[lineIdx][2]:
                target.posInfo.append([roundPos[lineIdx][0], roundPos[lineIdx][1], minDis-1])
            elif pos[idx][2]==pos[lineIdx][2]:
                target.posInfo.append([roundPos[lineIdx][0], roundPos[lineIdx][1], minDis])

    def plusDis(self, axie, thisRound, lineIdx, must=False):
        maxDis, idx = -1000, None
        for i in range(len(thisRound.roundPosInfo)):
            line = thisRound.roundPosInfo[i]
            if axie in line:
                if maxDis<line[2]:
                    maxDis, idx = line[2], i
        pos, roundPos = thisRound.posInfo, thisRound.roundPosInfo
        targetIdx = 1 if roundPos[lineIdx].index(axie)==0 else 0
        target = roundPos[lineIdx][targetIdx]
        if pos[idx][2] == roundPos[idx][2] or must:
            target.posInfo.append([roundPos[lineIdx][0], roundPos[lineIdx][1], maxDis+1])
        else :
            if pos[idx][2]<pos[lineIdx][2]:
                target.posInfo.append([roundPos[lineIdx][0], roundPos[lineIdx][1], maxDis+1])
            elif pos[idx][2]==pos[lineIdx][2]:
                target.posInfo.append([roundPos[lineIdx][0], roundPos[lineIdx][1], maxDis])

'''
能量获取
'''

class VegetalBite(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                if target.team.energy>0 and axie.team.energy<10:
                    target.team.energy = target.team.energy-1
                    axie.team.energy = axie.team.energy+1


class CarrotHammer(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target_card_isSheildBreak[2]:
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class AquaStock(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, targetAndCard, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            target = targetAndCard[0]
            targetCard = targetAndCard[1]
            if targetCard.cProp=='aquatic':
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class IvoryStab(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAnyAttack')

    def skill(self, axie, is_cridical, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if is_cridical:
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class PiercingSound(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
                target.team.energy = target.team.energy-1 if target.team.energy>0 else 0

class LunaAbsorb(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class NightSteal(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                if target.team.energy>0 and axie.team.energy<10:
                    target.team.energy = target.team.energy-1
                    axie.team.energy = axie.team.energy+1

class TailSlap(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class KotaroBite(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.roundSpeed<target.roundSpeed:
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class Disguise(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            flag = 0
            for card in axie.cardChain:
                if card.cProp == 'plant':
                    flag = 1
                    break
            if flag:
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

class BugSignal(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            for team in thisRound.axieAlive:
                if axie in team:
                    t, axieIdx = copy.copy(team), team.index(axie)
                    t.pop(axieIdx)
                    for otherAxie in t:
                        for card in otherAxie.cardChain:
                            if card.cardName == 'bugSignal' and target.team.energy>0 and axie.team.energy<10:
                                target.team.energy = target.team.energy-1
                                axie.team.energy = axie.team.energy+1

class ScaleDart1(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target.buff!={}:
                axie.team.energy = axie.team.energy+1 if axie.team.energy<10 else 10

'''
治疗
'''

class HealingAroma(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            if axie.canHeal:
                axie.hp += 120
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class DrainBite(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.canHeal:
                axie.hp += thisRound.ATT.attack
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class VeganDiet(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            if target.aProp == 'plant' and axie.canHeal:
                axie.hp += thisRound.ATT.attack
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class ShroomsGrace(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            if axie.canHeal:
                axie.hp += 120
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class ForestSpirit(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def is_front_axie(self, axie, testAxie):
        if axie.pos == [1, 2] and testAxie.pos == [1, 4]:
            return True
        elif axie.pos == [0, 1] and testAxie.pos == [0, 3]:
            return True
        elif axie.pos == [2, 1] and testAxie.pos == [2, 3]:
            return True
        elif axie.pos == [1, 0] and testAxie.pos == [1, 2]:
            return True
        else:
            return False

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            if thisRound.ATT.miss==0:
                flag = 1
                for team in thisRound.axieAlive:
                    if axie in team:
                        t, axieIdx = copy.copy(team), team.index(axie)
                        t.pop(axieIdx)
                        for targetAxie in t:
                            if self.is_front_axie(axie, targetAxie) and targetAxie.canHeal:
                                targetAxie.hp += 120
                                targetAxie.hp = targetAxie.hp if targetAxie.hp<targetAxie.maxHp else targetAxie.maxHp
                                flag = 0
                if flag and axie.canHeal:
                    axie.hp += 120
                    axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class SweetParty(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def is_front_axie(self, axie, testAxie):
        if axie.pos == [1, 2] and testAxie.pos == [1, 4]:
            return True
        elif axie.pos == [0, 1] and testAxie.pos == [0, 3]:
            return True
        elif axie.pos == [2, 1] and testAxie.pos == [2, 3]:
            return True
        elif axie.pos == [1, 0] and testAxie.pos == [1, 2]:
            return True
        else:
            return False

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            if thisRound.ATT.miss==0:
                flag = 1
                for team in thisRound.axieAlive:
                    if axie in team:
                        t, axieIdx = copy.copy(team), team.index(axie)
                        t.pop(axieIdx)
                        for targetAxie in t:
                            if self.is_front_axie(axie, targetAxie) and targetAxie.canHeal:
                                targetAxie.hp += 270
                                targetAxie.hp = targetAxie.hp if targetAxie.hp<targetAxie.maxHp else targetAxie.maxHp
                                flag = 0
                if flag and axie.canHeal:
                    axie.hp += 270
                    axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class Aquaponics(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.canHeal:
                cnt = 0
                for part in axie.bodyParts:
                    if part == 'anemone' or part == 'aquaVitality' or part == 'aquaponics':
                        cnt += 1
                axie.hp += 50*cnt
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class AquaVitality(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.canHeal:
                cnt = 0
                for part in axie.bodyParts:
                    if part == 'anemone' or part == 'aquaVitality' or part == 'aquaponics':
                        cnt += 1
                axie.hp += 50*cnt
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class Swallow(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.canHeal:
                axie.hp += thisRound.ATT.attack
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class WhySoSerious(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if thisRound.ATT.miss==0 and target.aProp == 'aquatic' and axie.canHeal:
                axie.hp += thisRound.ATT.attack
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp

class BloodTaste(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.canHeal:
                axie.hp += thisRound.ATT.attack
                axie.hp = axie.hp if axie.hp<axie.maxHp else axie.maxHp


'''
抽取、摧毁、禁用卡
'''

class ScaleDart(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.lastStand:
                thisRound.send_card(axie.team, 1)

class OctoberTreat(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'final')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            if axie.roundDefend>0:
                thisRound.send_card(axie.team, 1)

class CattailSlap(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, targetAndCard, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            target = targetAndCard[0]
            card = targetAndCard[1]
            if card.cProp in ['beast', 'bug', 'mech']:
                thisRound.send_card(axie.team, 1)

class SpicySurprise(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            for i in range(4):
                if target.cards[i].bodyPart == 'mouth':
                    target.cards_disable(target.cards[i])

class LeekLeak(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, targetAndCard, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            target = targetAndCard[0]
            card = targetAndCard[1]
            for i in range(4):
                if target.cards[i].attackType == 'ranged':
                    target.cards_disable(target.cards[i])

class HareDagger(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if thisRound.firstAttack:
                thisRound.send_card(axie.team, 1)

class HeroicReward(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target.aProp in ['aquatic', 'bird', 'dawn']:
                thisRound.send_card(axie.team, 1)

class Headshot(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            for i in range(4):
                if target.cards[i].bodyPart == 'horn':
                    target.cards_disable(target.cards[i])

class IvoryChop(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'final')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss == 0:
            if axie.roundDefend == 0:
                if axie.addCardInfo[self.cardName] == 1:
                    thisRound.send_card(axie.team, 1)
                    axie.addCardInfo[self.cardName] = 0
                elif axie.addCardInfo[self.cardName] == 0:
                    del axie.addCardInfo[self.cardName]

class ThirdGlance(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                thisRound.discard_card(target.team, 1)

class NumbingLecretion(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                for i in range(4):
                    if target.cards[i].attackType == 'melee':
                        target.cards_disable(target.cards[i])

class SunderClaw(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                thisRound.discard_card(target.team, 1)

'''
毒药
'''
class GasUnleash(Card):
    def __init__(self):
        super().__init__(cardNum.index, ['afterAttack', 'beingAttacked'])

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos[0] and thisRound.ATT.miss==0:
            poison.add_axie(target)
        elif pos==self.pos[1] and thisRound.ATT.miss==0:
            poison.add_axie(target[0])

class VenomSpray(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            poison.add_axie(target)

class BarbStrike(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if self.in_chain(axie, thisRound, self.cardName):
                poison.add_axie(target)
                poison.add_axie(target)

'''
暴击增减、特效
'''

class SingleCombat(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if len(axie.cardChain)>=3:
                attack.is_cridical=1

class BranchCharge(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.combo(axie, 'plant', False, comboNum=2):
                attack.increaseCritiChance=0.2

class SinisterStrike(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            attack = thisRoundAndAttack[1]
            attack.critiDamage = 1

class RampantHowl(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.lastStand == 1:
                for team in thisRound.axieAlive:
                    if axie in team:
                        for a in team:
                            moralUp.add_axie(a, 2)
                            morale = attDef.Morale()
                            morale.morale(a)

class DeathMark(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if axie.hp<0.3*axie.maxHp:
                lethal.add_axie(target, 0)

class SelfRally(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            moralUp.add_axie(axie, 2)
            moralUp.add_axie(axie, 2)
            morale = attDef.Morale()
            morale.morale(axie)

class HeartBreak(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            moralDown.add_axie(target, 2)
            morale = attDef.Morale()
            morale.morale(target)

'''
加、减攻击
'''
class RiskyFeather(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            attackDown.add_axie(axie, 0)
            attackDown.add_axie(axie, 0)

class PeaceTreaty(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            attackDown.add_axie(target, 0)

class Cockadoodledoo(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            attackUp.add_axie(axie, 0)

class FishHook(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target.aProp in ['plant', 'reptile', 'dusk']:
                attackUp.add_axie(axie, 0)

class ClamSlash(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target.aProp in ['beast', 'bug', 'mech']:
                attackUp.add_axie(axie, 0)

class Shipwreck(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            isSheildBreak = target_card_isSheildBreak[2]
            if isSheildBreak:
                attackUp.add_axie(axie, 0)

class NeuroToxin(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if 'poison' in target.debuff.keys():
                attackDown.add_axie(target, 0)

class BugNoise(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            attackDown.add_axie(target, 0)

class Acrobatic(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 2:
                speedUp.add_axie(axie, 2)
                speed = attDef.Speed()
                speed.speed(axie)

class SwiftEscape(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            speedUp.add_axie(axie, 2)
            speed = attDef.Speed()
            speed.speed(axie)

class UpstreamSwim(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if self.combo(axie, 'aquatic', False):
                speedUp.add_axie(axie, 2)
                speed = attDef.Speed()
                speed.speed(axie)

class Disarm(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            speedDown.add_axie(target, 2)
            speed = attDef.Speed()
            speed.speed(target)

class NileStrike(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            speedDown.add_axie(target, 2)
            speed = attDef.Speed()
            speed.speed(target)

class MysticRush(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            speedDown.add_axie(target, 2)
            speed = attDef.Speed()
            speed.speed(target)

'''
攻击位置、特定生物特效
'''

class TurnipRocket(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            if len(axie.cardChain)>=3:
                for i in range(len(thisRound.roundPosInfo)):
                    line = thisRound.roundPosInfo[i]
                    if axie in line:
                        idx = line.index(axie)
                        if idx == 0 and line[1].aProp=='bird':
                            self.minusdis(axie, thisround, i)
                        if idx == 1 and line[0].aProp=='bird':
                            self.minusDis(axie, thisRound, i)

class SeedBullet(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idx = 0 if axie in thisRound.axieAlive[1] else 1
            roundSpeed = [(axie, axie.roundSpeed) for axie in thisRound.axieAlive[idx]]
            roundSpeed = sorted(roundSpeed, key=lambda x:(-x[1]))
            idxAxie = 0 if idx else 1
            for i in range(len(thisRound.roundPosInfo)):
                line = thisRound.roundPosInfo[i]
                if line[idxAxie] == axie and line[idx] == roundSpeed[0][0]:
                    self.minusDis(axie, thisRound, i)

class GerbilJump(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
            idxAxie = 0 if idxTarget else 1
            if len(thisRound.axieAlive[idxTarget])>=2:
                minDist = 100
                minLine, minLine1 = None, None
                for i in range(len(thisRound.roundPosInfo)):
                    line = thisRound.roundPosInfo[i]
                    if line[idxAxie] == axie:
                        if line[2]<minDist:
                            minLine = i
                            minDist = line[2]
                            if minLine1 is not None:
                                minLine1 = None
                        elif line[2]==minDist:
                            minLine1 = i
                if minLine1 is None:
                    self.plusDis(axie, thisRound, minLine)
                else:
                    self.plusDis(axie, thisRound, minLine)
                    self.plusDis(axie, thisRound, minLine1)

class DarkSwoop(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idx = 0 if axie in thisRound.axieAlive[1] else 1
            roundSpeed = [(axie, axie.roundSpeed) for axie in thisRound.axieAlive[idx]]
            roundSpeed = sorted(roundSpeed, key=lambda x:(-x[1]))
            idxAxie = 0 if idx else 1
            for i in range(len(thisRound.roundPosInfo)):
                line = thisRound.roundPosInfo[i]
                if line[idxAxie] == axie and line[idx] == roundSpeed[0][0]:
                    self.minusDis(axie, thisRound, i)

class PuffySmack(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idx = 0 if axie in thisRound.axieAlive[1] else 1
            idxAxie = 0 if idx else 1
            for i in range(len(thisRound.roundPosInfo)):
                line = thisRound.roundPosInfo[i]
                if line[idx].lastStand==1:
                    self.plusDis(axie, thisRound, i)

class SmartShot(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
            idxAxie = 0 if idxTarget else 1
            if len(thisRound.axieAlive[idxTarget])>=2:
                minDist = 100
                minLine, minLine1 = None, None
                for i in range(len(thisRound.roundPosInfo)):
                    line = thisRound.roundPosInfo[i]
                    if line[idxAxie] == axie:
                        if line[2]<minDist:
                            minLine = i
                            minDist = line[2]
                            if minLine1 is not None:
                                minLine1 = None
                        elif line[2]==minDist:
                            minLine1 = i
                if minLine1 is None:
                    self.plusDis(axie, thisRound, minLine)
                else:
                    self.plusDis(axie, thisRound, minLine)
                    self.plusDis(axie, thisRound, minLine1)

class Insectivore(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            if axie.hp<0.5*axie.maxHp:
                for i in range(len(thisRound.roundPosInfo)):
                    line = thisRound.roundPosInfo[i]
                    if axie in line:
                        idx = line.index(axie)
                        if idx == 0 and line[1].aProp=='bug':
                            self.minusDis(axie, thisRound, i)
                        if idx == 1 and line[0].aProp=='bug':
                            self.minusDis(axie, thisRound, i)

class PatientHunter(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            if axie.hp<0.5*axie.maxHp:
                for i in range(len(thisRound.roundPosInfo)):
                    line = thisRound.roundPosInfo[i]
                    if axie in line:
                        idx = line.index(axie)
                        if idx == 0 and line[1].aProp=='aquatic':
                            self.minusDis(axie, thisRound, i)
                        if idx == 1 and line[0].aProp=='aquatic':
                            self.minusDis(axie, thisRound, i)

class ChitinJump(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
            idxAxie = 0 if idxTarget else 1
            maxDist = 0
            maxLine, maxLine1 = None, None
            for i in range(len(thisRound.roundPosInfo)):
                line = thisRound.roundPosInfo[i]
                if line[idxAxie] == axie:
                    if line[2]>maxDist:
                        maxLine = i
                        maxDist = line[2]
                        if maxLine1 is not None:
                            maxLine1 = None
                    elif line[2]==maxDist:
                        maxLine1 = i
            if maxLine1 is None:
                self.minusDis(axie, thisRound, maxLine)
            else:
                self.minusDis(axie, thisRound, maxLine)
                self.minusDis(axie, thisRound, maxLine1)

class CrimsonWater(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            if axie.hp<0.5*axie.maxHp:
                idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
                idxAxie = 0 if idxTarget else 1
                idxLine, minDis = None, 100
                idxLine1 = None
                for target in thisRound.axieAlive[idxTarget]:
                    is_injured = target.hp<target.maxHp
                    for i in range(len(thisRound.roundPosInfo)):
                        line = thisRound.roundPosInfo[i]
                        if line[idxAxie] == axie and line[idxTarget] == target and is_injured:
                            if line[2] <= minDis:
                                minDis = line[2]
                                idxLine = i
                                idxLine1 = None
                            elif line[2]==minDis:
                                idxLine1 = i
                if idxLine is not None:
                    if idxLine1 is None:
                        self.minusDis(axie, thisRound, idxLine)
                    else:
                        self.minusDis(axie, thisRound, idxLine)
                        self.minusDis(axie, thisRound, idxLine1)

class SpinalTap(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            if len(axie.cardChain)>=3:
                idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
                idxAxie = 0 if idxTarget else 1
                idxLine, minDis = None, 100
                idxLine1 = None
                for target in thisRound.axieAlive[idxTarget]:
                    idle = 0 if len(target.cardChain)>0 else 1
                    for i in range(len(thisRound.roundPosInfo)):
                        line = thisRound.roundPosInfo[i]
                        if line[idxAxie] == axie and line[idxTarget] == target and idle:
                            if line[2] <= minDis:
                                minDis = line[2]
                                idxLine = i
                                idxLine1 = None
                            elif line[2]==minDis:
                                idxLine1 = i
                if idxLine is not None:
                    if idxLine1 is None:
                        self.minusDis(axie, thisRound, idxLine)
                    else:
                        self.minusDis(axie, thisRound, idxLine)
                        self.minusDis(axie, thisRound, idxLine1)

class SneakyRaid(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
            idxAxie = 0 if idxTarget else 1
            maxDist = 0
            maxLine, maxLine1 = None, None
            for i in range(len(thisRound.roundPosInfo)):
                line = thisRound.roundPosInfo[i]
                if line[idxAxie] == axie:
                    if line[2]>maxDist:
                        maxLine = i
                        maxDist = line[2]
                        if maxLine1 is not None:
                            maxLine1 = None
                    elif line[2]==maxDist:
                        maxLine1 = i
            if maxLine1 is None:
                self.minusDis(axie, thisRound, maxLine)
            else:
                self.minusDis(axie, thisRound, maxLine)
                self.minusDis(axie, thisRound, maxLine1)

class SpikeThrow(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'target')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and 'fear' not in axie.debuff.keys() and \
                'stun' not in axie.debuff.keys():
            if len(axie.cardChain)>=3:
                idxTarget = 0 if axie in thisRound.axieAlive[1] else 1
                idxAxie = 0 if idxTarget else 1
                minDefend = 1000
                for target in thisRound.axieAlive[idxTarget]:
                    defend = target.roundDefend
                    for i in range(len(thisRound.roundPosInfo)):
                        line = thisRound.roundPosInfo[i]
                        if line[idxAxie] == axie and line[idxTarget] == target:
                            if defend<minDefend:
                                minDefend = defend
                                self.minusDis(axie, thisRound, i, True)

'''
特效增伤
'''
class PricklyTrap(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            flag = 0
            isLast = 1
            for i in range(len(thisRound.attOrder)):
                line = thisRound.attOrder[i]
                if axie in line:
                    flag = 1
                if flag and axie not in line and len(line[0].cardChain) != 0:
                    isLast = 0
            if isLast:
                attack.cardSkillCoeff = 0.2

class WoodenStab(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target_card_isSheildBreak[2]:
                attackUp.add_axie(axie, 0)

class BambooClan(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.in_chain(axie, thisRound, 'plant', is_card=False):
                attack.cardSkillCoeff = 0.2

class NutCrack(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.combo(axie, 'nutCrack') or\
                    self.combo(axie, 'nutThrow'):
                attack.cardSkillCoeff = 0.2

class NutThrow(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.combo(axie, 'nutCrack') or\
                    self.combo(axie, 'nutThrow'):
                attack.cardSkillCoeff = 0.2

class SugarRush(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beforeEveryAttack')

    def skill(self, axies, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            axie1, axie2 = axies[0], axies[1]
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if axie2.aProp == 'bug':
                attack.cardSkillCoeff = 0.1

class AirForceOne(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.in_chain(axie, thisRound, 'airForceOne'):
                attack.cardSkillCoeff=0.2

class EarlyBird(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            flag = 1
            for i in range(len(thisRound.attOrder)):
                line = copy.copy(thisRound.attOrder[i])
                if axie in line:
                    break
                else:
                    if len(line[0].cardChain) != 0:
                        flag = 0
                        break
            if flag:
                attack.cardSkillCoeff=0.2

class AlloutShot(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            damage = round(0.3*axie.maxHp)
            remain = axie.roundDefend - damage
            axie.roundDefend = remain if remain>=0 else 0
            if axie.roundDefend == 0 and axie.lastStand == 0:
                axieBeforeHp = axie.hp
                axie.hp = axie.hp+remain
                thisRound.add_last_stand(axie, axieBeforeHp)
                thisRound.axie_die()

class FeatherLunge(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.combo(axie, 'featherLunge') or\
                    self.combo(axie, 'scalyLunge'):
                attack.cardSkillCoeff = 0.2

class AngryLam(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if axie.hp<0.5*axie.maxHp:
                attack.cardSkillCoeff = 0.2

class FlankingSmack(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            flag = 1
            for i in range(len(thisRound.attOrder)):
                line = copy.copy(thisRound.attOrder[i])
                if axie in line:
                    break
                else:
                    if len(line[0].cardChain) != 0:
                        flag = 0
                        break
            if flag:
                attack.cardSkillCoeff=0.2

class ShellJab(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            idle = len(target.cardChain)==0
            if idle:
                attack.cardSkillCoeff = 0.3

class TinySwing(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if thisRound.roundNum>4:
                attack.cardSkillCoeff = 0.5

class SurpriseInvasion(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if target.roundSpeed>axie.roundSpeed:
                attack.cardSkillCoeff = 0.3

class ScalyLunge(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if self.combo(axie, 'featherLunge') or\
                    self.combo(axie, 'scalyLunge'):
                attack.cardSkillCoeff = 0.2

class AllergicReaction(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if target.debuff!={}:
                attack.cardSkillCoeff = 0.3

class DullGrip(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if target.roundDefend>0:
                attack.cardSkillCoeff = 0.3

class BugSplat(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if target.aProp=='bug':
                attack.cardSkillCoeff = 0.5

class MiteBite(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if len(axie.cardChain)>=2:
                attack.cardSkillCoeff = 1

'''
背水一战特效
'''

class RevengeArrow(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if axie.lastStand==1:
                attack.cardSkillCoeff = 0.5

class NitroLeap(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'speed')

    def skill(self, axie, targetAndSpeed, thisRound, pos):
        if pos==self.pos:
            speed = targetAndSpeed[1]
            if axie.lastStand==1:
                speed.cardSkillCoeff = 100

class StarShuriken(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'lastStandEnd')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            thisRound.canAddLastStand = 0

class HerosBane(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target.lastStand==1:
                target.lastStand = 0
                target.lastStandTicks = 0
                popAxie = []
                for i in range(len(thisRound.lastStand)):
                    if thisRound.lastStand[i] == target:
                        popAxie.append(target)
                for pAxie in popAxie:
                    thisRound.lastStand.remove(pAxie)
                thisRound.axie_die()

class GrubExplode(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'attack')

    def skill(self, axie, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if axie.lastStand==1:
                attack.cardSkillCoeff=1
                axie.lastStand = 0
                axie.lastStandTicks = 0
                popAxie = []
                for i in range(len(thisRound.lastStand)):
                    if thisRound.lastStand[i] == target:
                        popAxie.append(target)
                for pAxie in popAxie:
                    thisRound.lastStand.remove(pAxie)
                thisRound.axie_die()

'''
防御、盾牌特效
'''

class AquaDeflect(Card, TargetCard):
    def __init__(self):
        super().__init__(cardNum.index, 'defendTarget')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            idxTarget = 1 if axie in thisRound.axieAlive[0] else 0
            idxAxie = 0 if axie in thisRound.axieAlive[0] else 1
            for card in target.cardChain:
                if card.cProp == 'aquatic' and len(thisRound.axieAlive[idxTarget])>=2:
                    for i in range(len(thisRound.roundPosInfo)):
                        line = thisRound.roundPosInfo[i]
                        if axie in line and target in line:
                            self.plusDis(axie, thisRound, i)

class MerryLegion(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'defend')

    def skill(self, axie, defend, thisRound, pos):
        if pos==self.pos:
            if self.in_chain(axie, thisRound, 'merryLegion'):
                defend.cardSkillCoeff = 0.2

class SunderArmor(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'defend')

    def skill(self, axie, defend, thisRound, pos):
        if pos==self.pos:
            cnt = 0
            if axie.debuff != {}:
                for key in axie.debuff.keys():
                    if type(axie.debuff[key]) is list:
                        cnt += len(axie.debuff[key])
                    else:
                        if key == 'poison':
                            cnt += axie.debuff[key]
                        elif key == 'fear':
                            cnt += axie.debuff[key]+1
                        else:
                            cnt += 1
                defend.cardSkillCoeff = 0.2*cnt

class Shelter(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beforeEveryAttack')

    def skill(self, axies, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            axie1 = target
            axie, target = axies[0], axies[1]
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if axie1 == axie:
                attack.can_critical = 0

class DeepSeaGore(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            axie.roundDefend += round(0.3*axie.roundDefend)

class WoodmanPower(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target.aProp == 'plant':
                axie.roundDefend += thisRound.ATT.attack

class SlipperyShield(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterDefend')

    def skill(self, axie, target, thisRound, pos):
        if pos==self.pos:
            idx = 0 if axie in thisRound.axieAlive[0] else 1
            team = copy.copy(thisRound.axieAlive[idx])
            idx = team.index(axie)
            team.pop(idx)
            for teammate in team:
                teammate.roundDefend += round(0.15*teammate.roundDefend)

class CriticalEscape(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beforeEveryAttack')

    def skill(self, axies, target, thisRoundAndAttack, pos):
        if pos==self.pos:
            axie1, axie2 = axies[0], axies[1]
            thisRound = thisRoundAndAttack[0]
            attack = thisRoundAndAttack[1]
            if axie1 == target:
                attack.targetCardSkillCoeff = -0.15

class Bulkwark(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            target = target_card_isSheildBreak[0]
            card = target_card_isSheildBreak[1]
            isSheildBreak = target_card_isSheildBreak[2]
            if card.attackType == 'melee':
                attack = thisRound.ATT.attack
                damageBack = round(attack*0.4)
                targetBeforeHp = target.hp
                target.hp -= damageBack
                thisRound.add_last_stand(target, targetBeforeHp)

class VineDagger(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'defend')

    def skill(self, axie, defend, thisRound, pos):
        if pos==self.pos:
            for card in axie.cardChain:
                if card.cProp == 'plant':
                    defend.cardSkillCoeff = 1

class TinyCatapult(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            target = target_card_isSheildBreak[0]
            card = target_card_isSheildBreak[1]
            isSheildBreak = target_card_isSheildBreak[2]
            if card.attackType == 'ranged':
                attack = thisRound.ATT.attack
                damageBack = round(attack*0.5)
                targetBeforeHp = target.hp
                target.hp -= damageBack
                thisRound.add_last_stand(target, targetBeforeHp)

class OvergrowKeratin(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAnyAttackSearchAll')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos:
            axie.roundDefend += 20

class JarBarrage(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'noMoreDamage')

    def skill(self, axie, target, thisRound_isSheildBreak, pos):
        if pos == self.pos:
            thisRound = thisRound_isSheildBreak[0]
            isSheildBreak = thisRound_isSheildBreak[1]
            if isSheildBreak:
                thisRound.remain = 0

'''
去除减益效果
'''

class CleanseScent(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos:
            axie.debuff = {}

class Refresh(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def is_front_axie(self, axie, testAxie):
        if axie.pos == [1, 2] and testAxie.pos == [1, 4]:
            return True
        elif axie.pos == [0, 1] and testAxie.pos == [0, 3]:
            return True
        elif axie.pos == [2, 1] and testAxie.pos == [2, 3]:
            return True
        elif axie.pos == [1, 0] and testAxie.pos == [1, 2]:
            return True
        elif axie.pos == [1, 0] and testAxie.pos == [1, 4]:
            return True
        else:
            return False

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos:
            idx = 0 if axie in thisRound.axieAlive[0] else 1
            teammates = copy.copy(thisRound.axieAlive[idx])
            idxAxie = thisRound.axieAlive[idx].index(axie)
            teammates.pop(idxAxie)
            for teammate in teammates:
                if self.is_front_axie(axie, teammate):
                    teammate.debuff = {}

class Blackmail(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            for key in axie.debuff.keys():
                if key in target.debuff.keys():
                    if type(axie.debuff[key])==list:
                        target.debuff[key].extend(axie.debuff[key])
                    else:
                        if key=='poison':
                            target.debuff[key] += axie.debuff[key]
                        else:
                            target.debuff[key] = target.debuff[key]\
                                if target.debuff[key]>axie.debuff[key] else axie.debuff[key]
                else:
                    target.debuff[key] = axie.debuff[key]
            axie.debuff = {}

'''
控制效果晕眩、恐惧、睡眠
'''

class BalloonPop(Card):
    def __init__(self):
        super().__init__(cardNum.index, ['afterAttack', 'beingAttacked'])

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos[0] and thisRound.ATT.miss==0:
            fear.add_axie(target, 0)
        elif pos == self.pos[1] and thisRound.ATT.miss==0:
            fear.add_axie(axie, 0)

class SoothingSong(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'missDefend')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            sleep.add_axie(target, 0)
            thisRound.miss = 0

class Chomp(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            if len(axie.cardChain) >= 3:
                stun.add_axie(target, 0)

class StickyGoo(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            if target_card_isSheildBreak[2]:
                stun.add_axie(target_card_isSheildBreak[0], 0)

class AnestheticBait(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'beingAttacked')

    def skill(self, axie, target_card_isSheildBreak, thisRound, pos):
        if pos==self.pos and thisRound.ATT.miss==0:
            target = target_card_isSheildBreak[0]
            card = target_card_isSheildBreak[1]
            isSheildBreak = target_card_isSheildBreak[2]
            if target.aProp in ['bird', 'aquatic']:
                if axie.addCardInfo['anestheticBait'] == 1:
                    axie.addCardInfo['anestheticBait'] = 0
                    stun.add_axie(target, 0)

class TerrorChomp(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            if self.in_chain(axie, thisRound, 'terrorChomp'):
                fear.add_axie(target, 1)

class GrubSurprise(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            if target.roundDefend>0:
                fear.add_axie(target, 0)

'''
寒意、厄运、恶臭、脆弱状态
'''

class CoolBreeze(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'lastStandEnd')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            thisRound.canAddLastStand = 0
            chill.add_axie(target, 2)

class WaterSphere(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'lastStandEnd')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            thisRound.canAddLastStand = 0
            chill.add_axie(target, 2)

class Illomened(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            jinx.add_axie(target, 2)

class BlackBubble(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            jinx.add_axie(target, 2)

class PooFling(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            stench.add_axie(target, 0)
            stench.skill(target, thisRound)

class ChemicalWarfare(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            stench.add_axie(target, 0)
            stench.skill(target, thisRound)

class BuzzingWind(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            fragile.add_axie(target, 0)

class JugglingBalls(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'multiTimesAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos:
            if axie.addCardInfo[self.cardName] == 1:
                axie.addCardInfo[self.cardName] = 0
                idx = axie.cardChain.index(self)
                axie.cardChain.insert(idx+1, self)
                axie.cardChain.insert(idx+1, self)

class Eggbomb(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            aroma.add_axie(axie, 0)
            aroma.skill(axie, thisRound)

class TripleThreat(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'multiTimesAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos:
            if axie.addCardInfo[self.cardName] == 1 and axie.debuff != {}:
                axie.addCardInfo[self.cardName] = 0
                idx = axie.cardChain.index(self)
                axie.cardChain.insert(idx+1, self)

class ScarabCurse(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'afterAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos and thisRound.ATT.miss==0:
            target.canHeal = 0
            self.roundNum = thisRound.roundNum

class TwinNeedle(Card):
    def __init__(self):
        super().__init__(cardNum.index, 'multiTimesAttack')

    def skill(self, axie, target, thisRound, pos):
        if pos == self.pos:
            if axie.addCardInfo[self.cardName] == 1 and len(axie.cardChain) >=2:
                axie.addCardInfo[self.cardName] = 0
                idx = axie.cardChain.index(self)
                axie.cardChain.insert(idx+1, self)

#实例化
for i in range(totalCard):
    index = cardNum.addIndex()
    cardName = cardSkill.cardSkill.loc[cardNum.index].card
    locals()[cardName] = locals()[getClassName(cardName)]()
