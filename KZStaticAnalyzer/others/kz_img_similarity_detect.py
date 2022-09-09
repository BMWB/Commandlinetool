#!/usr/bin/python
#_*_ coding: utf-8 _*_

'a ios image similarity detect module'

_author_ = 'Yaping Liu'

import sys
import os
import argparse
from PIL import Image
from functools import reduce


class CompareImage():
    def compareImageWithPaths(self ,fp1, fp2):
        if not os.path.exists(fp1) or not os.path.exists(fp2):
            return False

        image1 = Image.open(fp1)
        image2 = Image.open(fp2)
        if not image1 or not image2:
            return False
        # compare image dimensions (assumption 1)
        if image1.size != image2.size:
            return False

        rows, cols = image1.size

        # compare image pixels (assumption 2 and 3)
        for row in range(rows):
            for col in range(cols):
                input_pixel = image1.getpixel((row, col))
                output_pixel = image2.getpixel((row, col))
                if input_pixel != output_pixel:
                    return False

        return True



class KZDetector:
    def __init__(self, mainPath, exclusiveRelativePaths):
        self.__mainPath = mainPath
        self.__exclusiveRelativePaths = []
        if exclusiveRelativePaths:
            self.__exclusiveRelativePaths = exclusiveRelativePaths
        compareObj = CompareImage()
        self.__allFilePaths = self.__extractFiles()
        filesList = self.__allFilePaths
        report = 'Total images count: ' + str(len(filesList)) + ', compare start!'
        print(report)
        repeatImagesCount = 0
        for curIndex, curFP in enumerate(filesList):
            startIndex = curIndex + 1
            if startIndex >= len(filesList):
                break
            
            leaveFiles = filesList[startIndex:]
            sameImgs = []
            curFileName = os.path.basename(curFP)
            curFilePre = curFileName.split('@')[0]
            curRepeatCount = 0 #The number of similar images with different names
            for perFP in leaveFiles:
                isSame = False
                perFileName = os.path.basename(perFP)
                perSplit = perFileName.split('@')
                perFilePre = perSplit[0]
                if perFilePre == curFilePre:
                    isSame = True
                else:
                    isSame = compareObj.compareImageWithPaths(curFP, perFP)
                    if isSame:
                        curRepeatCount += 1
                        #handle related path
                        if len(perSplit) > 1:
                            perSuffix = perSplit[1]
                            fullName = None
                            if '2x' in perSuffix:
                                fullName = perFilePre + '@3x.png'
                            elif '3x' in perSuffix:
                                fullName = perFilePre + '@2x.png'
                            if fullName:
                                relatedPath = os.path.dirname(perFP) + '/' + fullName
                                if os.path.exists(relatedPath):
                                    if relatedPath in filesList:
                                        curRepeatCount += 1
                                        sameImgs.append(relatedPath)
                                        filesList.remove(relatedPath)
                                    if relatedPath in leaveFiles:
                                        leaveFiles.remove(relatedPath)
                            
                if isSame: 
                    if perFP in filesList:
                        sameImgs.append(perFP)
                        filesList.remove(perFP)
                    if perFP in leaveFiles:
                        leaveFiles.remove(perFP)

            if curRepeatCount > 0:
                repeatImagesCount += curRepeatCount
                sameImgs.insert(0, curFP)
                summary = '\n\nFollowing similarity, similar count: ' + str(curRepeatCount)
                print(summary)
                report += summary
                for filep in sameImgs:
                    report += ('\n' + filep)
                    print(filep)
        result = '\n\nCompare completed, total repeat images count: ' + str(repeatImagesCount)
        report += result        
        print(result)
        savePath = os.path.join(self.__mainPath,'kz_image_similarity_log.txt')
        with open(savePath,'w+') as file:
            file.write(report)
        print('Compare log path: ' + savePath)
        

    #scan_files
    def __extractFiles(self):
        filesList = []
        pathsList = []
        #get valid dirs
        paths = []
        if os.path.isdir(self.__mainPath):
            paths = os.listdir(self.__mainPath)
        else:
            print('Main path must be dir!')
        for subPath in paths:
            if subPath[0] != '.' and subPath not in self.__exclusiveRelativePaths:
                pathsList.append(subPath)
        #get valid files
        def addValidFile(perFilePath):
            if perFilePath.endswith('.png'):
                filesList.append(perFilePath)
        for filePath in pathsList:
            subProjectPath = os.path.join(self.__mainPath,filePath)
            if os.path.isdir(subProjectPath):
                for root, sub_dirs, files in os.walk(subProjectPath):
                    for file in files:
                        addValidFile(os.path.join(root,file))
            else:
                addValidFile(subProjectPath)

        return filesList



def main():
     #parser
    parser = argparse.ArgumentParser(description='start args for memory leak detect!')
    parser.add_argument('-m', '--mainPath', type=str, help='project path')
    parserParams = parser.parse_args()
    projectPath = parserParams.mainPath

    if not projectPath:
        projectPath = os.path.pardir
    #custom exclusivePath
    exclusivePaths = ['Pods','Demo','Quick', 'ThirdLib']
    KZDetector(projectPath, exclusivePaths)
  

if __name__ == "__main__":
    main()




