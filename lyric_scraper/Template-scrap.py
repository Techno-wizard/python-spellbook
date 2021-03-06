#!/usr/bin/python2.7
# 7 9 2012
# v 0.1

import sys
import mechanize
import cookielib
import urllib2
from BeautifulSoup import BeautifulSoup
import nltk
from nltk.tokenize import *
import socks
import socket
    
def create_connection(address, timeout=None, source_address=None):
        sock = socks.socksocket()
        sock.connect(address)
        return sock

def clean_page_azlyrics(pre_processed_page):

    pre_processed_page = pre_processed_page.replace('<br />','\n')
    pre_processed_page = pre_processed_page.replace('<div style="margin-left:10px;margin-right:10px;">','')
    pre_processed_page = pre_processed_page.replace('</div>','')
    pre_processed_page = pre_processed_page.replace('<i>','')
    pre_processed_page = pre_processed_page.replace('</i>','')
    pre_processed_page = pre_processed_page.replace('[8x]','')
    pre_processed_page = pre_processed_page.replace('[4x]','')
    pre_processed_page = pre_processed_page.replace('[?]','')
    
    lyrics_sent_tokens = LineTokenizer(blanklines='discard').tokenize(pre_processed_page)
     
    return lyrics_sent_tokens

def search_lyrics(query):

    # Set proxy
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    
    # patch the socket module
    socket.socket = socks.socksocket
    #socket.create_connection = create_connection
    
    br = mechanize.Browser()
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(False)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),max_time=1)

    # Want debugging messages?
    br.set_debug_http(False)
    br.set_debug_redirects(False)
    br.set_debug_responses(False)

    br.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 7.0b;Windows NT 5.1)')]
    br.clear_history()

#   sit to get to is http://www.azlyrics.com/
    url_prexif = "http://"
    Site_Name = 'www.azlyrics.com/'

    full_url = url_prexif + Site_Name

    try:    
        br.open(full_url)
    except IOError: 
        print 'Failure to open site' #Handle failure 
        sys.exit(0)
        
    # List the forms that are in the page
    #print 'list forms'
    #for form in br.forms():
    #print "Form name:", form.name
    #print form

    br.select_form(nr=0)
    br['q'] = query

# submit it 
    br.submit()

# get full list of possible urls    
    responce = BeautifulSoup(br.response().read())
        
    lyrics = []    
    for block in responce.findAll('div',{'class':'sen'}):
        link = block.find('a',href=True)
        page = BeautifulSoup(urllib2.urlopen(link['href']))
        pre_processed_page = (str(page.find('div',{'style':'margin-left:10px;margin-right:10px;'})))
        processed_page = clean_page_azlyrics(pre_processed_page)
        lyrics.append(processed_page)
    if(lyrics == None):
        lyrics = 'Lyrics not found'
        
    return lyrics

