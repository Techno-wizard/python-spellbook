#!/usr/bin/env python

import sys, os
import signal
import argparse

from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset

import collections

import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup

import nltk
from nltk.tokenize import *

import socks
import socket
import pickle

# url class
class crawl_link(object):
    # url opject
    
    #  string of char
    def __init__(self, url, type, loc_ex,  depth):
        self.url = url
        self.type = type
        self.loc_ex = loc_ex
        self.depth = depth
                
    # follow method
    def follow(self):
        try:
            # Get a file-like object for the Python Web site's home page.
            req = urllib2.Request(self.url, headers={'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 7.0b;Windows NT 5.1)'})
            url = urllib2.urlopen(req)
            # Read from the object, storing the page's contents in url_content.
            url_content = url.read()
            url.close()
        except urllib2.HTTPError as e:
            message_to_screen(5, e.code)
            message_to_screen(6, e.read()) 
            url_content = ''
        return url_content

class url_content(object):
	# url content class

    def __init__(self, link):
        raw = link.follow()
        self.url = link.url
        self.depth = link.depth
        self.raw = raw
        soup = BeautifulSoup(self.raw)
        # BeautifulSoup processing
        self.soup = soup
        text = soup.get_text()
        if options['lower_case']:
            self.text = text.lower()
        else:
            self.text = text
        
        self.nltk_wd_raw = nltk.word_tokenize(self.text)
        
        if options['tagger'] == 'sb':
            tagger = pickle.load(open("./brown_simplify_tags.pickle"))

        else:
            tagger = nltk.data.load(nltk.tag._POS_TAGGER)
        
        self.tagged_words = tagger.tag(self.nltk_wd_raw)
        #self.tagged_words = nltk.pos_tag(self.nltk_wd_raw)
        
        self.nltk_wd_sorted = sorted(set(self.nltk_wd_raw))
        # Page text
        self.unique_words, self.sentance_list = self.__process_text_page(self.text)
        # page links
        self.number_links, self.links = self.__process_links_in_page(link, soup)
        
    def __process_links_in_page(self, link, soup):
        # classif  links
        link_list =[]
        parse = urlparse(link.url)
        scheme = parse[0]
        netloc_url = parse[1]
        local_path = parse[2]
        href_list = soup.findAll("a", attrs={"href":True})
        for href_link in href_list:
            link_list.append(href_link.get('href'))
        
        src_list = soup.findAll('img', src=True)
        for src_link in src_list:
            link_list.append(src_link['src'])
            
        link_number = (len(link_list))

        # links list
        page_link_list = []
        depth = link.depth + 1

        for found_link in link_list:
            parse = urlparse(found_link)
            
            if (parse[0] == 'http') or (parse[0] == 'https'):   
                # link same base as current link
                if parse[1] == netloc_url:
                    loc_ex = 'loc'
                    new_link = found_link
                else:
                    loc_ex = 'ex'
                    new_link = found_link
            else:
                loc_ex = 'loc'
                if found_link.startswith('/'):
                    new_link = scheme + '://' + netloc_url + found_link
                else:
                    new_link = scheme + '://' + netloc_url + '/' + found_link

            file_ext = parse[2].split('/')[-1].split('.')[-1].lower()
            
            files = ['msi', 'exe', 'gz', 'zip', 'tgz', 'bz2', 'dmg', 'xz', 'rpm', 'chm', 'asc']
            images = ['jpg', 'gif', 'png']
            docs = ['pdf', 'doc', 'docx']
            html = ['html', 'htm', 'php', 'asp']
            
            if file_ext in files:
                type = 'file'
            elif file_ext in images:
                type = 'image'
            elif file_ext in docs:
                type = 'doc'
            elif file_ext in html:
                type = 'html'
            else:
                type = 'html'
   
            page_link_list.append(crawl_link(new_link, type, loc_ex, depth))
            
        return link_number, page_link_list
        
    def __process_text_page(self, text):
        fd = {}
        unique_words = []
        sentance_list = []

        sentance_list = sent_tokenize(text)
        for sentens in sentance_list:
            word_list = word_tokenize(sentens)
            for word_raw in word_list:
                word = word_raw.lower()
                try:
                    fd[word] = fd[word]+1
                except KeyError:
                    fd[word] = 1
    
        for key in fd:
            unique_words.append(key)
            
        #unique_words = sorted(set(unique_words)) 
        return unique_words, sentance_list

