#!/usr/bin/env python 

import sys 
import pandas as pd
import os
import re 

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -i input_data.xlsx -o output_data.xlsx []
    -i input_data_path      Output from combineql.py
    -o output_data_path     Output data file''')
    sys.exit(exitcode)

def error(message, df, index): 
    '''
    Prints a message and a specified row of the data frame
    param message: error message 
    param df: data frame 
    param index: row # in data frame with error 
    '''
    print(f"ERROR: {message}")
    print(df.loc[[index]])

def addRefDiffs(df): 
    '''
    Adds columsn to the data frame with the difference between the source reference # and the target reference # 
    but only for cataphor and anaphor 
    '''
    df['Ref Diff'] = ""
    for index in df.index: 
        if df['Target Code'][index] != 'Referent':
            sourceRef = df['SID'][index].split(':')[1]
            targetRef = df['TID'][index].split(':')[1]
            refDiff = int(targetRef) - int(sourceRef)
            if refDiff < 0: 
                error(f"refDiff: {refDiff}", df, index)
            df['Ref Diff'][index] = refDiff
        
    #df.loc[df['Target Code'] != 'Referent', 'Ref Diff'] = df['TID'].split(':')[1] - df['SID'].split(':')[1]
    return df 

def addLineDiffs(df): 
    '''
    Adds columns to the data frame with the difference between the Source Line and the Target Line, 
    but only for Cataphor and Anaphor 
    '''
    df.loc[df['Target Code'] != 'Referent', 'Line Diff'] = df['Target Line'] - df['Source Line']
    df.loc[df['Relation'] == 'Anaphor', 'Anaphor Line Diff'] = df['Line Diff']
    df.loc[df['Relation'] == 'Cataphor', 'Cataphor Line Diff'] = df['Line Diff']

    return df

def calcLineMeans(df): 
    '''
    Calculate the average distance between source and target 
    '''
    print(f"Line Difference Mean: {df['Line Diff'].mean()}")
    print(f"Anaphor Line Difference Mean: {df['Anaphor Line Diff'].mean()}")
    print(f"Cataphor Line Difference Mean: {df['Cataphor Line Diff'].mean()}")
    

def main(): 
    # command line parsing 
    arguments = sys.argv[1:]
    if len(arguments) < 4: 
        usage(0)
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-i':
            input_data_path = arguments.pop(0)
        elif argument == '-o':
            output_data_path = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(1)
    
    # ensure input data files exists 
    if not os.path.exists(input_data_path):
        usage(1)

    # create data frames 
    df = pd.DataFrame() 
    df = df.append(pd.read_excel(input_data_path), ignore_index=True)
    
    # add line diff cols 
    df = addLineDiffs(df)
    
    # calculate line diff averages 
    calcLineMeans(df)

    df = addRefDiffs(df)

    # export to output file
    print(df)
    df.to_excel(f"{output_data_path}")

if __name__ == '__main__': 
    main() 
