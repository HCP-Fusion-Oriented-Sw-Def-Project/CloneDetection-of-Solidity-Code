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
    return list(match['code'].apply(lambda x : code[code['code'] == x]['code_name'].iloc[0].split('.')[0]))


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
resStoreAddr = '/home/yfliu/paper_data/completeRes/manualBugRes.pic'
#match

matchPathCon = "/home/yfliu/paper_data/manualResultCsv/manualCon.csv"


matchPathFun = "/home/yfliu/paper_data/manualResultCsv/manualFun.csv"

snippetCon = pd.read_csv(sniPathCon)
codeCon = pd.read_csv(codePathCon)
matchCon = pd.read_csv(matchPathCon)

snippetFun = pd.read_csv(sniPathFun)
codeFun = pd.read_csv(codePathFun)
matchFun = pd.read_csv(matchPathFun)

a = getContractName(matchCon, codeCon)
b = getContractName(matchFun, codeFun)
totalConName = list(set(a + b))

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