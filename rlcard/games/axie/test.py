import copy
import pdb


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


# def combineActions(axieAct, energy):
#     axie1, axie2, axie3 = axieAct
#     actionsIdx = []
#     lenAxie1, lenAxie2 = len(axie1['actions']), len(axie2['actions'])
#     lenAxie3 = len(axie3['actions'])
#     cntList = [0]*10
#     for i in range(lenAxie1):
#         eng = energy
#         tmpActionsIdx = []
#         tmpActionsIdx.append(axie1['actionsIdx'][i])
#         eng -= len(axie1['actions'][i])
#         flag1 = 1
#         for j in range(lenAxie2):
#             eng1 = eng
#             tmpActionsIdx1 = copy.copy(tmpActionsIdx)
#             flag11 = 0
#             if len(axie2['actions'][j]) <= eng:
#                 tmpActionsIdx1.append(axie2['actionsIdx'][j])
#                 eng1 -= len(axie2['actions'][j])
#                 flag11 = 1
#             else:
#                 if flag1:
#                     tmpActionsIdx1.append([])
#                     flag1 = 0
#                     flag11 = 1
#             if flag11:
#                 flag2 = 1
#                 for k in range(lenAxie3):
#                     eng2 = eng1
#                     tmpActionsIdx2 = copy.copy(tmpActionsIdx1)
#                     flag22 = 0
#                     if len(axie3['actions'][k]) <= eng2:
#                         tmpActionsIdx2.append(axie3['actionsIdx'][k])
#                         eng2 -= len(axie3['actions'][j])
#                         flag22 = 1
#                     else:
#                         if flag2:
#                             tmpActionsIdx2.append([])
#                             flag2 = 0
#                             flag22 = 1
#                     if flag22:
#                         flag = 1
#                         if tmpActionsIdx2 in actionsIdx:
#                             flag = 0
#                         if flag:
#                             length = len(tmpActionsIdx2[0])+len(tmpActionsIdx2[1])+len(tmpActionsIdx2[2])
#                             cntList[length] += 1
#                             cntList[0] += 1
#                             print(cntList)
#                             actionsIdx.append(tmpActionsIdx2)
#     return actionsIdx

def combineActions(axieAct, energy):
    axie1, axie2, axie3 = axieAct
    actionsIdx = []
    lenAxie1, lenAxie2 = len(axie1['actions']), len(axie2['actions'])
    lenAxie3 = len(axie3['actions'])
    cntList = [0]*10
    for i in range(lenAxie1):
        eng = energy
        tmpActionsIdx = []
        tmpActionsIdx.append(axie1['actionsIdx'][i])
        eng -= len(axie1['actions'][i])
        flag1 = 1
        for j in range(lenAxie2):
            eng1 = eng
            tmpActionsIdx1 = copy.copy(tmpActionsIdx)
            flag11 = 0
            if len(axie2['actions'][j]) <= eng:
                tmpActionsIdx1.append(axie2['actionsIdx'][j])
                eng1 -= len(axie2['actions'][j])
                flag11 = 1
            else:
                if flag1:
                    tmpActionsIdx1.append([])
                    flag1 = 0
                    flag11 = 1
            if flag11:
                flag2 = 1
                for k in range(lenAxie3):
                    eng2 = eng1
                    tmpActionsIdx2 = copy.copy(tmpActionsIdx1)
                    flag22 = 0
                    if len(axie3['actions'][k]) <= eng2:
                        tmpActionsIdx2.append(axie3['actionsIdx'][k])
                        eng2 -= len(axie3['actions'][j])
                        flag22 = 1
                    else:
                        if flag2:
                            tmpActionsIdx2.append([])
                            flag2 = 0
                            flag22 = 1
                    if flag22:
                        length = len(tmpActionsIdx2[0])+len(tmpActionsIdx2[1])+len(tmpActionsIdx2[2])
                        cntList[length] += 1
                        cntList[0] += 1
                        print(cntList)
                        actionsIdx.append(tmpActionsIdx2)
    actionsIdx = set(tuple(tuple(item1) for item1 in item0) for item0 in actionsIdx)
    actionsIdx = list(list(list(item1) for item1 in item0) for item0 in actionsIdx)
    print(len(actionsIdx))
    return actionsIdx

def update_history(actions0, actions1):
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
    return act0, act1


maxCard = 4
cards = ([2, 2, 2, 2], ['a', 'b', 'c', 'd'])
a = axieProbAct(maxCard, cards)
b = axieProbAct(maxCard, cards)
c = axieProbAct(maxCard, cards)
pdb.set_trace()
d = combineActions([a, b, c], 9)
# actions0 = [[0, 1, 3], [], [0]]
# actions1 = [[0, 1, 3], [], [0]]
# act0, act1 = update_history(actions0, actions1)
pdb.set_trace()
