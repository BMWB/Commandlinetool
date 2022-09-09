//
//  KZStaticAnalyzer.hpp
//  LLVM
//
//  Created by Yaping Liu on 7/16/19.
//

#ifndef KZStaticAnalyzer_hpp
#define KZStaticAnalyzer_hpp

#include "clang/Frontend/FrontendActions.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Signals.h"
#include "clang/Frontend/FrontendPluginRegistry.h"
#include "KZRecursiveASTVisitor.hpp"

using namespace clang;
using namespace clang::tooling;
namespace KZStaticAnalyzer {
    
    class KZASTConsumer: public ASTConsumer {
    public:
        KZASTConsumer(CompilerInstance &Compiler);
    private:
        KZSourceManager sourceMgr;
        KZRecursiveASTVisitor visitor;
        virtual void HandleTranslationUnit(ASTContext &Context);
        //class name
        void _checkClassName(ObjCImplementationDecl *impDecl);
        //property
        void _checkProperty(ObjCContainerDecl *containerDecl,
                            const bool &isHeaderFile);
        //method
        void _checkCFunction(FunctionDecl *funcDecl);
        void _checkOCMethod(ObjCMethodDecl *methodDecl,
                            const bool &isHeaderFile);
        void _checkMethodDeclarLength(const SourceRange &sr,
                                      const bool &isHeaderFile);
        void _checkMethodBody(CompoundStmt *compStmt,
                              const SourceLocation& methodBeginloc);
        void _checkPotentialEexceptionMethod(ObjCMethodDecl *methodDecl);

    };
    
    class KZToolFrontendAction: public ASTFrontendAction {
    public:
        std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &Compiler, StringRef InFile);
    };
    
    class KZPluginFrontendAction: public PluginASTAction {
    public:
        std::unique_ptr <ASTConsumer> CreateASTConsumer(CompilerInstance &Compiler, StringRef InFile);
        //Parse -plugin-arg-<plugin-name> args
        bool ParseArgs(const CompilerInstance &Compiler, const std::vector < std::string >& args);
    };
}

#endif /* KZStaticAnalyzer_hpp */
