import sys
import pprint
import json
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
import pandas as pd
from nltk.translate.bleu_score import SmoothingFunction
import pandas as pd
import numpy as np
import docker
import os
import re
from matplotlib.font_manager import FontProperties
from string import punctuation
import matplotlib.pyplot as plt
from solidity_parser import parser
import huffman
from collections import Counter
punc = punctuation
smooth = SmoothingFunction()
import time
print(time.ctime())
def matchType(sni,codeList):
    print(sni['index'])
    sniType = sni['hashSeries']
    sniMod = sni['funcModifier']
    sniTypeName = sni['typeNameSeries']
    posList = codeList.apply(lambda codeItem, sniType = sniType, sniMod = sniMod, sniTypeName = sniTypeName
                             :codeItem['hashSeries'] == sniType and sniMod == codeItem['funcModifier'] and \
                             codeItem['typeNameSeries'] == sniTypeName,axis = 1)
    return json.dumps([idx for idx, item in enumerate(list(posList)) if item])


snippet_contract = pd.read_csv("../paper_data/snippet_contract.csv")
snippet_function = pd.read_csv("../paper_data/snippet_function.csv")
code_contract = pd.read_csv("../paper_data/code_contract.csv")
code_function = pd.read_csv("../paper_data/code_function.csv")
snippet_function['index'] = snippet_function.index
snippet_contract['index'] = snippet_contract.index
#print("contract")
matchRes = snippet_contract.apply(lambda item:matchType(sni = item, codeList=code_contract), axis = 1)
matchRes.to_csv("../paper_data/match_contract.csv",index = False)
#print("function")
matchRes = snippet_function.apply(lambda item:matchType(sni = item, codeList=code_function), axis = 1)
matchRes.to_csv("../paper_data/match_function.csv",index = False)

print(time.ctime())
