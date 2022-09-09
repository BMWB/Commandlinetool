//
//  KZUtility.hpp
//  LLVM
//
//  Created by Yaping Liu on 7/22/19.
//

#ifndef KZUtility_hpp
#define KZUtility_hpp

#include <stdio.h>
#include <iostream>
#include <vector>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Lex/Lexer.h"
#include "clang/Frontend/CompilerInstance.h"

using namespace clang;

namespace KZStaticAnalyzer {
    
    bool kz_stringHasPrefix(const std::string &curStr,
                            const std::string &prefix);
    
    std::vector<std::string> kz_stringSplit(const std::string &str,
                                            const std::string &pattern);
    
    std::string kz_getFilePathName(const std::string &fp);
    
    class KZSourceManager {
    public:
        enum ExceptionType {
            None,
            BlockFormat,
            BlockComplexity,
            BlockSelfLeak,
            ClassName,
            MethodDeclare,
            MethodDepth,
            Property,
            Custom,
        };
        
        CompilerInstance *Compiler;
        ASTContext *Context;
        void saveException(std::string exceptionInfo, ExceptionType type);
        void printExceptions(void);
        unsigned getLineNumForLoc(SourceLocation loc);
        //analyze module
//        std::string t_methodDeclareLength;
//        std::string t_methodBodyDepth;
//        std::string t_blockRootDepth;
//        std::string t_blockenst;

    private:
        std::string blockFormatExces;
        std::string blockComplexityExces;
        std::string blockSelfLeakExces;
        std::string classNameExces;
        std::string methodDeclareExces;
        std::string methodDepthExces;
        std::string propertyExces;
        std::string customExces;

    };
}

#endif /* KZUtility_hpp */
