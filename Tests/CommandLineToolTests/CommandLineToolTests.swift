import XCTest
import class Foundation.Bundle
import Files
import CommandLineToolCore

final class CommandLineToolTests: XCTestCase {
    func testExample() throws {
//        // This is an example of a functional test case.
//        // Use XCTAssert and related functions to verify your tests produce the correct
//        // results.
//
//        // Some of the APIs that we use below are available in macOS 10.13 and above.
//        guard #available(macOS 10.13, *) else {
//            return
//        }
//
//        // Mac Catalyst won't have `Process`, but it is supported for executables.
//        #if !targetEnvironment(macCatalyst)
//
//        let fooBinary = productsDirectory.appendingPathComponent("CommandLineTool")
//
//        let process = Process()
//        process.executableURL = fooBinary
//
//        let pipe = Pipe()
//        process.standardOutput = pipe
//
//        try process.run()
//        process.waitUntilExit()
//
//        let data = pipe.fileHandleForReading.readDataToEndOfFile()
//        let output = String(data: data, encoding: .utf8)
//
//        XCTAssertEqual(output, "Hello, world!\n")
//        #endif
        
        let tempFolder = Folder.temporary
        
        let testFolder = try tempFolder.createSubfolderIfNeeded(withName: "CommandLineToolTests")
        
        try testFolder.empty()
        
        let fileManager = FileManager.default
        
        fileManager.changeCurrentDirectoryPath(testFolder.path)
        
        let  arguments = [testFolder.path,"hello.swift"]
        let tool = CommandLineTool(arguments:arguments)
        
        try tool.run()
        
        XCTAssertNotNil(try? testFolder.file(named: "Hello.swift"))
    }

    /// Returns path to the built products directory.
    var productsDirectory: URL {
      #if os(macOS)
        for bundle in Bundle.allBundles where bundle.bundlePath.hasSuffix(".xctest") {
            return bundle.bundleURL.deletingLastPathComponent()
        }
        fatalError("couldn't find the products directory")
      #else
        return Bundle.main.bundleURL
      #endif
    }
}
