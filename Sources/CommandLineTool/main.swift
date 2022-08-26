import CommandLineToolCore

let tool = CommandLineReleases()

do {
    try tool.run()
} catch {
    print("Whoops! An error occurred: \(error)")
}
