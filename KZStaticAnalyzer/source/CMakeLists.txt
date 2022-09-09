
#Make command line tool config
add_clang_executable(KZStaticAnalyzer
    KZStaticAnalyzer.cpp
    KZStaticAnalyzer.hpp
    KZRecursiveASTVisitor.cpp
    KZRecursiveASTVisitor.hpp
    KZUtility.cpp
    KZUtility.hpp
    KZCanonicalQuantify.h
)
target_link_libraries(KZStaticAnalyzer PRIVATE
    clangAST
    clangBasic
    clangFrontend
    clangLex
    LLVMSupport
    clangTooling
)


#Make clang plugin config
#add_llvm_library(KZStaticAnalyzer MODULE
#KZStaticAnalyzer.cpp
#KZStaticAnalyzer.hpp
#KZRecursiveASTVisitor.cpp
#KZRecursiveASTVisitor.hpp
#KZUtility.cpp
#KZUtility.hpp
#KZCanonicalQuantify.h
#PLUGIN_TOOL clang
#)

#if(LLVM_ENABLE_PLUGINS AND (WIN32 OR CYGWIN))
#target_link_libraries(KZStaticAnalyzer PRIVATE
#    clangAST
#    clangBasic
#    clangFrontend
#    clangLex
#    LLVMSupport
#    clangTooling
#)
#endif()
