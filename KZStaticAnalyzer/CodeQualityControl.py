#!/usr/bin/python3
#_*_ coding: utf-8 _*_

'Code quality control module'

_author_ = 'Yaping Liu'

import sys
import os
import argparse
import subprocess
            
from execute.CompileContext import CompileContext
from execute.FileProcessor import KZClangAnalyzer, KZClangFormat
         

def handleFilesWithConfig(needStaticCheck, needFormatCode, basicConfigObj):
    #format code
    if needFormatCode and basicConfigObj.formatSDKPath:
        print('\n========= Code Format =========')
        validFormatFiles = basicConfigObj.compileFilePaths + basicConfigObj.formatHeaderPaths
        KZClangFormat.fileFormat(basicConfigObj.formatSDKPath, 
                                validFormatFiles,
                                basicConfigObj.formatConfig)

    #analyze check
    result = ''
    leak = ''
    if needStaticCheck and basicConfigObj.checkSDKPath:
        print('========= Code Analyze =========')
        (result, leak) = KZClangAnalyzer.fileAnalyze(basicConfigObj.compileFilePaths,
                                                    basicConfigObj.checkSDKPath,
                                                    basicConfigObj.clangParamsCmd)
        #write log
        if len(result) > 0:
            with open(basicConfigObj.checkLogPath,'w+') as file:
                file.write(result)
            print('\nAnalyze complete with log path: ' + basicConfigObj.checkLogPath)
        else:
            print('\nAnalyze complete with no exceptions!')
    
    return (result, leak)



def startAnalyze(needStaticCheck, needFormatCode, mainPath, customExcludeDirs):
    #initialize config
    basicConfigObj = CompileContext(mainPath, customExcludeDirs)
    success = basicConfigObj.configBasicInfos()
    if not success:
        return

    (result, leakResult) = handleFilesWithConfig(needStaticCheck, needFormatCode, basicConfigObj)

    #clean
    basicConfigObj.clearConfigInfos()

    print('\n🎉 🎉 Analyze Finish!')
    return (result, basicConfigObj.checkLogPath, leakResult)


def main():
    #parser
    parser = argparse.ArgumentParser(description='Code quality control lib!')
    parser.add_argument('-c', '--check', action='store_true', help='static check')
    parser.add_argument('-f', '--format', action='store_true', help='code format')
    parser.add_argument('-m', '--mainPath', type=str, help='project main path')
    parser.add_argument('-d', '--dirs', nargs='+', help='analyze dirs that need be excluded')
    parserParams = parser.parse_args()

    startAnalyze(parserParams.check, parserParams.format, parserParams.mainPath, parserParams.dirs)
  


if __name__ == "__main__":
    main()