def signal_handler(signal, frame):
        message_to_screen(5,'You pressed Ctrl+C!')
        sys.exit(0)
    
def create_connection(address, timeout=None, source_address=None):
        sock = socks.socksocket()
        sock.connect(address)
        return sock

def command_line_options():
    global options
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Starting url:',required=True,default='',nargs='?')
    parser.add_argument('-ex', '--external_links', help='Follow external links:',required=False, action='store_true')
    parser.add_argument('-d', '--depth_of_links', help='Depth on links to follow:',required=False,default= 0 ,nargs='?')
    parser.add_argument('-f', '--file_name', help='Root file name for lists:',required=False,default=None ,nargs='?')
    parser.add_argument('-m', '--max_char', help='maximum length of characters:',required=False,default= 0 ,nargs='?')
    parser.add_argument('-lc', '--lower_case', help='Flag for lower case all text:',required=False, action='store_true')
    parser.add_argument('-wl', '--words_flag', help='Flag for word list:',required=False, action='store_true')
    parser.add_argument('-ph', '--phrase_flag', help='Flag for phrase list:',required=False, action='store_true')
    parser.add_argument('-pl', '--pair_flag', help='Flag for pair list:',required=False, action='store_true')
    parser.add_argument('-bl', '--bi_flag', help='Flag for bi word list:',required=False, action='store_true')
    parser.add_argument('-tl', '--tri_flag', help='Flag for  tri word list:',required=False, action='store_true')
    parser.add_argument('-gl', '--gramma_flag', help='Flag for  gramma rule word list:',required=False, action='store_true')
    parser.add_argument('-np', '--no_socks_proxy', help='Do not use local Tor socks proxy:',required=False, action='store_true')
    parser.add_argument('-v', '--verbosity', help='How much to display on screen 0 - 10 (default 5):',required=False,default= 5 ,nargs='?')
    parser.add_argument('-di', '--down_load_images', help='Down load images:',required=False, action='store_true')
    parser.add_argument('-dd', '--down_load_docs', help='Down load documents:',required=False, action='store_true')
    parser.add_argument('-df', '--down_load_files', help='Down load files:',required=False, action='store_true')
    parser.add_argument('-sd', '--download_directory', help='Directory to save download files in:',required=False, default = '.' ,nargs = '?')
    args = parser.parse_args()
    
    options = {}
    options['url'] = args.url
    options['depth'] = int(args.depth_of_links)
    options['ex_ln'] = args.external_links
    options['max_char'] = int(args.max_char)
    options['lower_case'] = args.lower_case
    options['file_name'] = args.file_name
    options['words_flag'] = args.words_flag
    options['phrase_flag'] = args.phrase_flag
    options['pair_flag'] = args.pair_flag
    options['bi_flag'] = args.bi_flag
    options['tri_flag'] = args.tri_flag
    options['gramma_flag'] = args.gramma_flag
    options['no_proxy'] = args.no_socks_proxy
    options['verbosity'] = args.verbosity
    options['download_images'] = args.down_load_images
    options['download_docs'] = args.down_load_docs
    options['download_files'] = args.down_load_files
    options['download_directory'] = args.download_directory
    options['tagger'] = 'sb'
        
    return options

def message_to_screen(message_level, message):
    if message_level <= int(options['verbosity']):
        print message
    return

def unique_tagged_words(page_tagged_words):
    for word in page_tagged_words:
        if word[0]  not in schar_set:
            if word not in total_tagged_words:
            # put unque words from page in overall unquie word list
                total_tagged_words.append(word)       
    return

def unique_words(page_unique_words):
    write_words = []
    
    for word in page_unique_words:
        if word not in total_unquie_words:
            # put unque words from page in overall unquie word list
                total_unquie_words.append(word)
                if (len(word) <= options['max_char'] or options['max_char'] == 0 ): 
                    write_words.append(word)
                
    write_words = sorted(set(write_words))       
    message_to_screen(6, 'Unquie words found in page not encounter previously')
    for word in write_words:
        message_to_screen(3, word)
                       
    if options['file_name']:
        message_to_screen(6,'writing to file %s.lst' % options['file_name'])
        min_word_lenght = 1
        with open(options['file_name']+'.lst', "a") as word_file:
            for word in write_words:
                word_lenght = len(word.encode('utf-8').decode('ascii', 'ignore'))
                if  (word_lenght > min_word_lenght) or (word_lenght == 0):
                    word_file.write(word.encode('utf-8')+'\n\r') 
    return

