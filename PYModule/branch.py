# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import sys
import urllib.parse

moduleMap = {
    'geek' : 'spgeek',
    'boss' : 'spboss',
    'chatbase' : 'spchatbase',
    'login' : 'splogin',
    'basic' : 'spbasic',
    'network' : 'spnetwork',
    'third' : 'spthirdlib',
    'optional' : 'spoptional',
    'main' : 'shopzp',
    'business' : 'spbusiness',
    'interfaces' : 'spinterfaces',
    'livevideo' : 'splivevideo',
    'support' : 'spsupport'
}
moduleIdMap = {
    'geek' : '2804',
    'boss' : '2803',
    'chatbase' : '2808',
    'login' : '2807',
    'basic' : '2805',
    'network' : '2806',
    'third' : '2802',
    'optional' : '2809',
    'main' : '2795',
    'business' : '2810',
    'interfaces' : '2811',
    'livevideo' : '2813',
    'support' : '2812'
}

if __name__ == "__main__":
    params = sys.argv
    if len(params) == 3:
        token = params[1]
        branch = urllib.parse.quote_plus(params[2])
        print(branch)

        type = input("输入选择的方法（1、打开分支 2、锁定分支  3、打开git页面）==>>")

        while 1:
            group = input("\n输入组件名称：")
            if group == 'q':
                type = input("输入选择的方法（1、打开分支 2、锁定分支  3、打开git页面）==>>")
                group = input("\n输入组件名称：")

            if moduleMap.get(group, False) == False and group != 'all':
                print('Group Name Error')
                continue

            if type == '1':
                if group == 'all':
                    for git_id in moduleIdMap.values():
                        cmd = 'curl --request DELETE --header "PRIVATE-TOKEN: ' + token + '" "https://git.kanzhun-inc.com/api/v4/projects/' + git_id + '/protected_branches/' + branch + '"'
                        os.system(cmd)
                    print('已打开')
                else:
                    git_id = moduleIdMap[group]
                    cmd = 'curl --request DELETE --header "PRIVATE-TOKEN: ' + token + '" "https://git.kanzhun-inc.com/api/v4/projects/' + git_id + '/protected_branches/' + branch + '"'
                    print(cmd)
                    os.system(cmd)
                    print('已打开')
            elif type == '2':
                if group == 'all':
                    for git_id in moduleIdMap.values():
                        cmd = 'curl --request POST --header "PRIVATE-TOKEN: ' + token + '" "https://git.kanzhun-inc.com/api/v4/projects/' + git_id + '/protected_branches?name=' + branch + '&push_access_level=0&merge_access_level=0"'
                        os.system(cmd)
                else:
                    git_id = moduleIdMap[group]
                    cmd = 'curl --request POST --header "PRIVATE-TOKEN: ' + token + '" "https://git.kanzhun-inc.com/api/v4/projects/' + git_id + '/protected_branches?name=' + branch + '&push_access_level=0&merge_access_level=0"'
                    os.system(cmd)
            elif type == '3':
                cmd = "open -a '/applications/Google Chrome.app' "+"https://git.kanzhun-inc.com/bosszhipinspec/" + moduleMap[group] + "/-/settings/repository"
                os.system(cmd)
            else:
                print('Error Ops Type')
    else:
        print('Need Git Private Token And Branc')
    
