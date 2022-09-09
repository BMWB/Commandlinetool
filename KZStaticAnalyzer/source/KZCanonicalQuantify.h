//
//  KZCanonicalQuantify.h
//  LLVM
//
//  Created by Yaping Liu on 7/27/19.
//

#ifndef KZCanonicalQuantify_h
#define KZCanonicalQuantify_h

/**
 Block Format
 **/
#define BLOCK_FORMAT_LIMIT_COLUMN                     50

/**
 Block Complexity
 **/
//root block maximum lines
#define BLOCK_COMPLEXITY_ROOT_LIMIT_LINE              40
//root block maximum nest layers
#define BLOCK_COMPLEXITY_NEST_LIMIT_NUM               4

/**
 Standard Class Name Prefix
 **/
#define CLASS_NAME_PREFIXS                            {"BZ", "BB", "BG"}

/**
 Method Declare
 **/
//declare max length in method first line
#define METHOD_DECLARE_MAX_LENGTH                     130
//max parameter count in method first line
#define METHOD_DECLARE_FIRST_LINE_MAX_PARAMS           4

/**
 Method Body
 **/
#define METHOD_BODY_MAX_LINES                          140


/**
 Property name
 **/
#define PROPERTY_NAME_STANDARD_MAP \
{{"UILabel" , "lb"},\
{"UIButton" , "btn"},\
{"UITextView", "tv"},\
{"UITextField", "tf"},\
{"UITableView", "tb"},\
}

/**
 Custom standard
 **/
//table view estimated height less than 1
#define CUSTOM_POTENTIAL_EXC_METHOD_TABLEVIEW  \
"tableView:estimatedHeightForFooterInSection:"
//collcetion view reusable view return nil
#define CUSTOM_POTENTIAL_EXC_METHOD_COLLECTIONVIEW  \
"collectionView:viewForSupplementaryElementOfKind:atIndexPath:"






#endif /* KZCanonicalQuantify_h */
