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

    print(qdf)
    print(ldf)

if __name__ == '__main__': 
    main() 
