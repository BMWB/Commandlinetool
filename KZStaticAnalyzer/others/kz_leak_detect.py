#!/usr/bin/python
#_*_ coding: utf-8 _*_

'a ios memory leak detect module'

_author_ = 'Yaping Liu'

import sys
import os
import argparse
import re

class KZBlockClass:
    def __init__(self):
        self.startIndex = 0
        self.endIndex = 0
        self.errorLine = 0
        self.errorLineContent = None


class KZMemoryLeakDetector:
    def __init__(self, mainPath, exclusiveRelativePaths):
        self.__mainPath = mainPath
        self.__exclusiveRelativePaths = exclusiveRelativePaths
        filesList = self.__extractFiles()
        for perFile in filesList:
            self.__split_note_content(perFile)
   
   
    #scan_files
    def __extractFiles(self):
        filesList = []
        pathsList = []
        #get valid dirs
        paths = os.listdir(self.__mainPath)
        if not self.__exclusiveRelativePaths:
            exclusivePaths = []
        for subPath in paths:
            if subPath[0] != '.' and subPath not in self.__exclusiveRelativePaths:
                pathsList.append(subPath)
        #get valid files
        for filePath in pathsList:
            subProjectPath = os.path.join(self.__mainPath,filePath)
            for root, sub_dirs, files in os.walk(subProjectPath):
                for file in files:
                    if file.endswith('.m'):
                        filesList.append(os.path.join(root,file))

        return filesList


    #detect_content
    def __split_note_content(self, filePath):
        with open(filePath,'r') as file:
            fileTotalLines = file.readlines()
            comment_symbols = 0   # /*
            has_block_symbol = False   # ^
            left_brace_num = 0 # {
            program_start_symbols = 0  # @implementation
            start_index = -1
            end_index = -1
            for lineIndex, perLineContent in enumerate(fileTotalLines):
                perTripContent = perLineContent.replace(' ','')
                if not perTripContent.startswith('//'):
                    #exclusive comments
                    if '/*' in perTripContent and '*/' in perTripContent:
                        continue
                    elif '/*' in perTripContent:
                        comment_symbols += 1
                        continue
                    elif '*/' in perTripContent:
                        comment_symbols -= 1
                        continue
                    if comment_symbols == 0:
                        #check valid code
                        if '@implementation' in perTripContent:
                            program_start_symbols += 1

                        elif program_start_symbols > 0 and '@end' in perTripContent:
                            program_start_symbols -= 1

                        if (program_start_symbols == 0) or \
                            self.__isSafeMethodWithSelf(perTripContent) or \
                            self.__isSpecialMethodsNeedIgnore(perTripContent):
                            continue
                        
                        #get block content position
                        if not has_block_symbol and '^' in perTripContent:
                            has_block_symbol = True
                            start_index = lineIndex
                            blk_right_content = perTripContent.split('^')[-1]
                            left_brace_num += self.__checkLeftBraceNumForContent(blk_right_content)
                            if left_brace_num <= 0:
                                end_index = lineIndex
                        elif has_block_symbol:
                            left_brace_num += self.__checkLeftBraceNumForContent(perTripContent)
                            if left_brace_num <= 0:
                                end_index = lineIndex
                        else:
                            continue
                        
                        #capture block content
                        #TODO:use string index to index capture block content
                        if has_block_symbol and left_brace_num <= 0 \
                            and end_index > -1 and start_index > -1:
                            self.__detect_usefulContent(fileTotalLines[start_index:end_index+1],start_index,filePath)
                            has_block_symbol = False
                            end_index = -1
                            start_index = -1
                            

    #detect_usefulContent
    def __detect_usefulContent(self,usefulLines,startIndex,fileName):
        
        tempFirst = usefulLines[0].rpartition('^')[-1]
        usefulLines[0] = tempFirst
        tempLast = usefulLines[-1].partition('}')[0]
        usefulLines[-1] = tempLast
        
        for index ,perUsefulStr in enumerate(usefulLines):
            if not 'self' in perUsefulStr:
                continue
            perTripStr = perUsefulStr.replace(' ','')
            perTripStr = perTripStr.replace('block_self','')
            perTripStr = perTripStr.replace('weakSelf','')
            perTripStr = perTripStr.replace('weakself','')
            perTripStr = perTripStr.replace('weak_self','')
            perTripStr = perTripStr.replace('strong_self','')
            perTripStr = perTripStr.replace('.self','')

            if not perTripStr.startswith('//') and 'self' in perTripStr:
                print('----- Leak Entry -----')
                print('File path: %s' % (fileName))
                print('Line number: %d' % (startIndex+index+1))
                print('Leak code: %s\n' % (perUsefulStr.strip()))


    #Judge valid methods that contain `self`.
    def __isSafeMethodWithSelf(self, perLine):
        if ('^' in perLine and 'animation' in perLine) or \
        ('^' in perLine and 'completion' in perLine) or \
        ('(^)' in perLine) or\
        ('dispatch_' in perLine):
            return True
        else:
            return False

    def __isSpecialMethodsNeedIgnore(self, perLine):
        #:(xxx (^ xxx) (xxx xxx)) 
        blockParamsPattern = re.compile(r':{1}\s*\({1}[\w\s]+\({1}\s*\^{1}[\w\s]*\){1}\s*\({1}[\w\s]*\){1}\s*\){1}',re.M)
        serRe = re.search(blockParamsPattern, perLine)
        if (serRe):
            return True
        else:
            return False


    def __checkLeftBraceNumForContent(self, content):
        if not content:
            return 0
        leftBraceNum = 0
        if '{' in content:
            leftBraceNum = content.count('{')
        if '}' in content:
            leftBraceNum -= content.count('}')
        
        return leftBraceNum   



#main
def main():
    print('####### 检测工程内存泄露 ########')
    #parser
    parser = argparse.ArgumentParser(description='start args for memory leak detect!')
    parser.add_argument('-m', '--mainPath', type=str, help='project path')
    parserParams = parser.parse_args()
    projectPath = parserParams.mainPath

    if not projectPath:
        projectPath = os.path.pardir
    #custom exclusivePath
    exclusivePaths = ['Pods','Demo','Quick', 'ThirdLib']
    
    KZMemoryLeakDetector(projectPath, exclusivePaths)

    print('####### 结束工程内存泄露 ########')

if __name__ == '__main__':
    main()




