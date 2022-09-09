#!/usr/bin/env python3
#_*_ coding: utf-8 _*_#

import subprocess
import sys, os
import shutil
import json
import argparse

def __getSelectModule(modules, tips):
    #get select modules
    selectModules = []
    while (True):
        select = input(tips)
        selectNums = select.split(',')
        for sel in selectNums:
            selTrip = sel.strip()
            if selTrip.isdigit():
                smn = int(selTrip)
                if smn == 0:
                    selectModules = []
                    selectModules.extend(modules[1:len(modules)])
                    break
                if int(smn) < len(modules):
                    selectModules.append(modules[smn])
        if len(selectModules) > 0:
            break
        else:
            continue
    return selectModules


def __configPreCommitHookConfig(staticLibPath, modules):
    projectPath = os.path.dirname(os.path.dirname(staticLibPath))
    preHookExecutePath =  os.path.join(staticLibPath, 'bin/boss-pre-commit')
    if not os.path.exists(preHookExecutePath):
        print('Config failed, unable to find executable file of pre-commit!')
        return
    selectModules = __getSelectModule(modules, "(1) 请输入要安装的模块序号 (多选请用英文逗号隔开)：")
    #move hook
    topDirPath = os.path.dirname(projectPath)
    if not os.path.exists(topDirPath):
        print('Config failed, top path does not exist!')
        return
    for sm in selectModules:
        name = sm["name"]
        hookPath = os.path.join(topDirPath, name, '.git/hooks')
        if os.path.exists(hookPath):
            dst = os.path.join(hookPath, 'pre-commit')
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy(preHookExecutePath, dst)
        else:
            print('WARNING: ' + name + ' does not exist!')



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
    #custom
    validModules = []
    validModules.extend(modules[1:len(modules)])
    firstQuery = True
    while (True):
        inputTips = "(2) 是否需要定制模块检查人 (y/n)："
        if not firstQuery:
           inputTips =  "    是否还需定制模块检查人 (y/n)："
        inputRes = input(inputTips)
        firstQuery = False
        if inputRes == 'y':
            selectModules = __getSelectModule(modules, "(a) 请输入定制ARC的模块序号 (多选请用英文逗号隔开)：")
            #reviewers
            defaultRes = ''
            while (True):
                inputRes = input("(b) 请输入定制代码检查人 (多人请用英文逗号隔开)：")
                if len(inputRes) > 0:
                    defaultRes = inputRes
                    break
                else:
                    continue
            for sm in selectModules:
                sm['defaultReviewers'] = defaultRes
            continue
        elif inputRes == 'n':
            break 
        else:
            continue

    ''' move '''
    projectPath = os.path.dirname(os.path.dirname(staticLibPath))
    preHookExecutePath =  os.path.join(staticLibPath, 'bin/boss-post-commit')
    if not os.path.exists(preHookExecutePath):
        print('Config failed, unable to find executable file of boss-post-commit!')
        return
    #move hook
    topDirPath = os.path.dirname(projectPath)
    if not os.path.exists(topDirPath):
        print('Config failed, top path does not exist!')
        return
    for sm in validModules:
        moduleDir = os.path.join(topDirPath, sm['name'])
        #config
        configDir = os.path.join(moduleDir, '.git', 'kz_auto_arc')
        if not os.path.exists(configDir):
            os.makedirs(configDir)
        configPath = os.path.join(configDir, 'autoArcConfig.json')
        dfs = defaultSub
        if 'defaultSubscriber' in sm:
            configdf = sm['defaultSubscriber']
            if len(configdf) > 0:
                dfs = configdf
        configObj = {'defaultReviewers' : sm['defaultReviewers'], 'defaultSubscriber' : dfs}
        with open(configPath, 'w+') as file:
            json.dump(configObj, file)

        #hook 
        hookPath = os.path.join(topDirPath, sm["name"], '.git/hooks')
        if os.path.exists(hookPath):
            dst = os.path.join(hookPath, 'post-commit')
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy(preHookExecutePath, dst)
        else:
            print('WARNING: ' + sm["name"] + ' does not exist!')


def printModuleInfos(modules):
    maxNameLength = 0
    for m in modules:
        if len(m['name']) > maxNameLength:
            maxNameLength = len(m['name'])
    print('{0:2}  {1:{2}}  {3:20}'.format('序号', '模块名', maxNameLength, '默认代码检查人'))
    maxNameLength += 4
    for index, m in enumerate(modules):
        print('{0:2d}    {1:{2}} {3:30}'.format(index, m['name'], maxNameLength, m['defaultReviewers']))



def queryModuelsConfig(staticLibPath, modules):
    projectPath = os.path.dirname(os.path.dirname(staticLibPath))
    topDirPath = os.path.dirname(projectPath)
    for sm in modules:
        moduleDir = os.path.join(topDirPath, sm['name'])
        #config
        configDir = os.path.join(moduleDir, '.git', 'kz_auto_arc')
        configPath = os.path.join(configDir, 'autoArcConfig.json')
        if not os.path.exists(configPath):
            mname = sm["name"]
            if mname != 'all':
                print('WARNING: ' + sm["name"] + ' does not install auto arc!')
            continue
        configObj = None
        try:
            with open(configPath, 'r') as file:
                configObj = json.load(file)
        except Exception as e:
            print('[Auto ARC] open arc config json failed: %s' % e)
        if 'defaultReviewers' in configObj:
            sm['defaultReviewers'] = configObj['defaultReviewers']
        else:
            sm['defaultReviewers'] = ''


def main():
    parser = argparse.ArgumentParser(description='Boss code quality install config!', add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='config help')
    parser.add_argument('-q', '--query', action='store_true', help='query custom config')
    parserParams = parser.parse_args()
    helps = parserParams.help
    query = parserParams.query
    if helps:
        print('\nUsage:\n ./BossZPConfig.py <command>\n\nCommands:')
        print('{0:20}{1:}'.format('-h, --help', '查看配置帮助信息'))
        print('{0:20}{1:}'.format('-q, --query', '查看已经进行配置的本地arc信息'))
        return
    if not query:
        print('===================== 开始代码质量控制配置 =====================')

    #e.g:/Users/twl/bossproject/.PythonLib/KZStaticAnalyzer
    installDirPath = os.path.dirname(os.path.abspath(__file__))
    staticLibPath = os.path.dirname(installDirPath)
    configPath = os.path.join(installDirPath, 'BossInstallConfig.json')
    configObj = None
    try:
        with open(configPath, 'r') as file:
            configObj = json.load(file)
    except Exception as e:
        print('Boss config file is invalid: %s' % e)
    if not configObj:
        return
    
    #current modules
    modules = configObj
    allM = {"name" : "all", "defaultReviewers" : ""}
    modules.insert(0, allM)
    if query:
        queryModuelsConfig(staticLibPath, modules)
        printModuleInfos(modules)
        return
    print('模块选择列表：\n')
    printModuleInfos(modules)

    print('\n------------ 开始静态检查和格式化等pre commit配置 ------------')
    __configPreCommitHookConfig(staticLibPath, modules)

    print('\n\n------------ 开始自动ARC等post commit配置 ------------------')
    __configPostCommitHookConfig(staticLibPath, modules)

    print('\n配置结果：\n')
    printModuleInfos(modules)
    print('\n===================== 🎉🎉 配置完成 =====================')

if __name__ == '__main__':
    main()
