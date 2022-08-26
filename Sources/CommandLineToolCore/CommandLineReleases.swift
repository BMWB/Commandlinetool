//
//  File.swift
//  
//
//  Created by admin on 2022/8/26.
//

import Foundation
import Releases

public final class CommandLineReleases {
    private let arguments: [String]
    
    public init(arguments: [String] = CommandLine.arguments) {
        self.arguments = arguments
    }
    
    public func run() throws {
        
        guard arguments.count > 1 else {
            throw Error.missingFileName
        }
        
        let fileName = arguments[1]
        
        let url = URL(string: fileName)! //"https://github.com/johnsundell/unbox"
        let releases = try? Releases.versions(for: url)
        // Print the latest version
        print(releases as Any)
    
    }
}

public extension CommandLineReleases {
    enum Error: Swift.Error {
        case missingFileName
        case failedToCreateFile
    }
}

