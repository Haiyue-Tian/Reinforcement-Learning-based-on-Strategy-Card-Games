from rlcard.games.axie.printInfo import *
from rlcard.games.axie.battle import *


def getClassName(cardName):
    return ''.join(cardName[0].upper()+cardName[1:])


def inputHandInCards(pvp, team1=None, team2=None, isTestBattle=False, isRl=False, axieChain=None):
    def inputCard(pvp, team):
        if pvp.rnd.teamLeft == team:
            cardsList = handInCard[pvp.rnd.roundNum][0:3]
        elif pvp.rnd.teamRight == team:
            cardsList = handInCard[pvp.rnd.roundNum][3:]
        for i in range(len(cardsList)):
            axieCard = cardsList[i]
            for j in range(4):
                if axieCard[j] != 0:
                    cardIdx = axieCard[j]-1
                    team.hand_in_one_card(team.axies[i], team.axies[i].cards[cardIdx])
    if isTestBattle:
        inputCard(pvp, team1)
        inputCard(pvp, team2)
    else:
        if isRl:
            if axieChain[0][0] == 'l':
                axieTmp = pvp.rnd.teamLeft.axies[int(axieChain[0][-1])-1]
                for cardIdx in axieChain[1]:
                    try:
                        pvp.rnd.teamLeft.hand_in_one_card(axieTmp, axieTmp.cards[cardIdx])
                    except:
                        pdb.set_trace()
            else:
                axieTmp = pvp.rnd.teamRight.axies[int(axieChain[0][-1])-1]
                for cardIdx in axieChain[1]:
                    try:
                        pvp.rnd.teamRight.hand_in_one_card(axieTmp, axieTmp.cards[cardIdx])
                    except:
                        pdb.set_trace()
        else:
            ifAddCard = 'y'
            while ifAddCard=='y' or ifAddCard[0]=='l' or ifAddCard[0]=='r':
                axieChain = ()
                tmp = ''
                tmpList = ['l1', 'l2', 'l3', 'r1', 'r2', 'r3', 'q']
                while tmp not in tmpList:
                    tmp = input("出牌: 选择Axie (l1/l2/l3/r1/r2/r3, q退出): ")
                if tmp == 'q':
                    break
                axieChain += (tmp,)
                tmp = ''
                while tmp == '':
                    tmp = input("请输入需要出的牌 (1234): ")
                tmp = ''.join(ch for ch in tmp if tmp.isalnum())
                axieChain += ([int(i) for i in list(tmp)],)
                if axieChain[0][0] == 'l':
                    axieTmp = pvp.rnd.teamLeft.axies[int(axieChain[0][-1])-1]
                    for cardIdx in axieChain[1]:
                        team1.hand_in_one_card(axieTmp, axieTmp.cards[cardIdx-1])
                else:
                    axieTmp = pvp.rnd.teamRight.axies[int(axieChain[0][-1])-1]
                    for cardIdx in axieChain[1]:
                        team2.hand_in_one_card(axieTmp, axieTmp.cards[cardIdx-1])
                ifAddCard = ''
                ifAddCardFlag = ['y', 'n']
                while ifAddCard not in ifAddCardFlag:
                    ifAddCard = input('还有其他Axie出牌吗？(y/n): ')


def inputSendCards(rnd, team, num, card, sendCardNotSpecify, isTestBattle=False, numOri=None):
    if isTestBattle:
        if numOri>1 :
            if rnd.teamLeft == team:
                cardsList = sendCard[rnd.roundNum][0:3]
                for item in card:
                    axieIdx = rnd.teamLeft.axies.index(item[0])
                    cardsList[axieIdx][item[1]] -= item[2]
            elif rnd.teamRight == team:
                cardsList = sendCard[rnd.roundNum][3:]
                for item in card:
                    axieIdx = rnd.teamRight.axies.index(item[0])
                    cardsList[axieIdx][item[1]] -= item[2]
            for i in range(len(cardsList)):
                axieCard = cardsList[i]
                for j in range(4):
                    team.axies[i].cardsNow[j] += axieCard[j]
                    team.sendCardThisRound += axieCard[j]
                    team.axies[i].cardsNum[j] -= axieCard[j]
                    num -= axieCard[j]
            return num
        else:
            if rnd.teamLeft == team:
                cardsList = sendOneCard[rnd.roundNum][0:3]
                for item in card:
                    axieIdx = rnd.teamLeft.axies.index(item[0])
                    cardsList[axieIdx][item[1]] -= item[2]
            elif rnd.teamRight == team:
                cardsList = sendOneCard[rnd.roundNum][3:]
                for item in card:
                    axieIdx = rnd.teamRight.axies.index(item[0])
                    cardsList[axieIdx][item[1]] -= item[2]
            for i in range(len(cardsList)):
                axieCard = cardsList[i]
                for j in range(4):
                    team.axies[i].cardsNow[j] += axieCard[j]
                    team.sendCardThisRound += axieCard[j]
                    team.axies[i].cardsNum[j] -= axieCard[j]
                    num -= axieCard[j]
            return num
    else:
        direction = "左侧队伍的" if team.axies[0] in rnd.teamLeft.axies else "右侧队伍的"
        ifSendCard = 'y'
        if sendCardNotSpecify==False:
            while ifSendCard=='y':
                axieChain = ()
                tmp = ''
                tmpList = ['1', '2', '3', 'q']
                while tmp not in tmpList:
                    tmp = input("发牌: 选择"+direction+"Axie (1/2/3, q退出): ")
                if tmp == 'q':
                    break
                axieChain += (tmp,)
                tmp = ''
                flag = 1
                while flag:
                    while tmp == '':
                        tmp = input("请输入需要摸的牌 (1234): ")
                    tmp = ''.join(ch for ch in tmp if tmp.isalnum())
                    flag = 0
                    if num-len(tmp)>=0:
                        num = num-len(tmp)
                    else:
                        flag = 1
                        tmp=''
                axieChain += ([int(i) for i in list(tmp)],)
                for idx in axieChain[1]:
                    team.axies[int(axieChain[0][-1])-1].cardsNow[idx-1] += 1
                    team.axies[int(axieChain[0][-1])-1].team.sendCardThisRound += 1
                    team.axies[int(axieChain[0][-1])-1].cardsNum[idx-1] -= 1
                printInfo(rnd, False)
                sendCardFlag = ['y', 'n']
                ifSendCard = ''
                while ifSendCard not in sendCardFlag:
                    ifSendCard = input('还有其他Axie需要牌吗？(y/n): ')
        return num