def unique_sentances(page_sentance_list):
    write_sentances = []
    for sentance in page_sentance_list:
        rm_sent = LineTokenizer(blanklines='discard').tokenize(sentance)
        sentance = ''.join(rm_sent)
        if sentance not in total_unquie_sentances:
            total_unquie_sentances.append(sentance)
            write_sentances.append(sentance)
            
    write_sentances = sorted(set(write_sentances))       
    message_to_screen(6, 'Unquie sentances found in page not encounter previously')
    for sentance in write_sentances:
        sentance = sentance.encode('utf-8')
        message_to_screen(3, sentance)
        
        if options['file_name']:       
            with open(options['file_name']+'-sent.lst', "a") as sentence_file:
                for sentence in write_sentances:
                    sentence_file.write(sentence+'\n\r') 
    return
     
def lexical_diversity(text):
    return len(text) / len(set(text))

def word_pairs():
    
    # Collocations are expressions of multiple words which commonly co-occur
    # While these words are highly collocated, the expressions are also very infrequent.

    tokens = nltk.wordpunct_tokenize(total_text)
    bi_grm = nltk.collocations.BigramAssocMeasures()
    bi_finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)

    # remove stuff
    stopset = set(nltk.corpus.stopwords.words('english'))
    filter_set2 = lambda word: word in stopset
    bi_finder.apply_word_filter(filter_set)
    bi_finder.apply_word_filter(filter_set2)
                                
    # only grams that appear 3+ times
    #bi_finder.apply_freq_filter(3)
    
    scored = bi_finder.score_ngrams( bi_grm.likelihood_ratio  )

    # Group bigrams by first word in bigram.                                        
    prefix_keys = collections.defaultdict(list)

    for key, scores in scored:
        prefix_keys[key[0]].append((key[1], scores))

        # Sort keyed bigrams by strongest association.                                  
        for key in prefix_keys:
            prefix_keys[key].sort(key = lambda x: -x[1])
        
    message_to_screen(6, 'Word pairing found in text')
    for key in prefix_keys:
        str_ngram =''
        for word_pairs in prefix_keys[key]:
            str_ngram = key.encode('utf-8') + word_pairs[0].encode('utf-8')
            
            if (len(str_ngram) <= options['max_char'] or options['max_char'] == 0 ): 
                message_to_screen(3, str_ngram)
                
                if options['file_name']:       
                    with open(options['file_name']+'-pair.lst', "a") as pair_file:
                        pair_file.write(str_ngram+'\n\r') 

def bi_pmi():
    # Collocations are expressions of multiple words which commonly co-occur
    # While these words are highly collocated, the expressions are also very infrequent.
    # Therefore it is useful to apply filters, such as ignoring 
    # all bigrams which occur less than three times
    
    tokens = nltk.wordpunct_tokenize(total_text)
    bi_grm = nltk.collocations.BigramAssocMeasures()
    bi_finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)

    # remove stuff
    bi_finder.apply_word_filter(filter_set)
                                
    # only grams that appear 3+ times
    bi_finder.apply_freq_filter(3)
    
    # return the 100 n-grams with the highest PMI
    top_bi_pmi = bi_finder.nbest(bi_grm.pmi, 1000)
    
    top_bi_pmi_str =[]
    for pmi in top_bi_pmi:
        str_ngram = ''
        for word in pmi:
            str_ngram = str_ngram + word.encode('utf-8')
        
        if (len(str_ngram) <= options['max_char'] or options['max_char'] == 0 ):    
            top_bi_pmi_str.append(str_ngram)
        
    message_to_screen(6, 'Word pmi pairing found in text')
    for pair in top_bi_pmi_str:
        message_to_screen(3, pair)    
        if options['file_name']:       
            with open(options['file_name']+'-bi.lst', "a") as pair_file:
                pair_file.write(pair+'\n\r')

    return

