//
//  KZRecursiveASTVisitor.cpp
//  LLVM
//
//  Created by Yaping Liu on 7/18/19.
//

#include "KZRecursiveASTVisitor.hpp"
#include "KZCanonicalQuantify.h"

using namespace KZStaticAnalyzer;

/**
 Block check methods
 **/
bool KZRecursiveASTVisitor::VisitBlockExpr(BlockExpr *blockExp)
{
    /** check block code format **/
    _checkBlockCodeFormat(blockExp);

    /** check block complexity segment **/
    bool containInRoot = false;
    if (!nestBlocks.empty()) {
        BlockExpr *rootBExpr = nestBlocks[0];
        if (_checkContainBlocks(rootBExpr, blockExp)) {
            containInRoot = true;
            _checkBlockNestNodes(blockExp);
        }else{
            checkCurrentNestBlocksComplexity();
            nestBlocks.clear();
        }
    }
    nestBlocks.push_back(blockExp);
    
    /** check block leak of `self` segment **/
    //if current block in root block, does't execute `self` leak detection.
    if (containInRoot) return true;
    _checkBlockSelfLeak(blockExp);
    
    return true;
}

void KZRecursiveASTVisitor::_checkBlockCodeFormat(BlockExpr *blockExp) {
    return;
    CompoundStmt *cmpSt = dyn_cast_or_null<CompoundStmt>(blockExp->getBody());
    if (!cmpSt) return;
    
    SourceManager &manager = this->sourceMgr->Compiler->getSourceManager();
    const LangOptions &lp = this->sourceMgr->Context->getLangOpts();
    Optional<Token> inBodyFirstToken = Lexer::findNextToken(cmpSt->getBeginLoc(), manager, lp);
    if (inBodyFirstToken == None) return;
    unsigned column = manager.getSpellingColumnNumber(inBodyFirstToken.getValue().getLocation());
    if (column >= BLOCK_FORMAT_LIMIT_COLUMN) {
        unsigned line = this->sourceMgr->getLineNumForLoc(blockExp->getBeginLoc());
        std::string info = "Has non-standard block body indent in line ";
        info.append(std::to_string(line));
        this->sourceMgr->saveException(info, KZSourceManager::BlockFormat);
    }
}


void KZRecursiveASTVisitor::_checkBlockNestNodes(BlockExpr *blockExp) {
    BlockExpr *lastBlock = nestBlocks.back();
    bool containtInLast = _checkContainBlocks(lastBlock, blockExp);
    if (!containtInLast) {
        checkCurrentNestBlocksComplexity();
        //recursive delete expr which not contain current block expr.
        for (auto ite = nestBlocks.begin(); ite != nestBlocks.end();) {
            if(!_checkContainBlocks(*ite, blockExp)){
                ite = nestBlocks.erase(ite);
            }else{
                ite++;
            }
        }
    }
}


