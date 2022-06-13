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
    return list(match['0'].apply(lambda x : code.loc[x[0]]['code_name'].split('.')[0]))


#根据匹配结果，选择一部分漏洞信息存成json
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
    
rootAddr = '/home/yfliu/paper_data/bugResult/'
toolNames = ['mythril','osiris','slither']
resStoreList = [[], [], []]

resList = []
for item in toolNames:
    resList.append(os.listdir(os.path.join(rootAddr, item)))
    
sniPathCon = "/home/yfliu/paper_data/conFunFormat/snippet_contract.csv"
codePathCon = "/home/yfliu/paper_data/conFunFormat/code_contract.csv"
sniPathFun = "/home/yfliu/paper_data/conFunFormat/snippet_function.csv"
codePathFun = "/home/yfliu/paper_data/conFunFormat/code_function.csv"

#store
#resStoreAddr = '/home/yfliu/paper_data/completeRes/match_bug_res_v2.pic'
resStoreAddr = '/home/yfliu/paper_data/completeRes/nicadBugRes.pic'
#resStoreAddr = '/home/yfliu/paper_data/completeRes/nicad32CBugRes.pic'
#match
#nicad3-2c
#matchPathCon = '/home/yfliu/paper_data/matchRes/nicad32CConMatch.pic'
#matchPathFun = '/home/yfliu/paper_data/matchRes/nicad32CFunMatch.pic'
#nicad-2
matchPathCon = "/home/yfliu/paper_data/matchRes/nicadConMatch.pic"
matchPathFun = "/home/yfliu/paper_data/matchRes/nicadFunMatch.pic"
#ast-new
#matchPathCon = "/home/yfliu/paper_data/matchRes/match_contract_v2.pic"
#matchPathFun = "/home/yfliu/paper_data/matchRes/match_function_v2.pic"


snippetCon = pd.read_csv(sniPathCon)
codeCon = pd.read_csv(codePathCon)
matchCon = pd.read_pickle(matchPathCon)
matchCon = matchCon[matchCon['0'].apply(lambda x : len(x) > 0 )]
snippetFun = pd.read_csv(sniPathFun)
codeFun = pd.read_csv(codePathFun)
matchFun = pd.read_pickle(matchPathFun)
matchFun = matchFun[matchFun['0'].apply(lambda x : len(x) > 0 )]

totalConName = list(set(getContractName(matchCon, codeCon) + getContractName(matchFun, codeFun)))

for i in range(len(totalConName)):    
    name = totalConName[i].split('.')[0]
    #对每一个name，如果有结果，那么取出来，没有给None
    for idx in range(len(toolNames)):
        getToolRes(toolNames[idx], resList[idx], name, resStoreList[idx])

df = pd.DataFrame({
    'name':totalConName
})
for idx in range(len(toolNames)):
    df[toolNames[idx]] = resStoreList[idx]
    
df.to_pickle(resStoreAddr)