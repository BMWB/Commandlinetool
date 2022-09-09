//
//  KZStaticAnalyzer.hpp
//  LLVM
//
//  Created by Yaping Liu on 7/18/19.
//

#include "KZStaticAnalyzer.hpp"
#include "KZCanonicalQuantify.h"
#include <algorithm>

using namespace KZStaticAnalyzer;
/**
 Basic check methods
 **/
KZASTConsumer::KZASTConsumer(CompilerInstance &Compiler)
{
    this->sourceMgr.Compiler = &Compiler;
    this->visitor.sourceMgr = &(this->sourceMgr);
}

void KZASTConsumer::HandleTranslationUnit(ASTContext &Context)
{
    //set translation context
    this->sourceMgr.Context = &Context;
    //check self in block
    TranslationUnitDecl *unitDecl = Context.getTranslationUnitDecl();
    DeclContext::decl_range range = unitDecl->decls();
    const FileID& mainID = this->sourceMgr.Compiler->getSourceManager().getMainFileID();
    const FileEntry * entry = this->sourceMgr.Compiler->getSourceManager().getFileEntryForID(mainID);
    std::string mainFileName = kz_getFilePathName(entry->getName().str());

    for (Decl *perDecl : range) {
        //whether is main file or main file header
        std::string curFilePath = this->sourceMgr.Compiler->getSourceManager().getFilename(perDecl->getLocation()).str();
        std::string curFileName = kz_getFilePathName(curFilePath);
        if (curFileName != mainFileName) {
            continue;
        }
        bool isHeaderFile = !this->sourceMgr.Compiler->getSourceManager().isInMainFile(perDecl->getLocation());
        //check c fucntion
        FunctionDecl *funcDecl = dyn_cast_or_null<FunctionDecl>(perDecl);
        if (funcDecl) {
            _checkCFunction(funcDecl);
            continue;
        }
        
        //container
        ObjCContainerDecl *containerDecl = dyn_cast_or_null<ObjCContainerDecl>(perDecl);
        if (containerDecl) {
            //search implementation decl
            ObjCImplementationDecl *impDecl = dyn_cast_or_null<ObjCImplementationDecl>(perDecl);

            if (impDecl) {
                //check class name
                _checkClassName(impDecl);
            }else{
                //check property
                _checkProperty(containerDecl, isHeaderFile);
            }
            for (ObjCMethodDecl *mDecl : containerDecl->methods()) {
                //check oc method
                _checkOCMethod(mDecl, isHeaderFile);
                if (impDecl){
                    //check blcok related
                    CompoundStmt *methodBody = mDecl->getCompoundBody();
                    if (methodBody && !methodBody->body_empty()) {
                        this->visitor.TraverseStmt(methodBody);
                    }
                }
            }
        }
    }
    //check nest block vector when current file analyze end.
    this->visitor.checkCurrentNestBlocksComplexity();
    //format print all exceptions.
    this->sourceMgr.printExceptions();
}

void KZASTConsumer::_checkClassName(ObjCImplementationDecl *impDecl)
{
    if(!impDecl) return;
    std::string clsName = impDecl->getNameAsString();
    const char *standards[] = CLASS_NAME_PREFIXS;
    bool valid = false;
    for (const char *prefix : standards) {
        if (kz_stringHasPrefix(clsName, prefix)) {
            valid = true;
            break;
        }
    }
    if (!valid) {
        this->sourceMgr.saveException(clsName, KZSourceManager::ClassName);
    }
}

void KZASTConsumer::_checkCFunction(FunctionDecl *funcDecl)
{
    CompoundStmt *compStmt = dyn_cast_or_null<CompoundStmt>(funcDecl->getBody());
    if (compStmt) {
        SourceRange sr = SourceRange(funcDecl->getBeginLoc(), compStmt->getBeginLoc());
        _checkMethodDeclarLength(sr, false);
        _checkMethodBody(compStmt, funcDecl->getBeginLoc());
    }
}

void KZASTConsumer::_checkOCMethod(ObjCMethodDecl *methodDecl, const bool &isHeaderFile) {
    /** check oc method stardard **/
    //check method length
    SourceRange sr = SourceRange(methodDecl->getBeginLoc(), methodDecl->getDeclaratorEndLoc());
    _checkMethodDeclarLength(sr, isHeaderFile);
    //check
    CompoundStmt *compStmt = methodDecl->getCompoundBody();
    if (compStmt) {
        _checkMethodBody(compStmt, methodDecl->getBeginLoc());
    }
    
    /** check potential exception method **/
    if (!isHeaderFile) {
        _checkPotentialEexceptionMethod(methodDecl);
    }
}

