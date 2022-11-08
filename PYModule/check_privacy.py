#!/usr/bin/python
# -*-coding:utf-8 -*-=
import os
import commands
import sys
import mmap
import threading
import time
            
# public
publicInfos = ['authorizationStatus', 'requestAuthorization:']
# app tracking
appTrackingInfos = ['ATTrackingManager', 
                    'isAdvertisingTrackingEnabled',
                    'requestTrackingAuthorizationWithCompletionHandler:', 
                    'trackingAuthorizationStatus', 
                    'ASIdentifierManager', 
                    'advertisingIdentifier', 
                    '/System/Library/Frameworks/AdSupport.framework', 
                    '/System/Library/Frameworks/AppTrackingTransparency.framework']
# photo library
photoLibraryInfos = ['PHPhotoLibrary', 
                     'requestAuthorizationForAccessLevel:handler:', 
                     'requestAuthorization:', 
                     'authorizationStatusForAccessLevel:', 
                     'presentLimitedLibraryPickerFromViewController:', 
                     'fetchAssetCollectionsWithType:subtype:options:', 
                     'PHImageManager', 
                     'requestImageForAsset:targetSize:contentMode:options:resultHandler:', 
                     'requestImageDataForAsset:options:resultHandler:', 
                     'requestAVAssetForVideo:options:resultHandler:', 
                     'requestExportSessionForVideo:options:exportPreset:esultHandler:', 
                     'requestLivePhotoForAsset:targetSize:contentMode:options:resultHandler:'
                     'requestPlayerItemForVideo:options:resultHandler:', 
                     'requestImageDataAndOrientationForAsset:options:resultHandler:'
                     '/System/Library/Frameworks/Photos.framework']
# media
mediaInfos = ['AVCaptureDevice', 
               'requestAccessForMediaType:completionHandler:', 
               'authorizationStatusForMediaType:', 
               'UIImagePickerController', 
               'UIImagePickerControllerDelegate', 
               'imagePickerController:didFinishPickingMediaWithInfo:', 
               'MPMediaLibrary', 
               '/System/Library/Frameworks/AVFoundation.framework']
# camera
cameraInfos = ['AVMediaTypeVideo', 
               'AVCaptureSession',
               'AVCaptureDeviceInput', 
               'AVCaptureStillImageOutput', 
               'AVCaptureMovieFileOutput', 
               'AVCaptureVideoPreviewLayer', 
               'captureStillImageAsynchronouslyFromConnection:completionHandler:', 
               'startRecordingToOutputFileURL:recordingDelegate:']
# microphone
microphoneInfos = ['AVMediaTypeAudio', 
                   'AVAudioRecorder', 
                   'AVAudioRecorderDelegate',
                   'audioRecorderDidFinishRecording:successfully:', 
                   'audioRecorderBeginInterruption:', 
                   'audioRecorderEndInterruption:withOptions:', 
                   'audioRecorderEndInterruption:withFlags:', 
                   'audioRecorderEndInterruption:']
# location
locationInfos = ['CLLocationManager', 
                 'CLLocationManagerDelegate', 
                 'requestWhenInUseAuthorization', 
                 'requestAlwaysAuthorization', 
                 'locationServicesEnabled', 
                 'startUpdatingLocation',
                 'stopUpdatingLocation',
                 'startUpdatingHeading',
                 'requestTemporaryFullAccuracyAuthorizationWithPurposeKey:completion:', 
                 'locationManager:didChangeAuthorizationStatus:', 
                 'locationManager:DidChangeAuthorization:',
                 'locationManager:didUpdateHeading:', 
                 '/System/Library/Frameworks/CoreLocation.framework']
# contacts
contactsInfos = ['CNContactStore', 
                 'requestAccessForEntityType:completionHandler:', 
                 'authorizationStatusForEntityType:', 
                 'CNContactFetchRequest', 
                 'enumerateContactsWithFetchRequest:error:usingBlock:', 
                 '/System/Library/Frameworks/Contacts.framework']
