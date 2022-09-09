#!/usr/bin/python3
#_*_ coding: utf-8 _*_

'clang module'

_author_ = 'Yaping Liu'

import sys
import os
import argparse
import subprocess
import queue
import threading
from execute.YPOperationQueue import OperationQueue

PRINT_IDENTIFIER_START          = "#S#"

PRINT_IDENTIFIER_END            = "#E#"

EXTRACT_LEAK_START              = "🔧🔧🔧  Block Leak :"

EXTRACT_LEAK_END                = "🔧🔧🔧"
               

class KZClangAnalyzer():
    @classmethod
    def fileAnalyze(cls, complieFilePaths, sdkPath, clangCmd):
        #multiple thread check
        l_checkLeak = ''
        l_checkLog = ''
        l_queueLock = threading.Lock()
        def staticCheck(taskInfo):
            nonlocal l_checkLeak
            nonlocal l_checkLog
            nonlocal l_queueLock

            cp = taskInfo.currentTask
            fileName = os.path.basename(cp)
            print('\n🔧🔧 %s Analyzing %s ...' % (taskInfo.name, fileName))
            runCmd = sdkPath + ' ' + cp + clangCmd
            op = subprocess.getoutput(runCmd)
            if PRINT_IDENTIFIER_START in op and PRINT_IDENTIFIER_END in op:
                result = op.split(PRINT_IDENTIFIER_START)[1]
                result = result.split(PRINT_IDENTIFIER_END)[0]
                #extract leak part
                leakResult = None
                if EXTRACT_LEAK_START in result:
                    leakResult = result.split(EXTRACT_LEAK_START)[1]
                    if EXTRACT_LEAK_END in leakResult:
                        leakResult = leakResult.split(EXTRACT_LEAK_END)[0]
                #save result
                logTitle = '\n------------ ' + fileName + ' ------------\n'
                log = logTitle
                log += result
                l_queueLock.acquire()
                l_checkLog += log
                if leakResult:
                    l_checkLeak = l_checkLeak + logTitle + leakResult
                l_queueLock.release()
        #multi threads operation
        opq = OperationQueue(threadsCount=8, operationFunc=staticCheck)
        opq.startOperation(complieFilePaths)
        #return result
        return(l_checkLog, l_checkLeak)

       


class KZClangFormat():
    @classmethod
    def fileFormat(cls, formatSdkPath, fomatFilePaths, formatConfig):
        if len(fomatFilePaths) < 1:
            return
        def formatMethod(taskInfo):
            cp = taskInfo.currentTask
            fileName = os.path.basename(cp)
            print('\n🔧🔧 Foramt ' + fileName + ' ...')
            command = [formatSdkPath, cp, '-style', formatConfig, '-i']
            p = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=None,
                                stdin=subprocess.PIPE,
                                universal_newlines=True)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                print('\n🔧🔧 Foramt ' + fileName + ' failed !')

        #start format code
        opq = OperationQueue(threadsCount=8, operationFunc=formatMethod)
        opq.startOperation(fomatFilePaths)

    @classmethod
    def fileLinesFormat(cls, formatSdkPath, fileAndLinesDic, formatConfig):
        if len(fileAndLinesDic) < 1:
            return
        fomatFilePaths = list(fileAndLinesDic.keys())
        def formatMethod(taskInfo):
            cp = taskInfo.currentTask
            fileName = os.path.basename(cp)
            print('\n🔧🔧 Foramt ' + fileName + ' ...')
            command = [formatSdkPath, cp, '-style', formatConfig, '-i']
            lines = fileAndLinesDic[cp]
            command.extend(lines)
            p = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=None,
                                stdin=subprocess.PIPE,
                                universal_newlines=True)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                print('\n🔧🔧 Foramt ' + fileName + ' failed !')

        #start format code
        opq = OperationQueue(threadsCount=8, operationFunc=formatMethod)
        opq.startOperation(fomatFilePaths)

    
'''
    with open(fullPath) as f:
        code = f.readlines()
        formatted_code = StringIO(stdout).readlines()
        diff = difflib.unified_diff(code, formatted_code,
                                    filename, filename,
                                    '(before formatting)', '(after formatting)',0)
        diff_string = ''.join(diff)
        if len(diff_string) > 0:
            print(diff_string)
'''

#main
def main():
    return 0


if __name__ == '__main__':
    print('The script cannot be used alone')
else:
    main()







