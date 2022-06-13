from nltk.translate.bleu_score import sentence_bleu, corpus_bleu,SmoothingFunction
import pandas as pd
import numpy as np
import docker
import os
import re
import random
from string import punctuation
import json
import matplotlib.pyplot as plt
punc = punctuation
smooth = SmoothingFunction()

def mythril_get(bb):
    mythril_result = []
    myt = bb['mythril']
    line = bb['contract_line']
    for index,j in enumerate(myt):
        if j != None and type(j) != float and len(j) > 0:
            total = []
            for i in j:
                #print(i)
                ccode = i.get('code')
                formatted = {
                    #'address':i['address'],
                    #'code':ccode,
                    'function':i['function'],
                    'lineno':i['lineno'],
                    'title':i['title'],
                    'type':i['type']
                }
                
                if(line[index][0] <= formatted['lineno'] and line[index][1] >= formatted['lineno']):
                    total.append(formatted)
            mythril_result.append(total)
        else:
            mythril_result.append([])
    return mythril_result
def slither_get(bb):
    slither_result = []
    sli = bb['slither']
    line = bb['contract_line']
    for index,j in enumerate(sli):
        if j != None and type(j) != float and len(j) > 0:
            temp=[]
            for i in j:
                if len(i['elements']) > 0 and i['elements'][0].get('source_mapping'):
                    func = i['elements'][0].get('name')
                    t = {
                        'title':i['check'],
                        'function':func,
                        #'contract':i['elements'][0].get('contract').get('name'),
                        'lineno':i['elements'][0]['source_mapping']['lines'],
                        'type':i['impact']
                    }
                    #print("t:"+str(t['lineno'][0]))
                    #print('line'+str(line[index][0])+str(line[index][1]))
                    if(len(t['lineno']) > 0 and line[index][0] <= t['lineno'][0] and line[index][1] >= t['lineno'][0]):
                        temp.append(t)
            slither_result.append(temp)
        else:
            slither_result.append([])
    return slither_result
def osiris_get(bb):
    result = []
    osi = bb['osiris']
    line = bb['contract_line']
    count = 0
    for  index,i in enumerate(osi):
        if i != None and type(i) != float and len(i) > 0:
            temp = []  
            for j in i:
                error = j['errors']
                name = j['name']
                if len(error) > 0:
                    for ttt in error:
                        t = {
                            'title':ttt['message'],
                            'lineno':ttt['line'],
                            'function':name
                        }
                        if(line[index][0] <= t['lineno'] and line[index][1] >= t['lineno']):
                            temp.append(t)
            result.append(temp)
        else:
            result.append([])
    return result
def find_range(code,f):
    head = code.splitlines()[0]
    hang = f.splitlines()
    for i in range(len(hang)):
        if head in hang[i]:
            a = i
            flag = 1
            j = i+1
            while flag != 0 and j < len(hang):
                if '{' in hang[j]:
                    flag += hang[j].count('{')
                if '}' in hang[j]:
                    flag -= hang[j].count('}')
                j += 1
            return [a,j-1]
    return [0,0]
def find_func_range(code,f):
    head = code.splitlines()[0]
    hang = f.splitlines()
    for i in range(len(hang)):
        if head in hang[i]:
            a = i
            flag = 1
            j = i+1
            while flag != 0 and j < len(hang):
                if '{' in hang[j]:
                    flag += hang[j].count('{')
                if '}' in hang[j]:
                    flag -= hang[j].count('}')
                j += 1
            return [a,j-1]
    print("find_func_range error")
    return [0,0]
def get_contract_line(bb):
    code_range = []
    name = list(bb['code_name'])
    for i in range(len(name)):
        try:
            f = open('/home/yfliu/data_sol/'+name[i],encoding = 'utf-8').read()
        except:
            f = open('/home/yfliu/data_sol/'+name[i],encoding = 'GBK').read()
        code = bb.loc[i,'contract_code']
        con_range = find_range(code,f)
        code_range.append(con_range)
    return code_range
def get_function_line(bb):
    code_range = []
    name = list(bb['code_name'])
    for i in range(len(name)):
        try:
            f = open('/home/yfliu/data_sol/'+name[i],encoding = 'utf-8').read()
        except:
            f = open('/home/yfliu/data_sol/'+name[i],encoding = 'GBK').read()
        code = bb.loc[i,'contract_code']
        con_range = find_func_range(code,f)
        code_range.append(con_range)
    return code_range