def inputDiscardCards(rnd, team, num, sendCardNotSpecify):
    direction = "左侧队伍的" if team.axies[0] in rnd.teamLeft.axies else "右侧队伍的"
    ifSendCard = 'y'
    print('您需要抛弃'+str(num)+' 张牌')
    if sendCardNotSpecify==False:
        while ifSendCard=='y':
            axieChain = ()
            tmp = ''
            tmpList = ['1', '2', '3', 'q']
            while tmp not in tmpList:
                tmp = input("Discard card: 选择"+direction+"Axie (1/2/3, q退出): ")
            if tmp == 'q':
                break
            axieChain += (tmp,)
            tmp = ''
            flag = 1
            while flag:
                while tmp == '':
                    tmp = input("请输入需要discard的牌 (1234): ")
                tmp = ''.join(ch for ch in tmp if tmp.isalnum())
                flag = 0
                if num-len(tmp)>=0:
                    num = num-len(tmp)
                else:
                    flag = 1
                    tmp=''
            axieChain += ([int(i) for i in list(tmp)],)
            for idx in axieChain[1]:
                team.axies[int(axieChain[0][-1])-1].cardsNow[idx-1] -= 1
            printInfo(rnd, False)
            sendCardFlag = ['y', 'n']
            ifSendCard = ''
            while ifSendCard not in sendCardFlag:
                ifSendCard = input('还有其他Axie需要牌吗？(y/n): ')
    return num

def inputCard(test='card'):
    cards = []
    pos, posCandi = [], [str(i) for i in range(1,8)]
    tmp = ''
    ifAddAxie = 'y'
    flag = ['y', 'n']
    cnt = 0
    os.system('clear')
    while ifAddAxie == 'y' and cnt<3:
        card, cardCandi = [], [str(i) for i in range(1, 133)]
        ifAddCard = 'y'
        cnt += 1
        if test == 'card':
            while ifAddCard == 'y':
                while tmp == '':
                    tmp = input("+Card: 给第"+str(cnt)+"个Axie添加卡 (一张牌的index): ")
                tmp = ''.join(ch for ch in tmp if tmp.isalnum())
                card.append(int(tmp))
                tmp = ''
                ifAddCard = ''
                while ifAddCard not in flag:
                    ifAddCard = input('+Card: 需要继续添加卡吗？(y/n): ')
        elif test == 'battle':
            cardCnt = 0
            while cardCnt<4:
                cardCnt+=1
                while tmp not in cardCandi:
                    tmp = input("+Card: 给第"+str(cnt)+"个Axie添加第"+str(cardCnt)+"卡 (一张牌的index): ")
                tmp = ''.join(ch for ch in tmp if tmp.isalnum())
                card.append(int(tmp))
                tmp = ''
        cards.append(card)
        if test == 'battle':
            tmp = ''
            while tmp not in posCandi:
                tmp = input("+pos: 给第"+str(cnt)+"个Axie添加position: ")
            pos.append(int(tmp))
            tmp = ''
        if test == 'card':
            ifAddAxie = ''
            while ifAddAxie not in flag:
                ifAddAxie = input('+Axie: 需要继续添加Axie吗？(y/n): ')
    if test == 'card':
        return cards
    elif test == 'battle':
        return cards, pos
