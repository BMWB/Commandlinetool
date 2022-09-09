#!/usr/bin/env python3
#_*_ coding: utf-8 _*_#

import subprocess
import sys, os
import shutil
import argparse
import json

def __configPreCommitHookConfig(staticLibPath, needTargetCheck):
    projectPath = os.path.dirname(staticLibPath)
    if not os.path.exists(projectPath):
        print('Project path does not exist!')
        return
    
    hookName = 'normal-pre-commit'
    if needTargetCheck:
        hookName = 'target-normal-pre-commit'
    preHookExecutePath =  os.path.join(staticLibPath, ('bin/'+hookName))
    if not os.path.exists(preHookExecutePath):
        print('Unable to find executable file of pre-commit!')
        return


    hookPath = os.path.join(projectPath, '.git/hooks')
    if os.path.exists(hookPath):
        dst = os.path.join(hookPath, 'pre-commit')
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy(preHookExecutePath, dst)
    else:
        print('WARNING: %s does not exist!' % hookPath)


def __configPostCommitHookConfig(staticLibPath, modules):
    #subscriber
    defaultSub = ''
    while (True):
        inputRes = input("(1) 请输入默认订阅人 (多人请用英文逗号隔开)：")
        if len(inputRes) > 0:
            defaultSub = inputRes
            break
        else:
            continue
    #reviewers
    defaultViewer = ''
    while (True):
        inputRes = input("(2) 请输入默认检查人 (多人请用英文逗号隔开)：")
        if len(inputRes) > 0:
            defaultViewer = inputRes
            break
        else:
            continue

    ''' move '''
    projectPath = os.path.dirname(staticLibPath)           
    preHookExecutePath =  os.path.join(staticLibPath, 'bin/normal-post-commit')
    if not os.path.exists(preHookExecutePath):
        print('Config failed, unable to find executable file of normal-post-commit!')
        return
    #config
    configDir = os.path.join(projectPath, '.git', 'kz_auto_arc')
    if not os.path.exists(configDir):
        os.makedirs(configDir)
    configPath = os.path.join(configDir, 'autoArcConfig.json')
    configObj = {'defaultReviewers' : defaultViewer, 'defaultSubscriber' : defaultSub}
    with open(configPath, 'w+') as file:
        json.dump(configObj, file)

    #hook 
    hookPath = os.path.join(projectPath, '.git/hooks')
    if os.path.exists(hookPath):
        dst = os.path.join(hookPath, 'post-commit')
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy(preHookExecutePath, dst)
    else:
        print('WARNING: ' + hookPath + ' does not exist!')


def main():
    parser = argparse.ArgumentParser(description='Code quality control lib!')
    parser.add_argument('-t', '--targetCheck', action='store_true', help='need target check')
    parserParams = parser.parse_args()
    needTargetCheck = parserParams.targetCheck

    #e.g:/Users/xx/xx/bosshi/KZStaticAnalyzer
    print('===================== 开始代码质量控制配置 =====================')
    staticLibPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # print('🎉🎉 Config success!')
    print('\n------------ 开始静态检查和格式化等pre commit配置 ------------')
    __configPreCommitHookConfig(staticLibPath, needTargetCheck)
    print('Finish pre commit install.')

    print('\n\n------------ 开始自动ARC等post commit配置 ------------------')
    __configPostCommitHookConfig(staticLibPath, needTargetCheck)

    print('\n===================== 🎉🎉 配置完成 =====================')

if __name__ == '__main__':
    main()