# network
networkInfos = ['_getifaddrs', 
                '_inet_ntoa', 
                'CFNetworkCopySystemProxySettings',
                'CFNetworkCopyProxiesForURL',
                'CNCopyCurrentNetworkInfo', 
                'CNCopySupportedInterfaces',
                'CTTelephonyNetworkInfo',
                'subscriberCellularProvider',
                'isoCountryCode',
                'mobileCountryCode',
                'mobileNetworkCode', 
                '/System/Library/Frameworks/CFNetwork.framework', 
                '/System/Library/PrivateFrameworks/Network.framework']

# check map
checkTypeMap = {
    'appTrackingInfos': appTrackingInfos,
    'photoLibraryInfos': photoLibraryInfos,
    'mediaInfos': mediaInfos,
    'publicInfos': publicInfos,
    'cameraInfos' : cameraInfos,
    'microphoneInfos': microphoneInfos,
    'locationInfos': locationInfos,
    'contactsInfos': contactsInfos,
    'networkInfos': networkInfos
}

# check map describe
checkTypeMapDescribe = {
    'appTrackingInfos': 'idfa隐私信息',
    'photoLibraryInfos': '相册隐私信息',
    'mediaInfos': '多媒体隐私信息(相册、相机、麦克风)',
    'publicInfos': '公共隐私信息(跟隐私相关但无法确认具体类型)',
    'cameraInfos' : '相机隐私信息',
    'microphoneInfos': '麦克风隐私信息',
    'locationInfos': '定位隐私信息',
    'contactsInfos': '通讯录隐私信息',
    'networkInfos': '网络隐私信息'
}

checkedLibs = []

class printWaitThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.threadState = 0
    def run(self): 
        self.threadState = 1                 
        self.printWait()
    def stop(self):
        self.threadState = 0
    def printWait(self):
        animation = "|/-\\"
        idx = 0
        while self.threadState == 1:
            sys.stdout.write('\r' + animation[idx % len(animation)] + ' ')
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ')
        sys.stdout.flush()

# exclude libs
excludeLibs = ['BossThirdPart', 'BossOptionalPart', 'libopencore-amrnb.a', 'libmp3lame.a']

mainPath = os.path.split(os.path.realpath(__file__))[0]

def check(libraryPath, fileName):
    stringsPath = os.path.join(mainPath, ('.%s' % fileName))
    cmd = 'strings - -a -arch arm64 %s > %s' % (libraryPath, stringsPath)
    thread = printWaitThread()
    # thread.start()
    os.system(cmd)
    # thread.stop()

    foundMap = {}
    for checkType, infos in checkTypeMap.items():
        foundInfos = []
        for info in infos:
            with open(stringsPath, 'rb', 0) as file:
                mmapFile = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                if mmapFile.find(info) != -1:
                    foundInfos.append(info)
        if len(foundInfos) > 0:
            foundMap[checkType] = foundInfos

    if len(foundMap) > 0:
        print('\n################### 在%s中扫描到隐私信息\n' % (fileName))
        print('******************* 资源路径:')
        print(libraryPath + '\n')
        for checkType, foundInfos in foundMap.items():
            print('=================== %s' % (checkTypeMapDescribe[checkType]))
            print(str(foundInfos) + '\n')
        print('################### 扫描结束\n\n\n')
    os.remove(stringsPath)
        
def main():
    params = sys.argv
    if len(params) == 1:
        params = ['', './']
        idx = 0

    for path, dir_list, file_list in os.walk(params[1]):
        for file_name in file_list:
            if file_name.find('.DS_Store') != -1 or file_name.find('.arcconfig') != -1:
                continue
            if file_name in excludeLibs or file_name in checkedLibs:
                continue
            if file_name.startswith('BZ') or file_name.startswith('zp') or file_name.startswith('ZP'):
                continue
            if file_name.endswith('.h') or file_name.endswith('.xml') or file_name.endswith('.nib'):
                continue
            if path.find('.framework') == -1 and file_name.find('.a') == -1:
                continue
            
            full_path = os.path.join(path, file_name)
            (status, output) = commands.getstatusoutput('file %s' % full_path)
            index = output.find('Mach-O universal binary')
            if index != -1:
                check(full_path, file_name)
                checkedLibs.append(file_name)

if __name__ == "__main__":
    main()