void KZASTConsumer::_checkMethodDeclarLength(const SourceRange &sr, const bool &isHeaderFile) {
    return;
    SourceManager &manager = this->sourceMgr.Compiler->getSourceManager();
    const LangOptions &lp = this->sourceMgr.Context->getLangOpts();
    CharSourceRange ll = manager.getExpansionRange(sr);
    std::string declare = Lexer::getSourceText(ll, manager, lp).str();
    std::vector<std::string> splits = kz_stringSplit(declare, std::string("\n"));
    if (splits.size() > 0) {
        std::string firstLine = splits[0];
        unsigned length = firstLine.size();
        //analyze module
        //this->sourceMgr.t_methodDeclareLength.append(std::to_string(length).append(","));
        unsigned line = this->sourceMgr.getLineNumForLoc(sr.getBegin());
        if (length > METHOD_DECLARE_MAX_LENGTH) {
            std::string info = "Method declaration has ";
            info.append(std::to_string(length));
            info.append(" column in line of ");
            info.append(std::to_string(line));
            if (isHeaderFile) {
                info.append(" in header file");
            }
            this->sourceMgr.saveException(info, KZSourceManager::MethodDeclare);
        }else {
            int fc = count(firstLine.begin(), firstLine.end(), ':');
            if (fc > METHOD_DECLARE_FIRST_LINE_MAX_PARAMS) {
                std::string info = "Method declaration has ";
                info.append(std::to_string(fc));
                info.append(" params in line of ");
                info.append(std::to_string(line));
                if (isHeaderFile) {
                    info.append(" in header file");
                }
                this->sourceMgr.saveException(info, KZSourceManager::MethodDeclare);
            }
        }
    }
}

void KZASTConsumer::_checkMethodBody(CompoundStmt *compStmt,
                                     const SourceLocation& methodBeginloc)
{
    unsigned startLine = this->sourceMgr.getLineNumForLoc(compStmt->getBeginLoc());
    unsigned endLine = this->sourceMgr.getLineNumForLoc(compStmt->getEndLoc());
    unsigned mdp = endLine - startLine;
    if (mdp > METHOD_BODY_MAX_LINES) {
        unsigned line = this->sourceMgr.getLineNumForLoc(methodBeginloc);
        std::string info = "Method body has ";
        info.append(std::to_string(mdp));
        info.append(" rows in line of ");
        info.append(std::to_string(line));
        this->sourceMgr.saveException(info, KZSourceManager::MethodDepth);
    }
//    analyze module
    //this->sourceMgr.t_methodBodyDepth.append(std::to_string(mdp).append(","));
}

void KZASTConsumer::_checkProperty(ObjCContainerDecl *containerDecl, const bool &isHeaderFile) {
    return;
    std::map<std::string, std::string> standardMap = PROPERTY_NAME_STANDARD_MAP;
    for (ObjCPropertyDecl *pDecl : containerDecl->properties()) {
        //get property type name
        std::string typeName = "";
        QualType T = pDecl->getType();
        if (auto TypePtr = T.getTypePtr()) {
            if (TypePtr->isObjCObjectPointerType()) {
                if (auto InterfaceType = TypePtr->getAsObjCInterfacePointerType()) {
                    typeName = InterfaceType->getObjectType()->getBaseType().getAsString();
                }
            }
        }
        if (typeName.size() < 1) continue;
        
        if (standardMap.find(typeName) != standardMap.end()) {
            std::string propertyName = pDecl->getNameAsString();
            std::string prefix = standardMap[typeName];
            if (!kz_stringHasPrefix(propertyName, prefix)) {
                unsigned line = this->sourceMgr.getLineNumForLoc(pDecl->getBeginLoc());
                std::string info = "Naming unstandard in line of ";
                info.append(std::to_string(line));
                if (isHeaderFile) {
                    info.append(" in header file");
                }
                this->sourceMgr.saveException(info, KZSourceManager::Property);
            }
        }
    }
}

/**
 Custom check methods
 **/
