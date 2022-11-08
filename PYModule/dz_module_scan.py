#!/usr/bin/env python3
# -*-coding:utf-8 -*-=

import sys
import os
import re
import json

main_path = os.path.split(os.path.realpath(__file__))[0]

module_map = {
    # "SPBasic" : "../../spbasic/SPBasic/Classes",
    "SPBoss" : "../../spboss/SPBoss/Classes",
    "SPBusiness" : "../../spbusiness/SPBusiness/Classes",
    "SPChatBase" : "../../spchatbase/SPChatBase/Classes",
    # "SPInterfaces" : "../../spinterfaces/SPInterfaces/Classes",
    "SPLiveVideo" : "../../splivevideo/SPLiveVideo/Classes",
    "SPLogin" : "../../splogin/SPLogin/Classes",
    # "SPNetwork" : "../../spnetwork/SPNetwork/Classes",
    "SPSupport" : "../../spsupport/SPSupport/Classes",
    "SPGeek" : "../../spgeek/SPGeek/Classes",
    # "SPThirdLib" : "../../spthirdlib/Products/Headers",
}

def myprint(d):
    print(myprint2(d, 0))


def myprint2(d, deep=0):
    result = ''
    newline = '\n'
    suojin = '    ' * deep
    if isinstance(d, dict):
        start, end = '{', '}'
        result = suojin + start + newline  # 定义当前字典的开头缩进，以及左括号
        for key in d.keys():
            result += myprint2(key, deep + 1) + ' : '  # 打印键，以及冒号
            if isinstance(d[key], (list, dict, tuple)):
                result = result + newline + myprint2(d[key], deep + 1) + ',' + newline  # 如值不是字符串，则换行进行打印这个序列或者字典
            else:
                result = result + repr(d[key]) + ',' + newline  # 若值是字符串，则直接打印字符串，并且加上逗号和换行

        result += suojin + end  # 打印结果的缩进，以及右括号
        return result

    elif isinstance(d, list):
        start, end = '[', ']'
        result = suojin + start + newline  # 定义当前序列的开头缩进，以及左括号
        for value in d:
            result = result + myprint2(value, deep + 1) + ',' + newline  # 直接将内容放入myprint2打印，并且加上新的缩进
        result += suojin + end  # 定义结尾的缩进，以及右括号
        return result
    elif isinstance(d, tuple):
        start, end = '(', ')'
        result = suojin + start + newline
        for value in d:
            result = result + myprint2(value, deep + 1) + ',' + newline
        result += suojin + end
        return result
    else:
        return suojin + repr(d)  # 打印字符串加上引号结果


def find_relation():
    if len(sys.argv) != 2:
        print("请输入要检测的模块")
        return

    target_module_name = sys.argv[1]
    if not target_module_name in module_map:
        print("请输入正确的模块名称")
        return

    target_module_path = os.path.join(main_path, module_map[target_module_name])
    if not os.path.exists(target_module_path):
        print("检测路径异常")
        return

    print("检测中...")

    header_ref_map = {}
    for path, dir_list, file_list in os.walk(target_module_path):
        for header_file in file_list:
            if header_file.find('.DS_Store') != -1 or header_file.find('.gitkeep') != -1:
                continue

            if header_file.find('.h') == -1 and header_file.find('.m') == -1:
                continue
            
            header_name = header_file.split(".")[0]
            if not header_name in header_ref_map:
                header_ref_map[header_name] = []
            file_object = open(os.path.join(path, header_file))
            try:
                for line in file_object.readlines():
                    if len(line) > 0 and line.startswith("#import"):
                        improt_headers = re.findall('["<](.*)[>"]', line)
                        if len(improt_headers):
                            import_header = improt_headers[0]
                            if "/" in import_header:
                                import_header = import_header.split("/")[1]
                            import_header_name = import_header.split(".")[0]
                            if import_header_name != header_name:
                                header_ref_map[header_name].append(import_header)
            finally:
                file_object.close()

    header_ref_result_map = {}
    for header_file, header_refs in header_ref_map.items():
        header_ref_result_map[header_file] = []
        for header_ref in header_refs:
            for module_name, module_path in module_map.items():
                if module_name != target_module_name:
                    for path, dir_list, file_list in os.walk(os.path.join(main_path, module_path)):
                        for file in file_list:
                            if file.find('.DS_Store') != -1 or file.find('.gitkeep') != -1:
                                continue

                            if file.find('.h') == -1:
                                continue
                            if file == header_ref:
                                header_ref_result_map[header_file].append("%s-->%s" % (module_name, file))
    # 过滤空数组
    finish_result_map = {}
    for key, values in header_ref_result_map.items():
        if len(values) > 0:
            finish_result_map[key] = values;
    
    myprint(finish_result_map)
    
    # 直接打印json字符串
    #print(json.dumps(finish_result_map))
                           

if __name__ == '__main__':
    find_relation()
