import pandas as pd
from .cards import *
import os

axieSkill = pd.read_csv('./axieSkill.csv')
allCards = AllCards()
for idx, item in enumerate(axieSkill.card):
    try:
        cardIdx = idx + 1
        os.rename('../card/'+item+'.png',
                '../card/'+str(cardIdx)+'-'+item+'.png')
    except:
        print(idx+1, item)

