#!/usr/bin/env python3

import sys
import os
import json
import tinify
from enum import Enum

class TinifyResult(Enum):
    TinifyResultError = 1
    TinifyResultToken = 2
    TinifyResultSkip = 3
    TinifyResultRetry = 4
    TinifyResultSuccess = 5

class CompressResult(Enum):
    CompressResultEnd = 1           # 压缩出现错误，需要结束
    CompressResultSkip = 2          # 遇到未知错误，不做记录等到下次再压缩
    CompressResultSuccess = 5       # 压缩成功

main_path = os.path.split(os.path.realpath(__file__))[0]
compressed_images_path = os.path.join(main_path, "compressed_images.json")
tinify_tokens_index = 0

default_image_paths = [
    '../ShopZP/Supporting Files/Assets.xcassets',

    '../../spbasic/SPBasic/Assets',
    '../../spbasic/SPBasic/Images.xcassets',

    '../../spboss/SPBoss/Assets',
    '../../spboss/SPBoss/Images.xcassets',

    '../../spbusiness/SPBusiness/Assets',
    '../../spbusiness/SPBusiness/Images.xcassets',

    '../../spchatbase/SPChatBase/Assets',
    '../../spchatbase/SPChatBase/Images.xcassets',

    '../../spgeek/SPGeek/Assets',
    '../../spgeek/SPGeek/Images.xcassets',

    '../../splivevideo/SPLiveVideo/Assets',
    '../../splivevideo/SPLiveVideo/Images.xcassets',

    '../../splogin/SPLogin/Assets',
    '../../splogin/SPLogin/Images.xcassets',

    '../../spsupport/SPSupport/Assets',
    '../../spsupport/SPSupport/Images.xcassets',
]

tinify_tokens = [
    'cBP52x9C4mgTDs7pFD7SSk1qYJ5zYWZd',
    'F7CgdhD1cPx40syFD0TL1jBW4T9tTFpP',
    'fsk8vyt6T13DdJsFr29G5vzD3p3Mzd1g',
    'hTphpzgpVj2kwGXkLJGPGHVVnl4RPFjL', 
    'fn26bztKVVRCDV5k2kzk6pMfrRDyZPbP',
    '2ys6fLj002gJZ9fkfs84w1m5CJwVfHz0',
    's2PvmYQbrFTYBPp1xXHc58Wvnkj8hqxB',
    '1cbkPmd0tLP4K7xsyz9Q6HX0cxzlq53q',
    'vp8k2jLzxm1zDL7SVFqhGR353nkzhYMN',
    'rXxmVTCJMZRLtL24cT4Zt4SB09z1cjH8',
    'qjr3Wq1mvxf7N89bZ2L6wyHTRRrcVJGk',
    'd0sDnMRrLdmpfS7vGjwrs4nhYGhYvXjM'
]

def compress_image_with_paths(file_paths):
    tinify_token = tinify_tokens[tinify_tokens_index]
    print("Start use token '%s'" % tinify_token)
    tinify.key = tinify_token

    compressed_images_info = {}
    if os.path.exists(compressed_images_path):
        with open(compressed_images_path, 'r') as file:
            compressed_images_info = json.load(file)

    for file_path in file_paths:
        real_file_path = file_path
        if not os.path.isabs(file_path):
            real_file_path = os.path.join(main_path, file_path)

        occur_error = False
        for image_path in traverse_image_path(real_file_path):
            relatively_image_path = os.path.relpath(image_path, main_path)
            compress_info = { "compress_count" : 0 }
            if relatively_image_path in compressed_images_info:
                compress_info = compressed_images_info[relatively_image_path]
            else:
                compressed_images_info[relatively_image_path] = compress_info
            compress_count = compress_info["compress_count"]

            if compress_count < 2:  # 每张图片压缩三次
                compress_result = compress_image(image_path)
                if compress_result == CompressResult.CompressResultSuccess:
                    compress_info["compress_count"] += 1
                elif compress_result == CompressResult.CompressResultEnd:
                    occur_error = True
                    break
        if occur_error:
            break

    with open(compressed_images_path, 'w') as file:
        json.dump(compressed_images_info, file)

def compress_image(image_path):
    error_occur_count = 0
    tinify_result = tinify_image(image_path)
    if tinify_result == TinifyResult.TinifyResultSuccess:
        return CompressResult.CompressResultSuccess
    elif tinify_result == TinifyResult.TinifyResultToken:
        global tinify_tokens_index
        tinify_tokens_index += 1
        if tinify_tokens_index >= len(tinify_tokens):
            print("\033[1;31m[Error]\033[0m No tinify token available")
            return CompressResult.CompressResultEnd
        tinify_token = tinify_tokens[tinify_tokens_index]
        print("Start use token '%s'" % tinify_token)
        tinify.key = tinify_token
        return compress_image(image_path)
    elif tinify_result == TinifyResult.TinifyResultRetry:
        error_occur_count += 1
        if error_occur_count >= 5:
            print("\033[1;31m[Error]\033[0m Too many retries, please make sure the environment and try again")
            return CompressResult.CompressResultEnd
        return compress_image(image_path)
    elif tinify_result == TinifyResult.TinifyResultSkip:
        return CompressResult.CompressResultSkip
    elif tinify_result == TinifyResult.TinifyResultError:
        return CompressResult.CompressResultEnd

def tinify_image(image_path):
    try:
        source = tinify.from_file(image_path)
        source.to_file(image_path)
        print("\033[1;32m[Success]\033[0m Compress image at '%s'" % image_path)
        return TinifyResult.TinifyResultSuccess
    except tinify.AccountError as e:
        # Verify your API key and account limit.
        print("\033[1;31m[Error]\033[0m Compress image at '%s' whit error: '%s' " % (image_path, e.message))
        return TinifyResult.TinifyResultToken
    except tinify.ClientError as e:
        # Check your source image and request options.
        print("\033[1;33m[Warning]\033[0m Compress image at '%s' whit error: '%s' " % (image_path, e.message))
        return TinifyResult.TinifyResultSkip
    except tinify.ServerError as e:
        # Temporary issue with the Tinify API.
        print("\033[1;31m[Error]\033[0m Compress image at '%s' whit error: '%s' " % (image_path, e.message))
        return TinifyResult.TinifyResultRetry
    except tinify.ConnectionError as e:
        # A network connection error occurred.
        print("\033[1;31m[Error]\033[0m Compress image at '%s' whit error: '%s' " % (image_path, e.message))
        return TinifyResult.TinifyResultRetry
    except Exception as e:
        # Something else went wrong, unrelated to the Tinify API.
        print("\033[1;31m[Error]\033[0m Compress image at '%s' whit error: '%s' " % (image_path, e.message))
        return TinifyResult.TinifyResultError

def traverse_image_path(file_path):
    if not os.path.exists(file_path):
        return
        
    if os.path.isdir(file_path):
        for path, dir_list, file_list in os.walk(file_path):
            for file_name in file_list:
                if file_name.endswith('.png') or file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
                    yield(os.path.join(path, file_name))
    else:
        if file_path.endswith('.png') or file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            yield(file_path)

def handle_compress_relust():
    compressed_images = []
    compressed_images_new = {}
    if os.path.exists(compressed_images_path):
        with open(compressed_images_path, 'r') as file:
            compressed_images = json.load(file)
    
    for path in compressed_images:
        compressed_images_new[path] = { "compress_count" : 2 }

    with open(compressed_images_path, 'w') as file:
        json.dump(compressed_images_new, file)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        compress_image_with_paths([target_path])
    else:
        compress_image_with_paths(default_image_paths)
