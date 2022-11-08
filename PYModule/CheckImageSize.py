# -*- coding: utf-8 -*-
# by mosn, 检测跨组件的图片调用

import os
import json
from PIL import Image

# 当前目录使用脚本所在路径
currentDir = os.path.pardir

#所有模块
modules = [
    '/../shopzp/ShopZP',
    '/../spbasic',
    '/../spboss'
    '/../spbusiness',
    '/../spchatbase',
    '/../spgeek'
    '/../spbasic',
    '/../splivevideo'
    '/../splogin',
    '/../spoptional',
    '/../spsupport'
    ]

ignoreRes = [
    'FaceDetection',
    'WBFace',
    'Products',
    'ATAuthSDK.framework',
    'DZThirdLib',
    'TencentOpenApi_IOS_Bundle.bundle'
]

totalSize = 0
totalCount = 0
reportDict = {}

def readLocalImageInfo():
    lines = []
    try:
        f = open("build_img_info.txt")
        lines = f.readlines()
        f.close()
    except IOError:
        print("No file Error")
    
    return lines

def writeLocalImageInfo(content):
    try:
        fo = open("build_img_info.txt", "a+")
        fo.write(content+"\n")
        fo.close()
    except IOError:
        print("Error")
      

# 遍历所有文件夹，返回所有图片
def listAllImages(rootdir):
    resultlist = []
    for filename in os.listdir(rootdir):
        if ignoreRes.count(filename)>0:
            continue

        pathname = os.path.join(rootdir, filename)
        if (os.path.isfile(pathname)):
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.webp'):
                resultlist.append(pathname)
        elif(os.path.isdir(pathname)):
            if pathname.endswith('.framework')==False:
                resultlist.extend(listAllImages(pathname))

    return resultlist

def takeSort(elem):
    return elem[0]     


# 根据模块压缩
def countRedundantImages(module):

    if module == '/../shopzp/ShopZP':
        path = currentDir + module + '/Supporting Files/Resource'
    elif module == '/../spbasic':
        path = currentDir + module + '/SPBasic/Bundle'
    else:
        path = currentDir + module

    allImagesList = listAllImages(path)
    
    groupCount = len(allImagesList)
    groupSize = 0

    sortList = []
    for filename in allImagesList:
        img = Image.open(filename)
        w,h= img.size #图片的长和宽
        
        size = os.path.getsize(filename)/1024.0
        groupSize = groupSize+size
        if size>30:
            sortList.append((size,w,h,filename).__str__())


    results = sorted(sortList, key=lambda item: item[0],reverse=True) 
 
    global totalSize
    global totalCount
    global reportDict

    totalSize = totalSize+groupSize
    totalCount = totalCount+groupCount

    reportDict[module+"Size"] = groupSize
    reportDict[module+"Count"] = groupCount

    return results
                
def reportCompare():
    historyList = readLocalImageInfo()
    lastDict = {}
    
    if len(historyList)>0:
        lastContent = historyList[-1]
        if lastContent:
            lastDict = json.loads(lastContent.strip())


    global totalSize
    global totalCount
    global reportDict

    compareCount = totalCount - int(lastDict.get("totalCount",0))
    compareSize = totalSize - float(lastDict.get("totalSize",0))

    report = "当前版本共"+str(totalCount)+"图片  "+"占用空间"+str(totalSize)+"KB \n"
    report = report + "本次比上个版本多"+str(compareCount)+"图片  "+"占用空间大"+str(compareSize)+"KB \n"

    for module in modules:
        compareGroupCount = reportDict[module+"Count"] - float(lastDict.get(module+"Count",0))
        compareGroupSize = reportDict[module+"Size"] - float(lastDict.get(module+"Size",0))
        report = report + module +"组件"+"多"+str(compareGroupCount)+"图片  "+"占用空间大"+str(compareGroupSize)+"KB \n"

    reportDict["totalCount"] = totalCount
    reportDict["totalSize"] = totalSize

    writeLocalImageInfo(json.dumps(reportDict))

    return report
            
# 分别每个模块开始
def func():
    outList = []
    for module in modules:
        result = countRedundantImages(module)
        if len(result)>0:
            print('==============  '+module+' ===============')
#            outList.append('==============  '+module+' ===============')
            for f in result:
                print(f)
#                outList.append(f)
    
    report = reportCompare()
    print(report)
    outList.append(report)
    return outList
        

if __name__ == "__main__":
    func()
