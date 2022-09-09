#!/usr/bin/python
#_*_ coding: utf-8 _*_

'clang module'

_author_ = 'Yaping Liu'

import clang
from clang.cindex import CursorKind, TokenKind, StorageClass
import sys
import os
import argparse

_g_debug = False

''' Block leak module '''
_g_check_block = True
_g_includeDirs = ['BossZP','BZBasic','BZBusiness']
# _g_includeDirs = []


''' Class module '''
_g_check_class = False
_g_exclusiveClasses = []


''' C method module '''
_g_check_CMethod = False



class KZClangParse():
    def __init__(self, complieFilePaths, headerFileDirs, exclusiveClasses, mainPath):
        clangLibPath = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib'
        clang.cindex.Config.set_library_file(clangLibPath)
        self.__indexObj = clang.cindex.Index.create(True)
        self.__mainPath = mainPath
        #class private vars
        self.__exclusiveClasses = exclusiveClasses
        self.__allClasses = []
        self.nonstandardClasses = []
        #block private vars
        self.blockLeakEntries = []
        #c method private vars
        self.nonstandardCMethods = []

        #create clang include args
        includeCmds = []
        #-isysroot
        sysPath = '-isysroot/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator12.0.sdk'
        includeCmds.append(sysPath)
        #-fmodules
        includeCmds.append('-fmodules')
        if headerFileDirs and len(headerFileDirs) > 0:
            for hd in headerFileDirs:
                perCmd = '-I' + hd
                includeCmds.append(perCmd) 
        
        #diagnostics
        diagDic = {'0': 'Ignored', '1': 'Note' ,'2': 'Warning', '3': 'Error', '4': 'Fatal'}
        def printDiagnostics(tu): 
            if not _g_debug:
                return
            for d in tu.diagnostics:
                excReason = str(d.category_number)
                if excReason in diagDic:
                    excReason = diagDic[excReason] 
                print(excReason + ': ' + d.spelling)
                
        #check
        for cp in complieFilePaths:
            tu = self.__indexObj.parse(cp, includeCmds)
            if _g_check_block:
                printDiagnostics(tu)
                self.__blockLeakCheck(cp, tu.cursor)
            if _g_check_class:
                self.__classNameCheck(tu.cursor)
            if _g_check_CMethod:
                self.__cMethodPreCheck(tu.cursor)
        
        if _g_check_class:
            print('\n🎉 🎉  Class detect complete, all: %d, nonstandard: %d' % (len(self.__allClasses), len(self.nonstandardClasses)))
            
        if _g_check_CMethod:
            print('\n🎉 🎉  C method detect complete, nonstandard: %d' % len(self.nonstandardCMethods))          


        if _g_check_block and _g_debug:
            #block write
            if len(self.blockLeakEntries) > 0:
                blockCheckLog = ''.join(self.blockLeakEntries)
                savePath = os.path.join(self.__mainPath,'kz_block_leak_log.txt')
                with open(savePath,'w+') as file:
                    file.write(blockCheckLog)
                print('\n🎉 🎉  Block detect complete, log path: ' + savePath)


    def __classNameCheck(self, cursor):
        for c in cursor.get_children():
            if c.kind == CursorKind.OBJC_IMPLEMENTATION_DECL:
                className = c.spelling
                if not className in self.__allClasses:
                    self.__allClasses.append(className)
                    if not className in self.__exclusiveClasses:
                        if not className.startswith('BZ') and \
                            not className.startswith('BB') and \
                            not className.startswith('BG'):
                            self.nonstandardClasses.append(className)
                            print('Nonstandard class name: ' + className)
            else:
                self.__classNameCheck(c)


    def __cMethodPreCheck(self, cursor):
        for c in cursor.get_children():
            if c.kind == CursorKind.FUNCTION_DECL and c.storage_class != StorageClass.STATIC:
                cmethodName = c.spelling
                if not '_' in cmethodName and not cmethodName in self.nonstandardCMethods: 
                    self.nonstandardCMethods.append(cmethodName)
                    print('Nonstandard C method: ' + cmethodName)
            else:
                self.__cMethodPreCheck(c)



    def __blockLeakCheck(self, compilePath, cursor):
        #iteration
        curFPTitle = '\n\n==========%s'% compilePath
        if _g_debug:
            print(curFPTitle)

        for c in cursor.get_children():
            if c.kind == CursorKind.OBJC_IMPLEMENTATION_DECL:
                self.__iteratCheckBlockExpr(c, compilePath)


    def __iteratCheckBlockExpr(self, cursor, compilePath):
        # print('+++++++ current currosr all sub elements')
        # for tempc in cursor.get_children():
        #         print ('\nKind: ' + str(tempc.kind) + '\ntype: ' + str(tempc.type.kind) + '\nspecll: ' + tempc.spelling)
        for perC in cursor.get_children():
            # print ('\nKind: ' + str(perC.kind) + '\ntype: ' + str(perC.type.kind) + '\nspecll: ' + perC.spelling)
            
            if perC.kind == CursorKind.OBJC_CLASS_REF:
                #check node whether is valid class reference
                isValidNode = self.__isValidClassWhenCheckBlock(perC.spelling)
                if not isValidNode:
                    break
            elif perC.kind == CursorKind.CALL_EXPR:
                #check node whether is valid call expr
                isValidNode = self.__isValidCallWhenCheckBlock(perC.spelling)
                if not isValidNode:
                    break
            elif perC.kind == CursorKind.BLOCK_EXPR:
                objSelfIdentifierLines = []
                blockContent = ''
                for t in perC.get_tokens():
                    content = t.spelling
                    blockContent += (content + ' ')
                    if t.kind == TokenKind.IDENTIFIER and content == 'self':
                        lineNum = str(t.location.line)
                        if not lineNum in objSelfIdentifierLines:
                            objSelfIdentifierLines.append(lineNum)
                if len(objSelfIdentifierLines) > 0:
                    self.__printBlockLeakInfo(compilePath, objSelfIdentifierLines, blockContent)
            self.__iteratCheckBlockExpr(perC, compilePath)


    def __printBlockLeakInfo(self, fp, objSelfExprs, blockContent):
        fileName = os.path.basename(fp)
        lines = ''
        for exprLine in objSelfExprs:
            lines += (exprLine + '、 ')
        exceReport = '\n\n----- Leak Entry -----\n'
        exceReport += 'File name: %s\n' % (fileName)
        exceReport += 'Leak lines: %s\n' % (lines)
        exceReport += 'Block content: %s' % (blockContent)
        self.blockLeakEntries.append(exceReport)
        print(exceReport)


    def __isValidClassWhenCheckBlock(self, callClass):
        if callClass:
            if callClass.startswith('UI') or callClass.startswith('_UI')\
                or callClass.startswith('NS'):
                return False
        return True


    def __isValidCallWhenCheckBlock(self, callExpr):
        if callExpr:
            if 'dispatch_' in callExpr:
                return False
        return True



