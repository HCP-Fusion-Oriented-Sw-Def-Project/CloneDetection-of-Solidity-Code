import pandas as pd
import docker
import os
import re
import json
import threading
import time
import matplotlib.pyplot as plt

#获得所有完整合约名
def getContractName(match, code):
    return list(match['0'].apply(lambda x : code.loc[eval(x)[0]]['code_name'].split('.')[0]))
totalConName = list(set(getContractName(matchCon, codeCon) + getContractName(matchFun, codeFun)))

def getToolRes(toolName, resList, conName,resStoreList):
    appendRes = None
    if conName in resList:
        res = json.loads(open(os.path.join(rootAddr, toolName, conName, 'result.json')).read())
        if toolName is 'mythril' and res != None and res['analysis'] != None and res['analysis']['success'] == True:
                appendRes = json.dumps(res['analysis']['issues'])
        if toolName is 'osiris' and res != None and res['analysis'] != None:
            appendRes = json.dumps(res['analysis'])
        if toolName is 'slither' and res != None and res['analysis'] != None:
            appendRes = json.dumps(res['analysis'])
    else:
        print('{} {}'.format(conName, toolName))
    resStoreList.append(appendRes)

resStoreAddr = '/home/yfliu/paper_data/BugRes_bleu.csv'

sniPathCon = "/home/yfliu/paper_data/snippet_contract.csv"
codePathCon = "/home/yfliu/paper_data/code_contract.csv"
#matchPathCon = "/home/yfliu/paper_data/match_contract.csv"#ast方法下，修改match
matchPathCon = "/home/yfliu/paper_data/contract_bleu_ast_all.csv"#ast方法下，修改match

sniPathFun = "/home/yfliu/paper_data/snippet_function.csv"
codePathFun = "/home/yfliu/paper_data/code_function.csv"
matchPathFun = "/home/yfliu/paper_data/match_function.csv"
matchPathFun = "/home/yfliu/paper_data/function_bleu_ast_all.csv"

snippetCon = pd.read_csv(sniPathCon)
codeCon = pd.read_csv(codePathCon)
matchCon = pd.read_csv(matchPathCon)
matchCon = matchCon[matchCon['0'].apply(lambda x : len(eval(x)) > 0 )]
snippetFun = pd.read_csv(sniPathFun)
codeFun = pd.read_csv(codePathFun)
matchFun = pd.read_csv(matchPathFun)
matchFun = matchFun[matchFun['0'].apply(lambda x : len(eval(x)) > 0 )]

rootAddr = '/home/yfliu/paper_data/contractResult/'
toolNames = ['mythril','osiris','slither']
resStoreList = [[], [], []]

resList = []
for item in toolNames:
    resList.append(os.listdir(os.path.join(rootAddr, item)))

for i in range(len(totalConName)):    
    name = totalConName[i].split('.')[0]
    #对每一个name，如果有结果，那么取出来，没有给None
    for idx in range(len(toolNames)):
        getToolRes(toolNames[idx], resList[idx], name, resStoreList[idx])
    