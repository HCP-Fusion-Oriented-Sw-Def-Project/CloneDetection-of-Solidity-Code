import pandas as pd
import docker
import os
import re
import json
import time

def TIMEOUT_COMMAND(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    cmd = command
    #print(cmd)
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
    while process.poll() is None:
        time.sleep(0.2)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            #print('timeout ----------1')
            errorlog = open('/home/yfliu/runSmartBugsErrorLog','a')
            errorlog.write(cmd + '\n')
            errorlog.close()
            print('timeout ----------2')
            return None
    return process.stdout.readlines()

def run_smartbugs(sol_list,root_dir,tools,save_addr,runLen, fihSol):
    print('runLen {}'.format(runLen))
    startTime = time.time()
    for i in range(runLen):
        #print(i)
        #if i % 100 == 0:
            #print('index {} second {} now {}'.format(i, time.time() - startTime, time.ctime()))
        solName = sol_list[i]
        if '.sol' not in solName:
            solName += '.sol'
        solComName = os.path.join(root_dir,solName)
        tempTList = [item for item in tools if solName.split('.')[0] not in fihSol[item]]
        #tempTList = ['osiris' if colComName not in fihSol['osiris']
        if len(tempTList) > 0  and ':' not in solName:
            print("{} {} {} {}".format(i, solComName, tempTList, time.ctime()))
            inputText = "cd /home/yfliu/smartbugs;python3 smartBugs.py --tool {} --file {}".format(' '.join(tempTList),solComName)
            #text = os.popen(inputText).read()
            pipe = TIMEOUT_COMMAND(inputText,60 * 60 * 5);

            #print("{} {} {} {}".format(i, solComName, tempTList, time.ctime()))


def get_addr(tool,rootList):
    code = []
    for root in rootList:
        directory = os.listdir(os.path.join(root,tool))
        for addr in directory:
            temp = os.path.join(root,tool,addr)
            code_dir = os.listdir(temp)#获得到达result.json的地址 
            for code_addr in code_dir:
                code.append(code_addr)
    return code 

toolPath = ['/home/yfliu/smartbugs/results','/home/yfliu/paper_data/bug_result/result_125/smartbugs/results','/home/yfliu/paper_data/bug_result/result_21/smartbugs/results']
toolList = ['mythril','slither','osiris']
fihSol = {}
for item in toolList:
    fihSol[item] = os.listdir('/home/yfliu/paper_data/contractResult/' + item)

rootAddr = '/home/yfliu/paper_data/contractResult/'
total = set(os.listdir('/home/yfliu/data_sol'))
total = set(pd.Series(list(total)).apply(lambda x : x.split('.')[0]))
mythril = set(os.listdir(os.path.join(rootAddr, 'mythril')))
osiris = set(os.listdir(os.path.join(rootAddr, 'osiris')))

rootDir = os.path.join("/home/yfliu/data_sol")
runList = os.listdir('/home/yfliu/data_sol')
#runList = open('/home/yfliu/data_sol_split_83.csv').read().split('\n')#需要运行的合约
#runList = pd.read_csv('/home/yfliu/.csv')['0']
run_smartbugs(runList,rootDir,['mythril','osiris'],'~/17wBugResult',len(runList), fihSol)