def tri_words():
    # Collocations are expressions of multiple words which commonly co-occur
    # While these words are highly collocated, the expressions are also very infrequent.
    # Therefore it is useful to apply filters, such as ignoring 
    # all bigrams which occur less than three times
    
    tokens = nltk.wordpunct_tokenize(total_text)
    tri_grm = nltk.collocations.TrigramAssocMeasures()
    tri_finder = nltk.collocations.TrigramCollocationFinder.from_words(tokens)
    
    #filter out stuff
    tri_finder.apply_word_filter(filter_set)
    
    # only grams that appear 3+ times
    tri_finder.apply_freq_filter(3)
    
    # return the 100 n-grams with the highest ratio
    top_tri = tri_finder.nbest(tri_grm.likelihood_ratio, 1000)
    
    top_tri_str =[]
    for tri in top_tri:
        str_ngram = ''
        for word in tri:
            str_ngram = str_ngram + word.encode('utf-8')
        
        if (len(str_ngram) <= options['max_char'] or options['max_char'] == 0 ):    
            top_tri_str.append(str_ngram)
        
    message_to_screen(6, 'Tri Words pairing found in text')
    for tri in top_tri_str:
        message_to_screen(3, tri) 
        if options['file_name']:       
            with open(options['file_name']+'-tri.lst', "a") as tri_word_file:
                tri_word_file.write(tri +'\n\r')

    return  

def tagged_words():
    tokens = nltk.wordpunct_tokenize(total_text)
    tagged_words = nltk.pos_tag(tokens)
    return tagged_words

def download(url):
    # code from stack overflow
    # http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
    print url
    parse = urlparse(url)
    file_name = parse[2].split('/')[-1]
    full_path = options['download_directory']+'/'+file_name
    
    print file_name
    
    try:
        open_url = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        message_to_screen(5, e.code)
        message_to_screen(6, e.read())
        return 
        
    info_open_url = open_url.info()
    try:
        totalSize = int(info_open_url["Content-Length"])
    except:
        return
        
    try:
        with open(full_path): pass
        return
    except IOError:
        pass
    
    print "Downloading %s bytes..." % totalSize,
    fp = open(full_path, 'wb')

    blockSize = 8192 #100000 # urllib.urlretrieve uses 8192
    count = 0
    while True:
        chunk = u.read(blockSize)
        if not chunk: break
        fp.write(chunk)
        count += 1
        if totalSize > 0:
            percent = int(count * blockSize * 100 / totalSize)
            if percent > 100: percent = 100
            print "%2d%%" % percent,
            if percent < 100:
                print "\b\b\b\b\b",  # Erase "NN% "
            else:
                print "Done."

    fp.flush()
    fp.close()
    if not totalSize:
        print
    
    #metadata_media(full_path)
    return

def metadata_media(filename):
    
    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    
    if not parser:
        print "Unable to parse file"
        return
    
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "Metadata extraction error: %s" % unicode(err)
        metadata = None
        
    if not metadata:
        print "Unable to extract metadata"
        return

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    
    for line in text:
        print makePrintable(line, charset)
        
    return
    
def gramma_rules_words(rules_list):
    
    phrase_list = []
    tag_word_list = {}
    for rule_mask in rules_list:
        message_to_screen(6, 'Gramma rule combinations found in total unique text for mask'), rule_mask
        mask_slot = []
        slot = 0
        for tag in rule_mask:
            # set the first two list agruments 0 is total num words 1 will be list pointer
            mask_slot.append([0,2])
            if tag in tag_word_list:
                mask_slot[slot].extend(sorted(tag_word_list[tag], key=len))
            else:
                tag_word_list[tag] = []
                for word in total_tagged_words:
                    if word[1] == tag:
                        tag_word_list[tag].append(word[0])
                mask_slot[slot].extend(sorted(tag_word_list[tag], key=len))
            mask_slot[slot][0] = len(mask_slot[slot])-2
            slot = slot + 1
            
        for slot in mask_slot:
            # check if any words in list 0 means no words
            message_to_screen(6,'number of matches'), slot[0]
            if slot[0] == 0 :
                mask_slot[0][1] = mask_slot[0][0] + 2
        
        while mask_slot[0][1]+2 <= mask_slot[0][0]:
            phrase = ''
            number_slots = range(len(rule_mask))
            rev_slots = reversed(range(1, len(rule_mask)))
                                  
            for slot in number_slots :
                #print 'slot %s' % slot
                list_pointer = mask_slot[slot][1]
                #print 'list pointer %s' % list_pointer
                word = mask_slot[slot][list_pointer]
                phrase = phrase + word.encode('utf-8')
                
                #print phrase, len(phrase)
                if (len(phrase) > options['max_char']) and (options['max_char'] != 0 ):
                    if slot != number_slots[-1]:
                        rev_slot = reversed(range(slot + 1, len(rule_mask)))
                        for slot in rev_slot:
                            mask_slot[slot][1] = mask_slot[slot][0]
                            
                if slot == number_slots[-1]:
                    mask_slot[slot][1] = mask_slot[slot][1] + 1
                    for slot in rev_slots :
                        if mask_slot[slot][1] > mask_slot[slot][0]:
                            mask_slot[slot][1] = 2
                            mask_slot[slot-1][1] =  mask_slot[slot-1][1] + 1
                           
            if (len(phrase) <= options['max_char'] or options['max_char'] == 0 ):
                if phrase not in phrase_list:
                    phrase_list.append(phrase)
                    message_to_screen(3, phrase) 
                    if options['file_name']:       
                        with open(options['file_name']+'-gramma.lst', "a") as gramma_word_file:
                            gramma_word_file.write(phrase +'\n\r')
    
    #message_to_screen(6, 'Gramma rule combinations found in total unique text')    
    return
    
