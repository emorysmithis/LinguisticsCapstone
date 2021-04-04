#!/usr/bin/env python 

import sys 
import pandas as pd
import os
import re 

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -q Quotations.xlsx -l Links.xlsx -o output_data.xlsx []
    -q quotations_data_path Quotations export from atlas ti project 
    -l links_data_path      Links export from atlas ti project 
    -o output_data_path     Output data file''')
    sys.exit(exitcode)

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
        if len(sourceCodes) > 1: 
            if relation == 'Anaphor': 
                if 'Antecedent' in sourceCodes: 
                    ldf['Source Code'][index] = 'Antecedent'
                else: 
                    print(f"ERROR: relation is {relation} but 'Antecedent' not in {sourceCodes}")
                    print(ldf.loc[[index]]) 
            elif relation == 'Cataphor': 
                if 'Cataphor' in sourceCodes: 
                    ldf['Source Code'][index] = 'Cataphor'
                else: 
                    print(f"ERROR: relation is {relation} but 'Cataphor' not in {sourceCodes}")
                    print(ldf.loc[[index]])
            elif relation == 'Exophora': 
                if 'Exophora' in sourceCodes: 
                    ldf['Source Code'][index] = 'Exophora'
                else: 
                    print(f"ERROR: relation is {relation} but 'Exophora' not in {sourceCodes}") 
                    print(ldf.loc[[index]])
        # order source -> target 
        sourceCode = ldf['Source Code'][index]
        targetCode = ldf['Target Code'][index]
        if sourceCode not in ['Antecedent', 'Cataphor', 'Exophora']: 
            print(f"ERROR: {sourceCode} not an acceptable source!")
            # check if target counterpart to source 
            # if counterpart, then switch 
        # else: 
            # check if source -> target correct counterparts 
            # if not, ERROR 
            

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