class KZDetector:
    def __init__(self, mainPath, includeDirs, exclusiveClasses):
        self.__mainPath = mainPath
        self.__includeDirs = includeDirs
        self.__compileFilePaths = []
        self.__headerFileDirs = []
        self.__extractFiles()
        self.clangParser = KZClangParse(self.__compileFilePaths, self.__headerFileDirs, exclusiveClasses, self.__mainPath)


    #scan_files
    def __extractFiles(self):
        #compile files
        if self.__includeDirs or len(self.__includeDirs) > 0:
            for filePath in self.__includeDirs:
                        validFullPath = os.path.join(self.__mainPath,filePath)
                        self.__searchCompileFilePaths(validFullPath)
        else:
            self.__searchCompileFilePaths(self.__mainPath)
        #header files
        self.__searchHeaderFilePaths()


    def __searchCompileFilePaths(self, searchPath):
        #add compile files
        def addCompileFP(perFilePath):
            if perFilePath.endswith('.m') or perFilePath.endswith('.mm'):
                self.__compileFilePaths.append(perFilePath)
        if os.path.isdir(searchPath):
            for root, sub_dirs, files in os.walk(searchPath):
                for f in files:
                    fullPath = os.path.join(root,f)
                    addCompileFP(fullPath)
        else:
            addCompileFP(searchPath)


    def __searchHeaderFilePaths(self):
        #add header files
        if os.path.isdir(self.__mainPath):
            for root, sub_dirs, files in os.walk(self.__mainPath):
                for fn in files:
                    if fn.endswith('.h') and not root in self.__headerFileDirs:
                        self.__headerFileDirs.append(root)
                        break

def func():
    #parser
    parser = argparse.ArgumentParser(description='start args for memory leak detect!')
    parser.add_argument('-m', '--mainPath', type=str, help='project path')
    parserParams = parser.parse_args()
    projectPath = parserParams.mainPath

    if not projectPath:
        projectPath = os.path.pardir

    detector = KZDetector(projectPath, _g_includeDirs , _g_exclusiveClasses)
    leakList = detector.clangParser.blockLeakEntries
    return leakList


def main():
    func()
  

if __name__ == "__main__":
    main()






