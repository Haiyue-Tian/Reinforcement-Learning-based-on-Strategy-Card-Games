import random, math, sys, copy, pdb
import pandas as pd
from .team import Team, Axie

'''
如果报IndexError: single positional indexer is out-of-bounds
是bodyParts里最起码有两个部位重复，比如[嘴，嘴]
'''
def generateAxie(aProp=None, bodyParts=None, pure=False):
    '''
    aProp is the property of axie
    bodyParts could be card names or body names, but they should represent different
    parts, like mouth, horn, back, and tail.
    make sure that the length of bodyParts should not longer than 4
    if pure is true, the axie is a pure axie
    if pure is false, the axie has 80% to be a not pure axie
    '''

    pureRandom = 0.9

    cardSkill = pd.read_csv('./csv/cardSkill.csv')

    prop = ['reptile', 'plant', 'dusk', 'aquatic', 'bird', 'dawn', 'beast', 'bug', 'mech']
    cProp = ['reptile', 'plant', 'aquatic', 'bird', 'beast', 'bug']
    NeverPureAxie = ['dusk', 'dawn', 'mech']

    if aProp is None and bodyParts is None:
        idx = math.floor(9*random.random())
        aProp = prop[idx]

    cnt = [0, 0, 0, 0]
    cards = [None, None, None, None]
    body = ['mouth', 'horn', 'back', 'tail']
    if bodyParts is not None:
        for part in bodyParts:
            try:
                p = cardSkill[cardSkill.part == part].iloc[0, 4]
                idx = body.index(p)
                cnt[idx] = cnt[idx]+1 if cnt[idx]<1 else sys.exit()
                cards[idx] = cardSkill[cardSkill.part == part].iloc[0, 1]
                pure = cardSkill[cardSkill.part == part].iloc[0, 3] == aProp
                if aProp is None:
                    aProp = cardSkill[cardSkill.part == part].iloc[0, 3]
            except:
                try:
                    p = cardSkill[cardSkill.card == part].iloc[0, 4]
                    idx = body.index(p)
                    cnt[idx] = cnt[idx]+1 if cnt[idx]<1 else sys.exit()
                    cards[idx] = cardSkill[cardSkill.card == part].iloc[0, 1]
                    pure = cardSkill[cardSkill.card == part].iloc[0, 3] == aProp
                    if aProp is None:
                        aProp = cardSkill[cardSkill.card == part].iloc[0, 3]
                except:
                    p = cardSkill[cardSkill.index == part-1].iloc[0, 4]
                    idx = body.index(p)
                    cnt[idx] = cnt[idx]+1 if cnt[idx]<1 else sys.exit()
                    cards[idx] = cardSkill[cardSkill.index == part-1].iloc[0, 1]
                    pure = cardSkill[cardSkill.index == part-1].iloc[0, 3] == aProp
                    if aProp is None:
                        aProp = cardSkill[cardSkill.index == part-1].iloc[0, 3]

    for i in range(4):
        if cnt[i] == 0:
            rand = 1 if random.random()<pureRandom else 0
            if (pure or rand) and aProp in cProp:
                p = cardSkill[(cardSkill.body==body[i])&(cardSkill.prop==aProp)]
            else:
                cPropTmp = copy.copy(cProp)
                if aProp in NeverPureAxie:
                    idx = math.floor(6*random.random())
                else:
                    idx = cProp.index(aProp)
                    cPropTmp.pop(idx)
                    idx = math.floor(5*random.random())
                p = cardSkill[(cardSkill.body==body[i])&(cardSkill.prop==cPropTmp[idx])]
            idx = math.floor(len(p)*random.random())
            cards[i] = p.iloc[idx, 1]
    for i in range(2):
        rand = 1 if random.random()<pureRandom else 0
        if (pure or rand) and aProp in cProp:
            cards.append(aProp)
        else:
            cPropTmp = copy.copy(cProp)
            if aProp in NeverPureAxie:
                idx = math.floor(6*random.random())
            else:
                idx = cProp.index(aProp)
                cPropTmp.pop(idx)
                idx = math.floor(5*random.random())
            cards.append(cPropTmp[idx])
    return (aProp, cards)


def generateTeam(axies=[None]*3, pos=[None]*3):
    '''
    axies:[(aProp1, cards1), (aProp2, cards2)] 可以写入零到三个axie
    pos  :[pos1=1          , pos2=None       ] 需要一一对应, 和写入的axie数相同
                                               可以是posIdx或None
    '''
    assert(len(axies)==len(pos))
    team = Team()

    if random.random() < 0.9:
        teamClass = [['aquatic', 'aquatic', 'plant'],
                     ['plant', 'bird', 'aquatic'],
                     ['plant', 'beast', 'aquatic'],
                     ['plant', 'plant', 'beast'],
                     ['plant', 'plant', 'bird'],
                     ['bug', 'bug', 'bug'],
                     ['reptile', 'reptile', 'reptile'],
                     ['aquatic', 'aquatic', 'aquatic'],
                     ['plant', 'beast', 'bird'],
                     ['plant', 'reptile', 'reptile'],
                     ['plant', 'beast', 'reptile'],
                     ['plant', 'reptile', 'bird']]
        pos = [[None, None, 1],
               [1, None, None],
               [1, None, None],
               [1, None, None],
               [1, None, None],
               [None, None, None],
               [None, None, None],
               [None, None, None],
               [1, 4, 7],
               [1, None, None],
               [1, None, None],
               [1, None, None]]
        idx = random.choice([i for i in range(len(teamClass))])
        axieClass = teamClass[idx]
        axies = [generateAxie(axieClass[i]) for i in range(3)]
        pos = pos[idx] if random.random() < 0.9 else [None, None, None]

    cnt = 0
    posCandi = [i+1 for i in range(7)]
    for i in range(len(axies)):
        if axies[i] is not None:
            cnt += 1
            if pos[i] == None:
                posIndex = random.choice(posCandi)
                while posIndex in pos:
                    posIndex = random.choice(posCandi)
            else:
                posIndex = pos[i]
            posCandi.remove(posIndex)
            axieInfo = axies[i]
            ID = round(random.random()*10**8)
            axie = Axie(axieInfo[0], axieInfo[1], ID)
            team.addAxie(axie, posIndex)
    while cnt<=3:
        ID = round(random.random()*10**8)
        cnt += 1
        pos = random.choice(posCandi)
        posCandi.remove(pos)
        axieInfo = generateAxie()
        axie = Axie(axieInfo[0], axieInfo[1], ID)
        team.addAxie(axie, pos)
    return team