def add_sol(sol_name,target):
    temp = target[sol_name]
    #print(temp[0])
    for i in range(len(temp)):
        if '.sol' not in temp[i]:
            temp[i] += '.sol'
    target[sol_name] = temp
def check_len(x):
    return len(x)
def print_code(addr):
    ttt = open("/home/yfliu/data_sol/"+addr).read().splitlines()
    for index,i in enumerate(ttt):
        print(str(index)+i)
def func_code(coindex):
    ana = bb[bb['code_index'] == coindex].iloc[0]
    #print(ana['contract_code'])
    for j in ['osiris_analysis','mythril_analysis_not_info','slither_analysis_not_info']:
        print(j)
        for i in ana[j]:
            print(i)
        print()
    def spli(x):
        return x.split('-')[0]
    def include_f(x,y):
        return y in eval(x)['href']
    temp2 = bb[bb['code_index'] == coindex]['sni_name'].apply(spli)
    print(list(temp2))
    for i in temp2:
        temp = post[post['info'].apply(include_f,y = i)]
        print(eval(temp.iloc[0]['info'])['href'])
    print_code(ana['code_name'])
def smallerRange(oldNum, lineNum):
    if len(oldNum) < 1 or len(lineNum) < 1:
        print('great error')
        return False
    oldStart = oldNum[0]
    oldEnd = oldNum[-1]
    lineStart = lineNum[0]
    lineEnd = lineNum[-1]
    return lineStart >= oldStart and lineEnd <= oldEnd
def updateMap(res, title, lineNum):
    lineNum = [lineNum] if type(lineNum) == int else lineNum
    lineOldNum = res[title]
    for oldNum in lineOldNum:
        #print(oldNum)
        if smallerRange(oldNum, lineNum):
            return
    res[title].append(lineNum)
    
def subDict(dict1, dict2):
    res = {}
    for item in dict1.keys():
        if item not in dict2.keys():
            res[item] = dict1[item]
        elif dict1[item] - dict2[item] > 0:
            res[item] = dict1[item] - dict2[item]
    return res
    
def getCount(mapRes):
    resCount = {}
    for item in mapRes:
        if len(item) > 0:
            for bugName in item.keys():
                count = len(item[bugName])
                if bugName in resCount.keys():
                    resCount[bugName] += count
                else:
                    resCount[bugName] = count
    return resCount

def get(cc, toolNames):
    mapRes = []
    for index,row in cc.iterrows():
        #同行算消除
        res = {}
        for toolName in toolNames:
            #toolRes = row[toolName]
            toolRes =  eval(row[toolName]) if type(row[toolName]) == str else row[toolName]
            for tRes in toolRes:
                lineNum = tRes['lineno']
                title = mapp[toolName.split('_')[0]][tRes['title'].strip()]#已经转换过
                if title in res.keys():
                    updateMap(res, title, lineNum)
                else:
                    res[title] = [[lineNum] if type(lineNum) == int else lineNum]#使用lineNum--list的len计算数量 [[],[]]
            #temp = [res]
            #print(getCount(temp))
        mapRes.append(res)
    resCount =  getCount(mapRes)
    return resCount  
    
#gas function
#将结果分割，需要不同的split字符串
def getGasResList(address, num):
    pat = open(address,'r').read()
    patList = re.split('\n[0-9]+ : ', pat)#
    ans = {}
    for sol in patList:
        if 'success' not in sol:
            continue
        sol = sol.split('\n')
        sol = sol[:-1]
        if sol[0] in ans.keys():
            ans[sol[0]] += patternDeal(sol, num)
        else:
            ans[sol[0]] = patternDeal(sol, num)
    return ans

#匹配gasPattern与克隆对的范围
def matchRange(item, contract_line):
    return int(item['rows'][0].strip()) >= contract_line[0] and int(item['rows'][1].strip()) <= contract_line[1]

#当克隆对合约在patList内，并且范围正确，旧获得
def compareRange(pat, contract_line, name):

    return  [
        item['rows'] for item in pat[name] if matchRange(item, contract_line)
    ] if name in pat.keys() else None

#将gas结果加到bb内
def GasAppendByRange(bb,pat,num):
    bb['pattern{}'.format(num)] = [ compareRange(pat, item[1]['contract_line'], item[1]['code_name'].split('.')[0]) for item in bb.iterrows() ]

def runGasPattern(patNum, rootAddress, bb):
    for num in patNum:
    #切割
        pat = getGasResList(os.path.join(rootAddress,'gasDetectResult{}.txt').format(num), num)
        GasAppendByRange(bb, pat, num)

