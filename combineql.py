#!/usr/bin/env python 

import sys 
import pandas as pd
import os

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -q Quotations.xlsx -l Links.xlsx -o output_data.xlsx []
    -q quotations_data_path Quotations export from atlas ti project 
    -l links_data_path      Links export from atlas ti project 
    -o output_data_path     Output data file''')
    sys.exit(exitcode)

def switchTargetSource(ldf, index): 
    '''
    Change the source to the target and the target to the source. 
    param ldf: links data frame 
    param index: row in data frame want to swap 
    return links data frame 
    '''
    # save source in temp vars 
    sid         = ldf['SID'][index]
    source      = ldf['Source'][index] 
    sourceCode  = ldf['Source Code'][index]
    # set source to target 
    ldf['SID'][index]           = ldf['TID'][index] 
    ldf['Source'][index]        = ldf['Target'][index] 
    ldf['Source Code'][index]   = ldf['Target Code'][index]
    # set target to source 
    ldf['TID'][index]           = sid
    ldf['Target'][index]        = source
    ldf['Target Code'][index]   = sourceCode
    return ldf 

def singularizeCode(ldf, code, codesList, colTitle, index): 
    '''
    Each source/target should only have one code in the links data frame. 
    This function takes a list of codes and the desired code and changes the dataframe 
    so that the source/target only has one code in that row. 
    param ldf: links data frame 
    param code: str, Code that should be source/target (ex: 'Antecedent')
    param codesList: list,  the list of codes (ex: sourceCodes) 
    param colTitle: str, the column holding the codes (ex: 'Source Code')
    param index: int, the row in the data frame that you are trying to singularize the codes on 
    return ldf 
    '''
    if code in codesList: 
        ldf[colTitle][index] = code
    else: 
        print(f"ERROR: relation is {relation} but {code} not in {codesList}")
        print(ldf.loc[[index]]) 
    return ldf 

def validateCodes(ldf): 
    ''' 
    Adjust the codes in the links df 
    - only one code per source/target 
    - Antecedent -> Anaphor 
    - Cataphor -> Postcedent 
    - Exophora -> Referent
    param ldf: links data frame 
    return links data frame 
    '''
    for index in ldf.index: 
        sourceCodes = ldf['Source Code'][index].split('\n')
        targetCodes = ldf['Target Code'][index].split('\n')
        relation    = ldf['Relation'][index]
        # only one code per source
        # TODO: need to write out/check logic 
        if len(sourceCodes) > 1: 
            if relation == 'Anaphor': 
                ldf = singularizeCode(ldf, 'Antecedent', sourceCodes, 'Source Code', index)
            elif relation == 'Cataphor': 
                ldf = singularizeCode(ldf, 'Cataphor', sourceCodes, 'Source Code', index)
            elif relation == 'Exophora': 
                ldf = singularizeCode(ldf, 'Exophora', sourceCodes, 'Source Code', index)
            else: 
                print(f"ERROR: {relation} not an accepted relation")
        # only one code per target 
        if len(targetCodes) > 1: 
            if relation == 'Anaphor': 
                ldf = singularizeCode(ldf, 'Anaphor', targetCodes, 'Target Code', index)
            elif relation == 'Cataphor': 
                ldf = singularizeCode(ldf, 'Postcedent', targetCodes, 'Target Code', index)
            elif relation == 'Exophora': 
                if 'Referent' in targetCodes: 
                    ldf['Target Code'][index] = 'Referent'
                else: 
                    if ldf['Source Code'][index] == 'Referent' and 'Exophora' in targetCodes: 
                        ldf['Target Code'][index] = 'Exophora'
                        ldf = switchTargetSource(ldf, index)
                        # TODO: difference between switching codes and switching entire source/target! 
                    else: 
                         print(f"ERROR: relation is {relation} but 'Referent' not in {targetCodes}") 
                         print(ldf.loc[[index]])


        # TODO: order source -> target 
        counterparts = {'Antecedent':'Anaphor', 'Cataphor':'Postcedent', 'Exophora':'Referent'}
        sourceCode = ldf['Source Code'][index]
        targetCode = ldf['Target Code'][index]
        if sourceCode not in counterparts:
            print(f"{sourceCode} not an acceptable source, {targetCode} is targetCode")
            if targetCode in counterparts: 
                # check if target counterpart to source
                if counterparts[targetCode] == sourceCode: 
                    # if counterpart, then switch source and target 
                    ldf = switchTargetSource(ldf, index) 
                else:
                    # if not counterparts, then error 
                    print(f"ERROR: {sourceCode} not a counterpart to {targetCode}")
            else: 
                print(f"ERROR: neither {sourceCode} nor {targetCode} is an acceptable source")
        else: # source is an accepted source 
            # check if source -> target correct counterparts 
            if counterparts[sourceCode] != targetCode: 
                # if not, ERROR     
                print(f"ERROR: source {sourceCode} !-> target {targetCode}")
                print(ldf.loc[[index]])
    return ldf 

def addCodes(ldf, qdf): 
    '''
    Add the code for each source and target to the links data frame 
    param ldf: links data frame 
    parm qdf: quotaitons data frame 
    return links dataframe 
    '''
    # add Source Codes col 
    ldf.insert(loc=2, column='Source Code', value="")
    
    # add Target Codes col 
    ldf['Target Code'] = ""
   
    # create dictionary with IDs as keys and codes as values ({1:5 : Antecedant, 1:6 : Anaphor...})
    codes = {row[0]: row[5] for row in qdf.values}
    
    # add codes to both source and target in links df 
    for index in ldf.index: 
        ldf['Source Code'][index] = codes[ldf['SID'][index]]
        ldf['Target Code'][index] = codes[ldf['TID'][index]]

    return ldf 

def changeLineNumFormat(qdf): 
    ''' 
    The line num format is currently '62 - 62'
    Change this to just be '62'
    param: quotations dataframe 
    return quotations dadtaframe 
    '''
    qdf['Line #'] = [l.split()[0] for l in qdf['Line #']]    
    return qdf 

def removeP1Comments(qdf): 
    '''
    When I first started annotating, I commented every exophora for participant01. 
    This function removes those comments because they are not helpful because I used 
    a separate document called participant01_exophoras to document references instead. 
    param: quotations dataframe 
    return quotations dataframe 
    '''
    qdf.loc[(qdf.Document == 'participant01'), 'Comment']=''
    return qdf

def main(): 
    # command line parsing 
    arguments = sys.argv[1:]
    if len(arguments) < 6: 
        usage(0)
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-q':
            quotations_data_path = arguments.pop(0)
        elif argument == '-l':
            links_data_path = arguments.pop(0)
        elif argument == '-o':
            output_data_path = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(1)
    
    # ensure input data files exists 
    if not os.path.exists(quotations_data_path) or not os.path.exists(links_data_path):
        usage(1)

    # create data frames 
    qdf = pd.DataFrame() 
    qdf = qdf.append(pd.read_excel(quotations_data_path), ignore_index=True)
    ldf = pd.DataFrame() 
    ldf = ldf.append(pd.read_excel(links_data_path), ignore_index=True)
    
    # delete unneeded cols 
    qdf = qdf.drop('Document Groups', 1)
    ldf = ldf.drop('Unnamed: 2',1)

    # rename cols 
    qdf = qdf.rename(columns={'Reference':'Line #'})
    ldf = ldf.rename(columns={'ID':'SID', 'ID.1':'TID'})
   
    # remove unneeded comments 
    qdf = removeP1Comments(qdf)

    # change line number strange formating to one number 
    qdf = changeLineNumFormat(qdf)

    # add quote codes to links 
    ldf = addCodes(ldf,qdf)

    # validate codes 
    ldf = validateCodes(ldf)

    #print(qdf)
    print(ldf)
    
    # export to output file 
    #qdf.to_excel(f"{output_data_path}")
    ldf.to_excel(f"{output_data_path}")

if __name__ == '__main__': 
    main() 
