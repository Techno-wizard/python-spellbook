#!/usr/bin/python2.7
# 7 9 2012
# v 0.1

# import exsteions
#

import sys
import os
import argparse
import string
import eyed3

import nltk
from nltk.tokenize import *

import Azlyrics
import songlyrics
import lyricsfreak

def extract_file(file):
    try:
        track = eyed3.load(file).tag
        query = track.title
    except:
        query = ''
    return query

def print_result(result,lower_case,remove_puntc,first_char):
    
    for text_block in result:
        for line in text_block:
            if lower_case :
                line = line.lower()
            if remove_puntc :
                line = line.translate(string.maketrans("",""), string.punctuation)
                
            first_char_line,num_words = first_char_only(line)
            if first_char :
                line = first_char_line
            
            print line
    return
    
def first_char_only(line):
    output = ''
    num_words = 0
    for word in line.split():
        num_words = num_words + 1
        output += word[0]
    return output,num_words

def search_site(song,site):
    if site == 0:
        print 'Search AZlyric\n'
        result = Azlyrics.search_lyrics(query)
    elif site == 1:
        print 'Search songlyrics\n'
        result = songlyrics.search_lyrics(query)
    elif site == 2:
        print 'Search lyricsfreak'
        result = lyricsfreak.search_lyrics(query)
    else:
        print 'No Site specified\n'
        result ='No search'
    return result

##### START OF MAIN CODE BLOCK #####
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_file', help='Specify a test File',required=False,default='',nargs='?')
    parser.add_argument('--song', help='Specify the song Title',required=False,default='',nargs='?')
    parser.add_argument('--song_list', help='Specify a list of songs',required=False,default='',nargs='?')
    parser.add_argument('--folder', help='Specify a folder of songs',required=False,default='',nargs='?')
    parser.add_argument('--min_words', help='Specify the minimum number of words',required=False,default='',nargs='?')
    parser.add_argument('--max_words', help='Specify the max number of words',required=False,default='',nargs='?')
    parser.add_argument('--write_file', help='Specify the file name for results',required=False,default='',nargs='?')
    parser.set_defaults(lower_case=False)
    parser.set_defaults(remove_puntc=False)
    parser.set_defaults(fist_char=False)  
    parser.add_argument('--lower_all_case', help='Out put all in lower case',required=False,dest='lower_case',action='store_true')
    parser.add_argument('--remove_puntc', help='Remove punctuation',required=False,dest='remove_puntc',action='store_true')
    parser.add_argument('--first_char', help='fist chariter only',required=False,dest='first_char',action='store_true')
    #parser.add_argument('--no-feature',dest='feature',action='store_false')
    
    args = parser.parse_args()

    text_file=args.text_file
    song=args.song
    song_list=args.song_list
    folder=args.folder
    min_words=args.min_words
    max_words=args.max_words
    lower_case=args.lower_case
    remove_puntc=args.remove_puntc
    first_char=args.first_char
    results_file_name=args.write_file
    
    site = 2

    if text_file :
        try:
            with open(text_file) as txt_file:
                result = txt_file.read()
                
            text_block = []   
            text_sent_tokens = LineTokenizer(blanklines='discard').tokenize(result)
            text_block.append(text_sent_tokens)
            print_result(text_block,lower_case,remove_puntc,first_char)
        except:
            print 'file not found'
            sys.exit(1)

    if song :
        print song
        query = song
        result = search_site(query,site)
        print_result(result,lower_case,remove_puntc,first_char)
    
    if song_list :
        try:
            with open(song_list) as song_file:
                list_of_songs = song_file.readlines()
        except:
            print 'file not found'
            sys.exit(1)
        
        for song in list_of_songs:
            print song
            query = song
            result = search_site(query,site)
            print_result(result,lower_case,remove_puntc,first_char)
            
    if folder :
        folder_list = os.listdir(folder)
        for song in folder_list:
            full_path_song = folder + '/' + song
            if os.path.isfile(full_path_song): 
                query = extract_file(full_path_song)
                if (query == ''):
                    query = song
                result = search_site(query,site)
                print_result(result,lower_case,remove_puntc,first_char)


        