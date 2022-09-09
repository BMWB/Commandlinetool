#!/usr/bin/python3
#_*_ coding: utf-8 _*_

'Compile context module'

_author_ = 'Yaping Liu'

import sys
import os
import shutil
import json                  
   
PACKAGE_NAME                    = "KZStaticAnalyzer"
           

class CompileContext():
    def __init__(self, mainPath, customExcludeDirs):
        #basic private vars
        self.__mainPath = mainPath
        self.__includeHeadersDir = None
        self.__analyzerTempDir = None
        self.__checkLogPath = ''
        self.__formatSDKPath = None
        self.__checkSDKPath = None
        self.__formatConfig = None
        self.__compileFilePaths = []
        self.__formatHeaderPaths = []
        self.__pchHeaderPaths = []
        self.__podHeaderDirPath = None
        self.__frameWorkPaths = []
        self.__clangParamsCmd = None
        self.__xprojMangePath = None
        #handle exclude dirs
        self.__excludeDirs = ['Pods', PACKAGE_NAME]
        if customExcludeDirs and isinstance(customExcludeDirs, list) and len(customExcludeDirs) > 0:
            for dirName in customExcludeDirs:
                if not dirName in self.__excludeDirs:
                    self.__excludeDirs.append(dirName)


    """ 
    Object Properties
    """
    @property
    def mainPath(self):
        return self.__mainPath

    @property
    def formatSDKPath(self):
        return self.__formatSDKPath

    @property
    def checkSDKPath(self):
        return self.__checkSDKPath

    @property
    def checkLogPath(self):
        return self.__checkLogPath
    
    @property
    def formatConfig(self):
        return self.__formatConfig

    @property
    def clangParamsCmd(self):
        if not self.__clangParamsCmd:
            self.__clangParamsCmd = self.__getClangParamsCmd()
        return self.__clangParamsCmd

    @property
    def compileFilePaths(self):
        return self.__compileFilePaths
    
    @property
    def formatHeaderPaths(self):
        return self.__formatHeaderPaths

    @property
    def libRootDirName(self):
        return PACKAGE_NAME

    @property
    def excludeDirNames(self):
        return self.__excludeDirs

    @property
    def xprojMangePath(self):
        return self.__xprojMangePath

    """ 
    Object Public Methods
    """
    def configBasicInfos(self):
        ''' General config '''
        #main path
        if not self.__mainPath or not os.path.exists(self.__mainPath):
            print('Unable to find project path : %s' % self.__mainPath)
            return False
        
        #static check log path
        self.__checkLogPath = os.path.join(self.__mainPath, 'kz_static_check_log.txt')

        #lib main dir path
        libMainDirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        #static check run time temp dir
        self.__analyzerTempDir = os.path.join(libMainDirPath, 'AnalyzerTemp')
        
        ''' Format config '''
        #format sdk
        self.__formatSDKPath = os.path.join(libMainDirPath, 'bin/clang-format')
        if not os.path.exists(self.__formatSDKPath):
            print("Unable to find clang-format tool!")
            return False
        #format config
        self.__formatConfig = self.__getConfigJSONString()
        if not self.__formatConfig:
            print('Clang format config error!')
            return False
        

        ''' Static check config '''
        #analyze sdk
        self.__checkSDKPath = os.path.join(libMainDirPath, 'bin/KZStaticAnalyzer')
        if not os.path.exists(self.__checkSDKPath):
            print("Can't find KZStaticAnalyzer tool!")
            return False
        #create headers dir
        self.__includeHeadersDir = os.path.join(self.__analyzerTempDir, 'IncludeHeaders')
        if os.path.exists(self.__includeHeadersDir):
            shutil.rmtree(self.__includeHeadersDir, ignore_errors=True)
        os.makedirs(self.__includeHeadersDir)
        
        '''xporj manage'''
        self.__xprojMangePath = os.path.join(libMainDirPath, 'execute/XcodeprojManager.rb')

        ''' Valid '''
        self.__extractFilesMethod()
        return True


    def clearConfigInfos(self):
        ''' Clean '''
        #clean headers
        if self.__analyzerTempDir and os.path.exists(self.__analyzerTempDir):
            shutil.rmtree(self.__analyzerTempDir, ignore_errors=True)

    """ 
    Object Private Methods
    """
    def __getClangParamsCmd(self):
        #create clang include args
        clangCmd = ' --'
        #-isysroot
        sysPath = ' -isysroot/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk'
        clangCmd += sysPath
        #-fmodules
        clangCmd += ' -fmodules'
        #-I
        clangCmd += (' -I' + self.__includeHeadersDir)
        #-I resolve #import<A/A.h> for pod
        if self.__podHeaderDirPath:
            clangCmd += (' -I' + self.__podHeaderDirPath)
        #-F resolve contain third framework.
        if self.__frameWorkPaths and len(self.__frameWorkPaths) > 0:
            for frameP in self.__frameWorkPaths:
                clangCmd += (' -F' + frameP)
        #add pch headers by '-include'
        if len(self.__pchHeaderPaths) > 0: 
            includePCHCmd = ''
            for pchPath in self.__pchHeaderPaths:
                includePCHCmd += (' -include' + pchPath)        
            clangCmd += includePCHCmd
        
        return clangCmd


     #Categorize project files
    
    #Categorize project files
    def __extractFilesMethod(self):
        if os.path.isdir(self.__mainPath):
            for root, sub_dirs, files in os.walk(self.__mainPath):
                #filter package files
                buildTemp = '/.buildtemp'
                exportBuild = '/derivedData'
                if PACKAGE_NAME in root or buildTemp in root or exportBuild in root:
                    continue
                #search pod header for static lib
                if not self.__podHeaderDirPath and root.endswith('Pods/Headers/Public'):
                    self.__podHeaderDirPath = root
                #search .framework path
                if root.endswith('.framework') and not root in self.__frameWorkPaths:
                    dirPath = os.path.dirname(root)
                    self.__frameWorkPaths.append(dirPath)
                #whether is exclude root
                isExcludeRoot = False
                for excludeDN in self.__excludeDirs:
                    endIdf = '/'+excludeDN
                    containIdf = endIdf+'/'
                    if root.endswith(endIdf) or containIdf in root:
                        isExcludeRoot = True
                        break
                #files category 
                for fn in files:
                    fp = os.path.join(root, fn)
                    if not os.path.exists(fp) or fn.endswith('.pch.pch'):
                        continue
                    if (fn.endswith('.h') or fn.endswith('.hpp') or fn.endswith('.pch')):
                        #copy compile header files
                        if self.__includeHeadersDir:
                            targetp = os.path.join(self.__includeHeadersDir, os.path.basename(fp))
                            if not os.path.exists(targetp):
                                #use `copyfile` method to resolve permission error
                                dstPath = shutil.copyfile(fp, targetp)
                                if dstPath and dstPath.endswith('.pch'):
                                    self.__pchHeaderPaths.append(dstPath)
                        
                        #search format header files
                        if not isExcludeRoot and not fp in self.__formatHeaderPaths and not '.pbobjc.' in fn:
                            self.__formatHeaderPaths.append(fp)
                    elif not isExcludeRoot and \
                        (fn.endswith('.m') or fn.endswith('.mm')) \
                        and not fp in self.__compileFilePaths and not '.pbobjc.' in fn:
                            self.__compileFilePaths.append(fp)

    def __getConfigJSONString(self):
        braceWrappingMap = {
                            #switch 语句case后面的花括号不需要换行
                            'AfterCaseLabel': 'false', 
                            #if等控制语句花括号不需要换行
                            'AfterControlStatement': 'false',
                            #枚举后面的花括号需要换行
                            'AfterEnum': 'true', 
                            #函数后面的花括号需要换行
                            'AfterFunction': 'false',
                            #else不切换换到下一行
                            'BeforeElse': 'false', 
                            #空方法体不能放在一行
                            'SplitEmptyFunction': 'true'
                            }
        configMap = {
                    #括号中参数水平平铺上下对齐
                    'AlignAfterOpenBracket':'Align',
                    #连续宏对齐
                    'AlignConsecutiveMacros':'true',
                    #换行符号`\`靠左对齐
                    'AlignEscapedNewlines':'Left',
                    #不允许短的case 标签在一行上
                    'AllowShortCaseLabelsOnASingleLine':'false',
                    #不允许短的函数体在同一行
                    'AllowShortFunctionsOnASingleLine':'None',
                    #返回类型与声明换行
                    'AlwaysBreakAfterReturnType':'None',
                    #如果超过行数限定值，c函数所有参数均单行展示
                    'BinPackParameters':'false',
                    'BraceWrapping': braceWrappingMap,
                    #括号换行方式
                    'BreakBeforeBraces':'Custom',
                    #行限制列数
                    'ColumnLimit':'160',
                    #case标签需要缩进
                    'IndentCaseLabels':'true',
                    #用于缩进的列数
                    'IndentWidth':'4',
                    #block体内缩进数
                    'ObjCBlockIndentWidth':'4',
                    #属性后面加空格
                    'ObjCSpaceAfterProperty':'true',
                    #协议前面加空格
                    'ObjCSpaceBeforeProtocolList':'true',
                    #指针标志 * 的位置
                    'PointerAlignment':'Right',
                    #不进行引入头文件排序
                    'SortIncludes':'false',
                    #赋值符号左边加空格
                    'SpaceBeforeAssignmentOperators':'true',
                    #继承时候冒号前面不加空格
                    'SpaceBeforeInheritanceColon':'false',
                    #控制语句之后括号之前有空格
                    'SpaceBeforeParens':'ControlStatements'
                    }   
        configJson = json.dumps(configMap)
        return configJson   
        
        

#main
def main():
    return 0


if __name__ == '__main__':
    # analyzer = CompileContext('/Users/doit/Desktop/Example', [])
    # analyzer.configBasicInfos()
    # analyzer.clearConfigInfos()
    print('The script cannot be used alone')
else:
    main()






