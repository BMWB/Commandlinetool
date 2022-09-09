import Foundation
import CommandLineToolCore
import SwiftIpaTool

//let tool = CommandLineReleases()
//
//do {
//    try tool.run()
//} catch {
//    print("Whoops! An error occurred: \(error)")
//}

do{
    let ipaTool = try IpaTool(projectPath: "/Users/admin/Desktop/DZ/managerzp",
                          configuration: .release,
                          exportOptionsPlist: "/Users/admin/Desktop/DZ/managerzp/ExportOptions.plist",
                              pgyerKey: "51895949ad44dcc3934f47c17aa0c0e5",
                              schemeKey:"ManagerZP-QA")
    
    /*
    var output = ipaTool.podInstall()
    print(output.readData)
    exit(-1)
    print(ipaTool)
    print("执行clean")
    */
    var output = ipaTool.clean()
    if output.readData.count > 0 {
        print("执行失败clean error = \(output.readData)")
        exit(-1)
    }
    print("执行archive")
    output = ipaTool.archive()
    if !FileManager.default.fileExists(atPath: ipaTool.xcarchive) {
        print("执行失败archive error = \(output.readData)")
        exit(-1)
    }
    print("执行exportArchive")
    output = ipaTool.exportArchive()
    
    if !FileManager.default.fileExists(atPath: ipaTool.exportIpaPath.appPath("\(ipaTool.scheme).ipa")) {
        print("执行失败exportArchive error =\(output.readData)")
        exit(-1)
    }
    print("导出ipa成功\(ipaTool.exportIpaPath)")
    print("开始上传蒲公英")
//    ipaTool.update()
}catch{
    print(error)
}
