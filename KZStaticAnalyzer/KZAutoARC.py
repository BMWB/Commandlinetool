#!/usr/bin/env python3
#_*_ coding: utf-8 _*_#

import argparse
import re
import subprocess
import sys, os
import json

NO_ACR_TOKEN = '--no-arc'
CUSTOM_TOKEN = '-r'

class AutoARCHandler():
    @classmethod
    def handleInputHookPath(cls, hookPath):
        gitDir = os.path.dirname(os.path.dirname(hookPath))
        projectDir = os.path.dirname(gitDir)
        mesPath = os.path.join(gitDir, 'COMMIT_EDITMSG')
        if not os.path.exists(mesPath):
            return 
        
        message = None
        with open(mesPath, 'r') as file:
            message = file.read()

        if NO_ACR_TOKEN in message:
            print('[Auto ARC] ARC has been disabled for current commit!') 
            return

        message = message.rstrip('\n')
        AutoARCHandler.__createArcTemplate(message, projectDir)
        


    @classmethod
    def __createArcTemplate(cls, message, projectDir):
        #set config
        configDir = os.path.join(projectDir, '.git', 'kz_auto_arc')
        if not os.path.exists(configDir):
            print('[Auto ARC] Auto ARC config dir not exisit, please reinstall!')
            return
        customMsg = message
        arcReviewers = ''
        if CUSTOM_TOKEN in message:
            sps = message.split(CUSTOM_TOKEN, 1)
            customMsg = sps[0]
            arcParams = sps[1].replace(' ', '')
            arcReviewers = arcParams
        arcSubers = ''
        configPath = os.path.join(configDir, 'autoArcConfig.json')
        if os.path.exists(configPath):
            configObj = None
            with open(configPath, 'r') as file:
                try:
                    configObj = json.load(file)
                except Exception as e:
                    print('[Auto ARC] open arc config json failed: %s' % e) 
            
            if not configObj:
                return
            if len(arcReviewers) < 1:
                arcReviewers = configObj['defaultReviewers']
            arcSubers = configObj['defaultSubscriber']
            

        if len(arcReviewers) < 1:
            print('[Auto ARC] Create arc diff failed:\nMissing reviewer param!')
            return
        if len(arcSubers) < 1:
            print('[Auto ARC] Create arc diff failed:\nMissing subscriber param!')
            return

        templateContent = ''
        #customMsg
        mes = customMsg + '\n'
        templateContent += mes
        #summary
        summary = 'Summary: ' + customMsg + '\n'
        templateContent += summary
        #test plan
        testplan = 'Test Plan: ' + customMsg + '\n'
        templateContent += testplan
        #reviewers
        reviewers = 'Reviewers: ' + arcReviewers + '\n'
        templateContent += reviewers
        #subscribers
        subscribers = 'Subscribers: ' + arcSubers + '\n'
        templateContent += subscribers
        #JIRA Issues
        jiraIssues = 'JIRA Issues: ' + ''
        templateContent += jiraIssues

        contentFp = os.path.join(configDir, 'autoArcInput')
        with open(contentFp, 'w+') as file:
            file.write(templateContent)

        arcCmd = 'arc diff --create -F %s' % contentFp

        (re, out) = subprocess.getstatusoutput(arcCmd)
        if re != 0:
            print('[Auto ARC] Create arc diff failed:\n%s' % out)
        else:
            token = 'Revision URI: '
            if token in out:
                spe = out.split(token)[1]
                arcUrl = spe.split('\n')[0]
                print('[Auto ARC] Revision URI: %s' % arcUrl)




def main():
    parser = argparse.ArgumentParser(description='Auto ARC script.')
    parser.add_argument('-p', '--hookPath', type=str, help='hook file path.')
    args = parser.parse_args()
    hookPath = args.hookPath
    AutoARCHandler.handleInputHookPath(hookPath)
    


if __name__ == '__main__':
    main()