def patternDeal(sol, num):
    if num == 6:
        return [ 
                {
                    'itemName' : item.split(':')[0],
                    'rows' : [ i.strip() for i in item.split(':')[1].split(',') ]
                      }  for item in sol[1:] if ':' in item and 'uint' in item.split(':')[0] and 'uint256' not in item.split(':')[0]
                ]
    return [ 
                {
                    'itemName' : item.split(':')[0],
                    'rows' : [ i.strip() for i in item.split(':')[1].split(',') ]
                      }  for item in sol[1:] if ':' in item 
                ]
    
head = [' access_control ',
 ' arithmetic ',
 ' denial_service ',
 ' reentrancy ',
 ' unchecked_low_calls ',
 ' bad_randomness ',
 ' front_running ',
 ' time_manipulation ',
 ' short_addresses ',
 ' Other ',
 ' Ignore ']
dic = dict(zip(head,[0]*10))
mapping = open('/home/yfliu/mapping.json').read()
mapp = json.loads(mapping)

slither_map = mapp['slither']
slither_key = slither_map.keys()
slither_type_map = dict(zip(slither_key,[0]*len(slither_key)))
u = open('/home/yfliu/paper/trash/temp.txt').read()
for i in u.splitlines():
    sp = i.split()
    slither_type_map[sp[1]] = sp[-2]
slither_type_map
slither_type_map['constant-function'] = 'Medium'
slither_bug_patch = ['constable-states','erc20-indexed','erc20-interface','external-function','incorrect-equality','naming-convention','shadowing-local','shadowing-state','shadowing-builtin','shadowing-abstract']  

def run_sTs(sniPath, codePath, matchPath, storeAddr, bugResAddr): 

    bugRes = pd.read_pickle(bugResAddr)
    snippet = pd.read_csv(sniPath)
    code = pd.read_csv(codePath)
    match = pd.read_pickle(matchPath)
    match['snippet'] = match.index
    match['code'] = match['0']
    match = match[match['code'].apply(lambda x : len(x) > 0 )]

    sni_index = 'snippet'
    code_index = 'code'
    sni_index = ''
    snippet = snippet[['sol_name','code']]
    code_name = []
    contract_code = []
    sni_name = []
    sni_code = []
    dealed_code = []
    for index,i in match.iterrows():
        a = snippet.loc[int(i['snippet'])]
        b = code.loc[i['code'][0]]#AST
        code_name.append(b['code_name'])
        contract_code.append(b['code'])
        dealed_code.append(b['dealed_code'])
        sni_name.append(a['sol_name'])
        sni_code.append(a['code'])
    bb = pd.DataFrame({
        'sni_index':list(match['snippet']),
        'code_index':[int(item[0]) for item in list(match['code'])],#ast
        'code_name':code_name,
        'dealed_code':dealed_code,
        'sni_name':sni_name,
        'contract_code':contract_code,
        'sni_code':sni_code
    })
    #为结果添加.sol方便下一步处理 确定contract在完整合约的范围 把工具结果(未处理)贴上去
    bname = bb['code_name']
    bb['contract_line'] = get_contract_line(bb)
    bb['name'] = bb['code_name'].apply(lambda x : x.split('.')[0])
    bb = bb.merge(bugRes,on='name')
    bb['mythril'] = bb['mythril'].apply(lambda x : json.loads(x) if type(x) == str else None)
    bb['slither'] = bb['slither'].apply(lambda x : json.loads(x) if type(x) == str else None)
    bb['osiris'] = bb['osiris'].apply(lambda x : json.loads(x) if type(x) == str else None)
    bb['osiris_analysis'] = osiris_get(bb)
    bb['mythril_analysis'] = mythril_get(bb)
    bb['slither_analysis'] = slither_get(bb)

    #gas
    rootAddress = '/home/yfliu/paper_data/gasPattern/new'
    patNum = [1,6,2,3,4,7]
    runGasPattern(patNum, rootAddress, bb)
    count = 0
    for item in patNum:
        print(item,end=' ')
        num = len(bb[bb['pattern{}'.format(item)].apply(lambda x : x != None and len(x) > 0)])
        print(num)
        count += num
    print(count)
    
    slither_temp = list(bb['slither_analysis'])
    slither_info = []
    for item in slither_temp:
        del_list = []
        info_list = []
        for index,t_item in enumerate(item):
            title = t_item['title']
            level = slither_type_map[title]
            if level == 'Informational' or title in slither_bug_patch:
                del_list.append(index)
        del_list.reverse()
        for tempt in del_list:
            info_list.append(item[tempt])
            del item[tempt]
        slither_info.append(info_list)
    bb['slither_analysis_not_info'] = slither_temp
    #bb['slither_analysis_info'] = slither_info
    slither_temp = list(bb['mythril_analysis'])
    slither_info = []
    for item in slither_temp:
        del_list = []
        info_list = []
        for index,t_item in enumerate(item):
            #title = t_item['title']
            level = t_item['type']
            if level != 'Warning':
                del_list.append(index)
        del_list.reverse()
        for tempt in del_list:
            info_list.append(item[tempt])
            del item[tempt]
        slither_info.append(info_list)
    bb['mythril_analysis_not_info'] = slither_temp

    cc = bb[bb['dealed_code'].apply(lambda x : len(x) > 2 )]
    cc = cc.reset_index()
    toolNames = ['mythril_analysis_not_info','osiris_analysis','slither_analysis_not_info']
    print('{} {}'.format('mythril', get(cc, ['mythril_analysis_not_info'])))
    print('{} {}'.format('osiris', subDict(get(cc, ['mythril_analysis_not_info','osiris_analysis']), get(cc, ['mythril_analysis_not_info']))))
    print('{} {}'.format('slither', subDict(get(cc, ['mythril_analysis_not_info','osiris_analysis','slither_analysis_not_info']), get(cc, ['mythril_analysis_not_info','osiris_analysis']))))
    print('total:',end = ' ')
    total = get(cc, ['mythril_analysis_not_info','osiris_analysis','slither_analysis_not_info'])
    count = 0
    for item in total:
        count += total[item]
    print(total)
    print(count)
    cc.to_pickle(storeAddr)

    
