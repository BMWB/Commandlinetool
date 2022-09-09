//
//  KZUtility.cpp
//  LLVM
//
//  Created by Yaping Liu on 7/22/19.
//

#include "KZUtility.hpp"

using namespace KZStaticAnalyzer;

#define PRINT_IDENTIFIER_START          "#S#"

#define PRINT_IDENTIFIER_END            "#E#"

/**
 Utility methods
 **/
namespace KZStaticAnalyzer {
    bool kz_stringHasPrefix(const std::string &curStr,
                            const std::string &prefix)
    {
        if (curStr.size() < prefix.size()) {
            return false;
        }else{
            if (curStr.compare(0, prefix.size(), prefix) == 0) {
                return true;
            }
        }
        return false;
    }
    
    std::vector<std::string> kz_stringSplit(const std::string &str,
                                            const std::string &pattern)
    {
        char * strc = new char[strlen(str.c_str())+1];
        strcpy(strc, str.c_str());  
        std::vector<std::string> res;
        char* temp = strtok(strc, pattern.c_str());
        while(temp != NULL)
        {
            res.push_back(std::string(temp));
            temp = strtok(NULL, pattern.c_str());
        }
        delete [] strc;
        return res;
    }
    
    std::string kz_getFilePathName(const std::string &fp){
        if (fp.find("/") != std::string::npos) {
            std::string fullName = kz_stringSplit(fp, "/").back();
            if (fullName.find(".")) {
                return kz_stringSplit(fullName, ".")[0];
            }
        }
        return "";
    }
}


/**
 KZSourceManager
 **/
void KZSourceManager::saveException(std::string exceptionInfo, ExceptionType type) {
    
    switch (type) {
        case BlockFormat:
            this->blockFormatExces.append(exceptionInfo);
            this->blockFormatExces.append("\n");
            break;
            
        case BlockSelfLeak:
            this->blockSelfLeakExces.append(exceptionInfo);
            this->blockSelfLeakExces.append("\n");
            break;
            
        case BlockComplexity:
            this->blockComplexityExces.append(exceptionInfo);
            this->blockComplexityExces.append("\n");
            break;
            
        case ClassName:
            this->classNameExces.append(exceptionInfo);
            this->classNameExces.append("\n");
            break;
            
        case MethodDeclare:
            this->methodDeclareExces.append(exceptionInfo);
            this->methodDeclareExces.append("\n");
            break;
            
        case MethodDepth:
            this->methodDepthExces.append(exceptionInfo);
            this->methodDepthExces.append("\n");
            break;
            
        case Property:
            this->propertyExces.append(exceptionInfo);
            this->propertyExces.append("\n");
            break;
            
        case Custom:
            this->customExces.append(exceptionInfo);
            this->customExces.append("\n");

            break;
            
        default:
            break;
    }
}

void KZSourceManager::printExceptions(void) {
    /**
    //analyze module
    std::string printTest = PRINT_IDENTIFIER_START;

    printTest.append("T1S");
    printTest.append(t_methodDeclareLength);
    printTest.append("T1E");

    printTest.append("T2S");
    printTest.append(t_methodBodyDepth);
    printTest.append("T2E");

     printTest.append("T4S");
    printTest.append(t_blockRootDepth);
    printTest.append("T4E");

    printTest.append("T5S");
    printTest.append(t_blockenst);
    printTest.append("T5E");

    
    printTest.append(PRINT_IDENTIFIER_END);
    std::cout << printTest << std::endl;
    return;
    **/
    
    if (this->blockSelfLeakExces.empty() &&
        this->blockComplexityExces.empty() &&
        this->blockFormatExces.empty() &&
        this->methodDeclareExces.empty() &&
        this->propertyExces.empty() &&
        this->methodDepthExces.empty() &&
        this->customExces.empty()) {
        return;
    }
    
    std::string printInfos = PRINT_IDENTIFIER_START;
    
    //block self leak
    if (!this->blockSelfLeakExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Block Leak :\n");
        printInfos.append(this->blockSelfLeakExces);
    }

    //block complexity exces
    if (!this->blockComplexityExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Block Complexity :\n");
        printInfos.append(this->blockComplexityExces);
    }
    
    //block format exces
    if (!this->blockFormatExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Block Format :\n");
        printInfos.append(this->blockFormatExces);
    }
    
    //class name exces
//    if (!this->classNameExces.empty()) {
//        printInfos.append("\n\n🔧🔧🔧  Nonstandard Class Name :\n");
//        printInfos.append(this->classNameExces);
//    }
    
    //method length exces
    if (!this->methodDeclareExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Method Declare Length :\n");
        printInfos.append(this->methodDeclareExces);
    }
    
    //method depth exces
    if (!this->methodDepthExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Method Body Depth :\n");
        printInfos.append(this->methodDepthExces);
    }

    //property exces
    if (!this->propertyExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Property Name :\n");
        printInfos.append(this->propertyExces);
    }
    
    //custom exces
    if (!this->customExces.empty()) {
        printInfos.append("\n\n🔧🔧🔧  Custom exceptions :\n");
        printInfos.append(this->customExces);
    }

    printInfos.append(PRINT_IDENTIFIER_END);
    std::cout << printInfos << std::endl;
}

unsigned KZSourceManager::getLineNumForLoc(SourceLocation loc)
{
    return this->Compiler->getSourceManager().getSpellingLineNumber(loc);
}
