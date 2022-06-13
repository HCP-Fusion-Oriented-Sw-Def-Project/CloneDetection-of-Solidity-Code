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
import gc
punc = punctuation
smooth = SmoothingFunction()

def preorderDemand(root,demandKey, keyValue, keyName):
    if type(root) == str:
        root = eval(root)
    if not root or type(root) == float:
        return
    result = []
    def pre_order(root):
        if type(root) == dict:
            if demandKey in root and root[demandKey] in keyValue:
                tempList = []
                for name in keyName:
                    tempList.append(root[name])
                if len(tempList) == 1:
                    result.append(tempList[0])
                else:
                    result.append(tempList)
            for key,value in root.items():
                if type(value) in [dict, list]:
                    pre_order(value)
        elif type(root) == list:
            for item in root:
                pre_order(item)
    pre_order(root)
    return result
#前序遍历
def preorder(root,keyName):
    if not root:
        return
    result = []
    def pre_order(root):
        if type(root) == dict:
            if keyName in root:
                result.append(root[keyName])
            for key,value in root.items():
                if type(value) in [dict, list]:
                    pre_order(value)
        elif type(root) == list:
            for item in root:
                pre_order(item)
    pre_order(root)
    return result

#使用parser获得ast
def loadAST(text):
    try:
        text = parser.parse(text)
        text = json.loads(json.dumps(text))
    except BaseException:
        return None
    return text

#找到片段的匹配，返回idx列表
def matchType(sni,codeList):
    print(sni['index'])
    sniType = sni['hashSeries']
    posList = codeList.apply(lambda codeItem, sni = sniType:codeItem['hashSeries'] == sni,axis = 1)
    return [idx for idx, item in enumerate(list(posList)) if item]

#解决函数无法生成ast的问题，加一个contract外壳
def addHeadForFunction(function, isFunc):
    head = '''contract temp{'''
    end = '''}'''
    return head + function + end if isFunc else function

#生成类型序列与名称序列
def runAST(series):
    astSeries = series.apply(lambda x:loadAST(x))
    print(astSeries)
    type_code = astSeries.apply(lambda x:preorder(x, 'type'))
    name_code = astSeries.apply(lambda x:preorder(x, 'name'))
    return astSeries, type_code, name_code

def runASTName(series):
    astSeries = series.apply(lambda x:loadAST(x))
    #print(astSeries)
    funcModifier = astSeries.apply(lambda x:preorderDemand(x, 'type', ['FunctionDefinition'], ['visibility', 'stateMutability']))
    typeName=astSeries.apply(lambda x:preorderDemand(x, 'type', ['ElementaryTypeName'], ['name']))
    paraName=astSeries.apply(lambda x:preorderDemand(x, 'type', ['Parameter'], ['name']))
    '''
    for item in astSeries:
       # print(type(item))
        funcModifier.append(preorderDemand(item, 'type', ['FunctionDefinition'], ['visibility', 'stateMutability']))
        typeNamer.append(preorderDemand(item, 'type', ['ElementaryTypeName'], ['name']))
        paraName.append(preorderDemand(item, 'type', ['Parameter'], ['name']))
        gc.collect()
    '''
    return astSeries.apply(lambda x : json.dumps(x)), funcModifier.apply(lambda x : json.dumps(x)), typeName.apply(lambda x : json.dumps(x)), paraName.apply(lambda x : json.dumps(x))

def tempFuncName(codeName, isFunc):
   # print(codeName)
    codeName['AST'], codeName['funcModifier'], codeName['typeNameSeries'], codeName['paraNameSeries'] = runASTName(codeName['code'].apply(lambda function, isFunc = isFunc : addHeadForFunction(function, isFunc)))

#解决函数需要额外加add的问题
def tempFunc(codeName, isFunc):
    #if isFunc:
        #codeName['AST'], codeName['typeSeries'], codeName['nameSeries'] = runAST(codeName['code'].apply(addHeadForFunction))
    #else:
    #    codeName['AST'], codeName['typeSeries'], codeName['nameSeries'] = runAST(codeName['code'])
    codeName['AST'], codeName['typeSeries'], codeName['nameSeries'] = runAST(codeName['code'].apply(lambda function, isFunc = isFunc : addHeadForFunction(function, isFunc)))
        
def encode_str(text, char_frequency, codes):
    if type(text) == float:
        #print('error')
        return None
    ret = ''
    for char in eval(text):
        for i, key in enumerate(char_frequency):
           # print(item)
            if char == key:
                ret += codes[i]
    return ret


#读取so与xblock的合约与函数 在最后一步从paper_data获得数据
snippet_contract = pd.read_csv("../../paper_data/snippet_contract.csv")
snippet_function = pd.read_csv("../../paper_data/snippet_function.csv")
code_contract = pd.read_csv("../../paper_data/code_contract.csv")
code_function = pd.read_csv("../../paper_data/code_function.csv")

tempFuncName(snippet_contract,False)
snippet_contract.to_csv("../../paper_data/snippet_contract.csv",index = False)
tempFuncName(snippet_function,True)
snippet_function.to_csv("../../paper_data/snippet_function.csv",index = False)
tempFuncName(code_contract,False)
code_contract.to_csv("../../paper_data/code_contract.csv",index = False)
tempFuncName(code_function,True)
code_function.to_csv("../../paper_data/code_function.csv",index = False)