sniPathF = "/home/yfliu/paper_data/conFunFormat/snippet_function.csv"
sniPathC = "/home/yfliu/paper_data/conFunFormat/snippet_contract.csv"

codePathF = "/home/yfliu/paper_data/conFunFormat/code_function.csv"
codePathC = "/home/yfliu/paper_data/conFunFormat/code_contract.csv"

#ast
#matchPathF = "/home/yfliu/paper_data/matchRes/match_function_v2.pic"
#matchPathC = "/home/yfliu/paper_data/matchRes/match_contract_v2.pic"  
#bugResAddr = '/home/yfliu/paper_data/completeRes/match_bug_res_v2.pic'
#funStoreAddr = '/home/yfliu/paper_data/astResultCsv/functionRes_v2.pic'
#conStoreAddr = '/home/yfliu/paper_data/astResultCsv/contractRes_v2.pic'

#nicad2c
#matchPathF = "/home/yfliu/paper_data/matchRes/nicadFunMatch.pic"
#matchPathC = "/home/yfliu/paper_data/matchRes/nicadConMatch.pic" 
#bugResAddr = '/home/yfliu/paper_data/completeRes/nicadBugRes.pic'
#funStoreAddr = '/home/yfliu/paper_data/astResultCsv/functionRes_nicad.pic'
#conStoreAddr = '/home/yfliu/paper_data/astResultCsv/contractRes_nicad.pic'

'''#nicad32c
matchPathC = '/home/yfliu/paper_data/matchRes/nicad32CConMatch.pic'
matchPathF = '/home/yfliu/paper_data/matchRes/nicad32CFunMatch.pic'
bugResAddr = '/home/yfliu/paper_data/completeRes/nicad32CBugRes.pic'
funStoreAddr = '/home/yfliu/paper_data/astResultCsv/functionRes_nicad32C.pic'
conStoreAddr = '/home/yfliu/paper_data/astResultCsv/contractRes_nicad32C.pic'
'''

matchPathC = '/home/yfliu/paper_data/matchRes/manualMatchCon.pic'
matchPathF = '/home/yfliu/paper_data/matchRes/manualMatchFun.pic'
bugResAddr = '/home/yfliu/paper_data/completeRes/manualBugRes.pic'
funStoreAddr = '/home/yfliu/paper_data/astResultCsv/functionRes_manual.pic'
conStoreAddr = '/home/yfliu/paper_data/astResultCsv/contractRes_manual.pic'

run_sTs(sniPathC, codePathC, matchPathC, conStoreAddr, bugResAddr)
run_sTs(sniPathF, codePathF, matchPathF, funStoreAddr, bugResAddr)