##### START OF MAIN CODE BLOCK #####
if __name__ == "__main__":
    
    global total_unquie_words
    global total_tagged_words
    global total_unquie_sentances
    global total_text
    global filter_set
    global schar_set
    
    signal.signal(signal.SIGINT, signal_handler)
    
    options = command_line_options()
    
    if not options['no_proxy']:
        # Set proxy
        message_to_screen(5, 'User local Tor')
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
    
    link_list = []
    unquie_url = []
    unquie_file_url = []
    unquie_doc_url = []
    unquie_image_url = []
    total_unquie_words = []
    total_tagged_words = []
    total_unquie_sentances = []
    total_text = ''
    
    # default filter set
    schar_set = ( '"', '`', '.', ',', '\\', '/', '*', '@', '#', '[', ']' '(', ')', ':', ';', '-', '_', '&', '^', '$', '!', '<', '>', '?' )
    filter_set = lambda word: word in schar_set
    
    if options['tagger'] == 'sb':
    # default gramma rules using pos simplifed brown pos
        default_rules = [['EX', 'MOD', 'V', 'DET', 'PRO'], ['VD', 'ADJ', 'N'],['NP', 'V', 'ADJ', 'ADV'],['PRO', 'NP', 'V', 'ADJ', 'ADV']]
    else:
    # Default gramma rules using ntlk default pos tree bank
        default_rules = [['EX', 'MD', 'VB', 'DT', 'PRP'], ['VB', 'JJ', 'NN'],['NNP', 'VB', 'JJ', 'ADV'],['PRO', 'NNP', 'VB', 'JJ', 'ADV']]
#
#   Assign the start url to start_link 0
    start_link = crawl_link(options['url'], 'html', 'loc', 0)
    link_list.append(start_link)
    
    if not os.path.exists(options['download_directory']):
        try:
            os.makedirs(options['download_directory'])
        except IOError:
            pass

    for link in link_list:
        if link.depth > options['depth']:
            link_list.remove(link)
        else:
            if (options['ex_ln'] == False ) and (link.loc_ex =='ex'):
                link_list.remove(link)
            else:
                message_to_screen(4, link.url)
                page = url_content(link)
                link_list.remove(link)         
            ## total text ###
                total_text = total_text + page.text
            # tagged words
                unique_tagged_words(page.tagged_words)
                
            ### write or display data ###
            
            # Words
                if options['words_flag'] :
                    unique_words(page.unique_words)

            # Sentances
                if options['phrase_flag'] :
                    unique_sentances(page.sentance_list)

                # add the links from the page to the list of links
                for new_link in page.links:
                    #print new_link.type, new_link.url
                    if (new_link.type == 'html') and (new_link.url not in unquie_url):
                        unquie_url.append(new_link.url)   
                        link_list.append(new_link)
                    elif (new_link.type == 'image') and (new_link.url not in unquie_image_url):
                        unquie_image_url.append(new_link.url)
                        if options['download_images'] : download(new_link.url)
                    elif (new_link.type == 'doc') and (new_link.url not in unquie_doc_url):
                        unquie_doc_url.append(new_link.url)
                        if options['download_docs'] : download(new_link.url)   
                    elif (new_link.type == 'file') and (new_link.url not in unquie_file_url):
                        unquie_file_url.append(new_link.url)
                        if options['download_files'] : download(new_link.url)
                    
    ### play with totals ###
    
    if options['pair_flag'] :
        word_pairs()
    
    if options['bi_flag'] :
        bi_pmi()
    
    if options['tri_flag'] :    
        tri_words()
        
    if options['gramma_flag'] :
        gramma_rules_words(default_rules)        
    
    message_to_screen(5, 'end of program')
    
