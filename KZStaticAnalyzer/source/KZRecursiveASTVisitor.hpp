//
//  KZRecursiveASTVisitor.hpp
//  LLVM
//
//  Created by Yaping Liu on 7/18/19.
//

#ifndef KZRecursiveASTVisitor_hpp
#define KZRecursiveASTVisitor_hpp

#include "KZUtility.hpp"

using namespace clang;

namespace KZStaticAnalyzer {

    class KZRecursiveASTVisitor: public RecursiveASTVisitor<KZRecursiveASTVisitor> {
        
    public:
        KZSourceManager *sourceMgr;
        bool VisitBlockExpr(BlockExpr *blockExp);
        void checkCurrentNestBlocksComplexity(void);

    private:
        std::vector<BlockExpr *> nestBlocks;
        void _checkBlockSelfLeak(BlockExpr *blockExp);
        void _checkBlockNestNodes(BlockExpr *blockExp);
        void _checkBlockCodeFormat(BlockExpr *blockExp);
        bool _checkContainBlocks(BlockExpr *sourceBlock, BlockExpr *targetBlock);
    };

}

#endif /* KZRecursiveASTVisitor_hpp */