void KZRecursiveASTVisitor::_checkBlockSelfLeak(BlockExpr *blockExp)
{
    //check the block whether need be checked.
    bool isValidBlock = true;
    const auto& parentList = this->sourceMgr->Context->getParents(*blockExp);
    if (!parentList.empty()) {
        const ObjCMessageExpr *messageExp = parentList[0].get<ObjCMessageExpr>();
        if (messageExp) {
            ObjCInterfaceDecl *callDecl = messageExp->getReceiverInterface();
            if (callDecl) {
                std::string clsName = callDecl->getNameAsString();
                //filter UIKit block
                if (kz_stringHasPrefix(clsName, "_UI") || kz_stringHasPrefix(clsName, "UI")) {
                    isValidBlock = false;
                }
            }
            if (isValidBlock) {
                //filter masonry block
                const ObjCMethodDecl *methodDecl = messageExp->getMethodDecl();
                if (methodDecl) {
                    std::string methodName = methodDecl->getSelector().getAsString();
                    if (kz_stringHasPrefix(methodName, "mas_")) {
                        isValidBlock = false;
                    }
                }
            }
        }else{
            const CallExpr *callExp = parentList[0].get<CallExpr>();
            if (callExp) {
                const FunctionDecl *funcDecl = callExp->getDirectCallee();
                if (funcDecl) {
                    std::string funcName = funcDecl->getNameAsString();
                    if (funcName.find("dispatch_") != std::string::npos || kz_stringHasPrefix(funcName, "co_launch")) {
                        isValidBlock = false;
                    }
                }
            }
        }
    }
    if (!isValidBlock) return;
    
    //whether has self
    BlockDecl *bDecl = blockExp->getBlockDecl();
    if (!bDecl->hasCaptures()) return;
    bool hasLeak = false;
    BlockDecl::capture_const_iterator iter = bDecl->capture_begin();
    for (; iter != bDecl->capture_end(); iter++) {
        ImplicitParamDecl *implicitDecl = dyn_cast_or_null<ImplicitParamDecl>(iter->getVariable());
        if (implicitDecl && implicitDecl->getParameterKind() == ImplicitParamDecl::ObjCSelf) {
            hasLeak = true;
            break;
        }
    }
    if (!hasLeak) return;
    
    //set self diagnostic
    CompoundStmt *cmpSt = dyn_cast_or_null<CompoundStmt>(blockExp->getBody());
    if (!cmpSt || cmpSt->body_empty()) return;
    SourceManager& manager = this->sourceMgr->Compiler->getSourceManager();
    const LangOptions& lp = this->sourceMgr->Context->getLangOpts();
    SourceLocation curLoc = cmpSt->getBeginLoc();
    while (curLoc < cmpSt->getEndLoc()) {
        Optional<Token> next = Lexer::findNextToken(curLoc, manager, lp);
        if (next == None) break;
        Token nt = next.getValue();
        std::string tokenStr = Lexer::getSpelling(nt, manager, lp);
        curLoc = next.getValue().getLocation();
        if (nt.getKind() == tok::raw_identifier && tokenStr.compare("self") == 0) {
            unsigned line = this->sourceMgr->getLineNumForLoc(curLoc);
            std::string info = "Find block Leak in line: ";
            info.append(std::to_string(line));
            this->sourceMgr->saveException(info, KZSourceManager::BlockSelfLeak);

            DiagnosticsEngine &DiagEngine = this->sourceMgr->Compiler->getDiagnostics();
            const char diagInfo[] = "The `self` keywork is found here in Block!";
            int diagID = DiagEngine.getCustomDiagID(DiagnosticsEngine::Warning, diagInfo);
            DiagEngine.Report(curLoc, diagID);
        }
    }
}

void KZRecursiveASTVisitor::checkCurrentNestBlocksComplexity(void)
{
    //analyze module
//    if (nestBlocks.size() > 0) {
//        BlockExpr *rootExp = nestBlocks[0];
//        unsigned startLine = this->sourceMgr->getLineNumForLoc(rootExp->getBeginLoc());
//        unsigned endLine = this->sourceMgr->getLineNumForLoc(rootExp->getEndLoc());
//        unsigned rootBlockLines = endLine - startLine;
//        this->sourceMgr->t_blockRootDepth.append(std::to_string(rootBlockLines).append(","));
//        this->sourceMgr->t_blockenst.append(std::to_string(nestBlocks.size()).append(","));
//    }
//    return;
    
    
    if (nestBlocks.size() >= BLOCK_COMPLEXITY_NEST_LIMIT_NUM) {
        BlockExpr *rootExp = nestBlocks[0];
        unsigned startLine = this->sourceMgr->getLineNumForLoc(rootExp->getBeginLoc());
        unsigned endLine = this->sourceMgr->getLineNumForLoc(rootExp->getEndLoc());
        unsigned rootBlockLines = endLine - startLine;
        if (rootBlockLines >= BLOCK_COMPLEXITY_ROOT_LIMIT_LINE) {
            std::string logInfo = "Complex block has ";
            logInfo.append(std::to_string(rootBlockLines));
            logInfo.append(" lines and call track line: ");
            for (BlockExpr *e : nestBlocks) {
                std::string line = std::to_string(this->sourceMgr->getLineNumForLoc(e->getBeginLoc()));
                logInfo.append("->");
                logInfo.append(line);
            }
            this->sourceMgr->saveException(logInfo, KZSourceManager::BlockComplexity);
        }
    }
}


/**
 General methods
 **/

bool KZRecursiveASTVisitor::_checkContainBlocks(BlockExpr *sourceBlock, BlockExpr *targetBlock)
{
    unsigned srcBeginLine = this->sourceMgr->getLineNumForLoc(sourceBlock->getBeginLoc());
    unsigned srcEndLine = this->sourceMgr->getLineNumForLoc(sourceBlock->getEndLoc());

    unsigned tarBeginLine = this->sourceMgr->getLineNumForLoc(targetBlock->getBeginLoc());

    if (tarBeginLine >= srcBeginLine && tarBeginLine < srcEndLine) {
        return true;
    }
    return false;
}

