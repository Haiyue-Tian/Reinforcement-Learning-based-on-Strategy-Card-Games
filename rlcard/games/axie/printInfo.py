import sys, os, pdb
import prettytable as pt


def printInfo(rnd, enter=True):
    def getCardInfo(rnd):
        if rnd.card is not None and rnd.attackAxie is not None \
                and rnd.defendAxie is not None:
            card = rnd.card
            axie, target = rnd.attackAxie, rnd.defendAxie
            aIdx = 1 if axie in rnd.axieAlive[1] else 0
            tIdx = 0 if axie in rnd.axieAlive[1] else 1
            try:
                if aIdx:
                    aIdx = rnd.teamRight.axies.index(axie)+1
                    tIdx = rnd.teamLeft.axies.index(target)+1
                    attacker = 'RightAxie'+str(aIdx)
                    defender = 'LeftAxie'+str(tIdx)
                else:
                    aIdx = rnd.teamLeft.axies.index(axie)+1
                    tIdx = rnd.teamRight.axies.index(target)+1
                    attacker = 'LeftAxie'+str(aIdx)
                    defender = 'RightAxie'+str(tIdx)
            except:
                pdb.set_trace()

            cardInfo = [card.idx, card.cardName, attacker, defender, str(rnd.ATT.attack)+'/'+str(int(card.attack)),
                        int(card.defend), int(card.cost), card.bodyPart, card.attackType, card.effectDiscription]
        else:
            cardInfo = ['']*10
        return cardInfo
    def attOrder(rnd):
        order = []
        if rnd.attOrder != None:
            for line in rnd.attOrder:
                if line[0] in rnd.teamLeft.axies:
                    tmp = 'Left'
                    idx = rnd.teamLeft.axies.index(line[0])
                    tmp+= 'Axie'+str(idx+1)
                elif line[0] in rnd.teamRight.axies:
                    tmp = 'Right'
                    idx = rnd.teamRight.axies.index(line[0])
                    tmp+= 'Axie'+str(idx+1)
                try:
                    order.append(tmp)
                except:
                    pdb.set_trace()
        return order

    def pos(rnd):
        posInfo = [['']*11, ['']*11, ['']*11]
        for i in range(len(rnd.teamLeft.axies)):
            axie = rnd.teamLeft.axies[i]
            if axie in rnd.axieAlive[0]:
                posInfo[axie.pos[0]][axie.pos[1]] = 'LeftAxie'+str(i+1)
        for i in range(len(rnd.teamRight.axies)):
            axie = rnd.teamRight.axies[i]
            if axie in rnd.axieAlive[1]:
                posInfo[axie.pos[0]][10-axie.pos[1]] = 'RightAxie'+str(i+1)
        return posInfo

    if rnd.isRl == 0:
        position = pos(rnd)
        p1=pt.PrettyTable()
        p1.add_row(position[0])
        p1.add_row(position[1])
        p1.add_row(position[2])

        p3=pt.PrettyTable()
        p3.add_column('Round '+str(rnd.roundNum), ['??????', '??????']) # ???
        p3.add_column('Team Left', [rnd.teamLeft.cardsNum, rnd.teamLeft.energy])
        p3.add_column('Team Right', [rnd.teamRight.cardsNum, rnd.teamRight.energy])
        p3.add_column('????????????', [attOrder(rnd), '']) # ???

        p2=pt.PrettyTable()
        p2.add_column('Axie', ['??????', '??????', '??????', '??????', '??????', '???1?????????', '???2?????????', '???3?????????', '???4?????????',
                            'Buff', 'Debuff', 'Health', 'Speed?????????/?????????',
                            'Skill', 'Morale?????????/?????????', 'ID', '?????????', 'cardsNow', 'cardsNum'])
        for i in range(3):
            try:
                axie = rnd.teamLeft.axies[i]
            except:
                pdb.set_trace()
            hp = str(axie.hp)+'/'+str(axie.maxHp)
            if axie.hp==0 and axie.lastStand:
                hp = 'Last Stand: '+ str(axie.lastStandTicks)
            cardChain = []
            for card in axie.cardChain:
                cardChain.append(axie.cards.index(card)+1)
            card1 = axie.cards[0].cardName + ' *'+str(axie.cardsNow[0]) if axie.cardsDisable[0] == 1 else \
                    axie.cards[0].cardName + ' *'+str(axie.cardsNow[0]) + ' ??????'
            card2 = axie.cards[1].cardName + ' *'+str(axie.cardsNow[1]) if axie.cardsDisable[1] == 1 else \
                    axie.cards[1].cardName + ' *'+str(axie.cardsNow[1]) + ' ??????'
            card3 = axie.cards[2].cardName + ' *'+str(axie.cardsNow[2]) if axie.cardsDisable[2] == 1 else \
                    axie.cards[2].cardName + ' *'+str(axie.cardsNow[2]) + ' ??????'
            card4 = axie.cards[3].cardName + ' *'+str(axie.cardsNow[3]) if axie.cardsDisable[3] == 1 else \
                    axie.cards[3].cardName + ' *'+str(axie.cardsNow[3]) + ' ??????'
            roundSpeed, roundMoral = str(axie.roundSpeed)+'/'+str(axie.speed), str(axie.roundMoral)+'/'+str(axie.moral)
            p2.add_column('LeftAxie'+str(i+1), [axie.posIdx, axie.aProp, axie.roundDefend, hp, cardChain, card1, card2, card3, card4,
                                            axie.buff, axie.debuff, axie.health, roundSpeed, axie.skill, roundMoral,
                                            axie.ID, axie in rnd.axieAlive[0], axie.cardsNow, axie.cardsNum])
        p2.add_column(' ', ['']*19)
        for i in range(3):
            axie = rnd.teamRight.axies[i]
            hp = str(axie.hp)+'/'+str(axie.maxHp)
            if axie.hp==0 and axie.lastStand:
                hp = 'Last Stand: '+ str(axie.lastStandTicks)
            cardChain = []
            for card in axie.cardChain:
                cardChain.append(axie.cards.index(card)+1)
            card1 = axie.cards[0].cardName + ' *'+str(axie.cardsNow[0]) if axie.cardsDisable[0] == 1 else \
                    axie.cards[0].cardName + ' *'+str(axie.cardsNow[0]) + ' ??????'
            card2 = axie.cards[1].cardName + ' *'+str(axie.cardsNow[1]) if axie.cardsDisable[1] == 1 else \
                    axie.cards[1].cardName + ' *'+str(axie.cardsNow[1]) + ' ??????'
            card3 = axie.cards[2].cardName + ' *'+str(axie.cardsNow[2]) if axie.cardsDisable[2] == 1 else \
                    axie.cards[2].cardName + ' *'+str(axie.cardsNow[2]) + ' ??????'
            card4 = axie.cards[3].cardName + ' *'+str(axie.cardsNow[3]) if axie.cardsDisable[3] == 1 else \
                    axie.cards[3].cardName + ' *'+str(axie.cardsNow[3]) + ' ??????'
            roundSpeed, roundMoral = str(axie.roundSpeed)+'/'+str(axie.speed), str(axie.roundMoral)+'/'+str(axie.moral)
            p2.add_column('RightAxie'+str(i+1), [axie.posIdx, axie.aProp, axie.roundDefend, hp, cardChain, card1, card2, card3, card4,
                                            axie.buff, axie.debuff, axie.health, roundSpeed, axie.skill, roundMoral,
                                            axie.ID, axie in rnd.axieAlive[1], axie.cardsNow, axie.cardsNum])
        p4=pt.PrettyTable(['Index', '???', '???', '???', 'Attack(??????/??????)', 'Sheild', 'Energy', '????????????', 'Attack Type', '??????'])
        p4.add_row(getCardInfo(rnd))
        #????????????
        os.system('clear')
        #??????
        sys.stdout.write("{} \n {} \n {} \n {}".format(p3, p1, p4, p2))
        sys.stdout.flush()
        sys.stdout.write("\n")
        if enter:
            input('press ENTER to continue')

def modules():
    for m in sys.modules:
        if str(sys.modules[m]).find(r'(built-in)')==-1:print('?????????: ', m, ', ????????????: ',
                                                             sys.modules[m])

def printResult(pvp):
    print('????????????: ')
    if len(pvp.rnd.axieAlive[0])==0 and len(pvp.rnd.axieAlive[1])!=0:
        print('Team Right Win')
    elif len(pvp.rnd.axieAlive[0])!=0 and len(pvp.rnd.axieAlive[1])==0:
        print('Team Left Win')
    elif len(pvp.rnd.axieAlive[0])==0 and len(pvp.rnd.axieAlive[1])==0:
        print('Draw')
