#!/usr/bin/env python3
#_*_ coding: utf-8 _*_#

import argparse
import difflib
import re
import subprocess
import sys, os
from io import StringIO


from execute.CompileContext import CompileContext
from execute.FileProcessor import KZClangAnalyzer, KZClangFormat

class KZIncreamentHandler:
    @classmethod
    def handleIncreamentContent(cls, mainPath, projectPath, excludeDirs=[], targetCheck=False):
        '''create context'''
        basicConfigObj = CompileContext(mainPath, excludeDirs)
        success = basicConfigObj.configBasicInfos()
        if not success:
            print('Config compile context failed!')
            return (True, {})
        '''get diff'''
        filesAndLinesDic = KZIncreamentHandler.__getModifyFilesAndLines(projectPath, basicConfigObj)
        if not filesAndLinesDic or len(filesAndLinesDic) < 1:
            #clean
            basicConfigObj.clearConfigInfos()
            return (True, {})
        '''analyze'''
        print('\n================== Code static check ==================')
        (analyzeLog, analyzeLeak) = KZClangAnalyzer.fileAnalyze(filesAndLinesDic.keys(),
                                                                basicConfigObj.checkSDKPath, 
                                                                basicConfigObj.clangParamsCmd)
        #clean
        basicConfigObj.clearConfigInfos()
        #return result
        if len(analyzeLog) > 0:
            print('\n🚫  The submission was interrupted because it contained non-standard code.\n🚫  Details are as follows:')
            print(analyzeLog)
            return (False, {})
        else:
            print('\n✅ Code analysis completed!')
        '''format'''
        print('\n================== Code format ==================')
        KZClangFormat.fileLinesFormat(basicConfigObj.formatSDKPath, 
                                    filesAndLinesDic,
                                    basicConfigObj.formatConfig)
        print('\n✅ Code format completed!')
        
        '''check file for targets'''
        if targetCheck:
            KZIncreamentHandler.__executeCheckFilesReference(basicConfigObj, projectPath, filesAndLinesDic)

        return (True, filesAndLinesDic)


    
    @classmethod
    def __getModifyFilesAndLines(cls, projectPath, basicConfigObj):
        #Get git diff content in cached.
        diffContent = subprocess.getoutput("cd %s; git diff --cached -U0  --no-color" % projectPath)
        if not diffContent or len(diffContent) < 1:
            return None
        inputContent = diffContent.splitlines()
        if len(inputContent) < 1:
            return None
        #Extract changed lines for each file.
        filename = None
        linesForFileDic = {}
        for line in inputContent:
            #search change file paths
            match = re.search(r'^\+\+\+\ (.*?/){1}(\S*)', line)
            if match:
                filePathPattern = match.group(2)
                #check exclude path
                isValidPath = True
                for excDirName in basicConfigObj.excludeDirNames:
                    excFull = excDirName + '/'
                    if excFull in filePathPattern:
                        isValidPath = False
                        break
                if isValidPath and (filePathPattern.endswith('.m') or filePathPattern.endswith('.h') or filePathPattern.endswith('.pch') or filePathPattern.endswith('.mm')):
                    filename = filePathPattern
                else:
                    filename = None
            #current line in invalid fine, so continue
            if filename == None:
                continue
            #search change lines for current file
            match = re.search(r'^@@.*\+(\d+)(,(\d+))?', line)
            if match:
                start_line = int(match.group(1))
                line_count = 1
                if match.group(3):
                    line_count = int(match.group(3))
                if line_count == 0:
                    continue
                end_line = start_line + line_count - 1
                formatCmds = ['-lines', str(start_line) + ':' + str(end_line)]
                fullPath = os.path.join(projectPath, filename)
                linesForFileDic.setdefault(fullPath, []).extend(formatCmds)
        
        #return diff
        return linesForFileDic
            
    @classmethod
    def __executeCheckFilesReference(cls, basicConfigObj, projectPath, filesAndLinesDic):
        projPath = None
        for root, sub_dirs, files in os.walk(projectPath):
            for fn in sub_dirs:
                if fn.endswith('.xcodeproj'):
                    projPath = os.path.join(root, fn)
                    break
            break
        if not projPath:
            return
        params = projPath + ' '
        for path in filesAndLinesDic.keys():
            params += ' %s' % path
        print('\n================== Files check ==================')
        op = subprocess.getoutput("ruby %s %s -W0" % (basicConfigObj.xprojMangePath, params))
        if len(op) > 0:
            print(op)
            addCmd = "cd %s; git add %s" % (projectPath, projPath)
            subprocess.getoutput(addCmd)
        print('\n✅ File check completed!')




def main():
    parser = argparse.ArgumentParser(description='Reformat changed lines in diff.')
    parser.add_argument('-m', '--mainPath', type=str, help='main path for analyzer.')
    parser.add_argument('-p', '--project', type=str, help='project path for getting modify files.')
    parser.add_argument('-d', '--dirs', nargs='+', help='dirs that need be excluded')
    parser.add_argument('-t', '--targetCheck', action='store_true', help='target check')

    args = parser.parse_args()
    mainPath = args.mainPath
    projectPath = args.project
    
    #has valid input values
    validProjectPath = projectPath and os.path.exists(projectPath)
    validMainPath = mainPath and os.path.exists(mainPath)
    if not validProjectPath or not validMainPath:
        print('You should input project path and main path!')
        return

    
    #Format commit codes
    customExcludeDirs = args.dirs
    excludeDirs = []
    if customExcludeDirs and isinstance(customExcludeDirs, list) and len(customExcludeDirs) > 0:
        excludeDirs = customExcludeDirs
        
    (complete, fpAndInfoDic) = KZIncreamentHandler.handleIncreamentContent(mainPath, projectPath, excludeDirs, args.targetCheck)
    #Add foramt change to cache
    if complete:
        if len(fpAndInfoDic) > 0:
            for fp in fpAndInfoDic.keys():
                addCmd = "cd %s; git add %s" % (projectPath, fp)
                subprocess.getoutput(addCmd)
    else:
        sys.exit(66)


if __name__ == '__main__':
  main()