void KZASTConsumer::_checkPotentialEexceptionMethod(ObjCMethodDecl *methodDecl)
{
    std::string methodName = methodDecl->getSelector().getAsString();
    //TODO: wait to recursion search ReturnStmt ...
    /**
     In 12.3.1 iOS system version,
     call CUSTOM_POTENTIAL_EXC_METHOD_TABLEVIEW method and return less than 1 will cause crash.
     */
    if (methodName == CUSTOM_POTENTIAL_EXC_METHOD_TABLEVIEW ||
        methodName == CUSTOM_POTENTIAL_EXC_METHOD_COLLECTIONVIEW)
    {
        CompoundStmt *compStmt = methodDecl->getCompoundBody();
        if (compStmt) {
//            std::string returnTypeString = methodDecl->getReturnType().getAsString();
//            std::cout << returnTypeString << std::endl;
            for (auto perSt : compStmt->body()) {
                ReturnStmt *rt = dyn_cast_or_null<ReturnStmt>(perSt);
                if (!rt) continue;
                Expr *valueExpr = rt->getRetValue()->IgnoreImpCasts();
                if (methodName == CUSTOM_POTENTIAL_EXC_METHOD_TABLEVIEW) {
                    bool wrongRetValue = false;
                    FloatingLiteral *fl = dyn_cast_or_null<FloatingLiteral>(valueExpr);
                    if (fl){
                        llvm::APFloat f = fl->getValue();
                        if (f.compare(llvm::APFloat(1.0)) == llvm::APFloatBase::cmpLessThan) {
                            wrongRetValue = true;
                        }
                    }else{
                        IntegerLiteral *il = dyn_cast_or_null<IntegerLiteral>(valueExpr);
                        if (il && il->getValue() == 0) {
                            wrongRetValue = true;
                        }
                    }
                    
                    if (wrongRetValue) {
                        unsigned line = this->sourceMgr.getLineNumForLoc(perSt->getBeginLoc());
                        std::string info = "Method `-tableView:estimatedHeightForFooterInSection:` return value must be greater than or equal to 1 , wrong line: ";
                        info.append(std::to_string(line));
                        this->sourceMgr.saveException(info, KZSourceManager::Custom);
                    }
                }else{
                    CStyleCastExpr *v = (CStyleCastExpr *)valueExpr->IgnoreParens();
                    if (llvm::isa_and_nonnull<CStyleCastExpr>(v)) {
//                        auto TypePtr = v->getType().getTypePtr();
//                        if (TypePtr->isNullPtrType()) {
//                            std::cout << "" << std::endl;
//                        }
                        IntegerLiteral *il = dyn_cast_or_null<IntegerLiteral>(v->getSubExpr());
                        if (il && il->getValue() == 0){
                            unsigned line = this->sourceMgr.getLineNumForLoc(perSt->getBeginLoc());
                            std::string info = "Method `-collectionView:viewForSupplementaryElementOfKind:atIndexPath:` return value should not be nil , wrong line: ";
                            info.append(std::to_string(line));
                            this->sourceMgr.saveException(info, KZSourceManager::Custom);
                        }
                    }
                }
            }
        }
    }
}


/**
 Start methods
 **/
std::unique_ptr<ASTConsumer> KZToolFrontendAction::CreateASTConsumer(CompilerInstance &Compiler, StringRef InFile)
{
    return std::unique_ptr<KZASTConsumer>(new KZASTConsumer(Compiler));
}

std::unique_ptr <ASTConsumer> KZPluginFrontendAction::CreateASTConsumer(CompilerInstance &Compiler, StringRef InFile)
{
    return std::unique_ptr <KZASTConsumer> (new KZASTConsumer(Compiler));
}

bool KZPluginFrontendAction::ParseArgs(const CompilerInstance &Compiler, const std::vector < std::string >& args)
{
    return true;
}


static FrontendPluginRegistry::Add < KZStaticAnalyzer::KZPluginFrontendAction > X("KZStaticAnalyzer", "Kan zhun clang static analyzer");


// Apply a custom category to all command-line options so that they are the
// only ones displayed.
static llvm::cl::OptionCategory MyToolCategory("options");

// CommonOptionsParser declares HelpMessage with a description of the common
// command-line options related to the compilation database and input files.
// It's nice to have this help message in all tools.
static llvm::cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

// A help message for this specific tool can be added afterwards.
static llvm::cl::extrahelp MoreHelp("\nMore help text...\n");

//
int main(int argc, const char **argv) {
    llvm::sys::PrintStackTraceOnErrorSignal(argv[0]);

    CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
    ClangTool Tool(OptionsParser.getCompilations(),
                   OptionsParser.getSourcePathList());
    return Tool.run(newFrontendActionFactory<KZStaticAnalyzer::KZToolFrontendAction>().get());
}

