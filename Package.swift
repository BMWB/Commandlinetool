// swift-tools-version: 5.6
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "CommandLineTool",
    platforms: [
        .macOS(.v10_12)
    ],
    // 添加下面9-10行
    products: [
        .executable(name: "CommandLineTool", targets: ["CommandLineTool"])
    ],
    
    dependencies: [
        .package(
            url: "https://github.com/johnsundell/files.git",
            from: "4.2.0"
        ),
        .package(url: "https://github.com/JohnSundell/Releases.git", from: "5.0.0"),
        .package(url: "https://github.com/JohnSundell/ShellOut.git", from: "2.0.0"),
        .package(url: "https://github.com/JohnSundell/Require.git", from: "2.0.0")
    ],
    targets: [
        // Targets are the basic building blocks of a package. A target can define a module or a test suite.
        // Targets can depend on other targets in this package, and on products in packages this package depends on.
        .executableTarget(
            name: "CommandLineTool",
            dependencies: ["CommandLineToolCore"]),
        .target(name: "CommandLineToolCore",
                dependencies: [.product(name: "Files", package: "files"),
                               "Releases",
                               "ShellOut",
                               "Require"]),
        .testTarget(
            name: "CommandLineToolTests",
            dependencies: ["CommandLineTool","CommandLineToolCore",.product(name: "Files", package: "files")]),
    ]
)
