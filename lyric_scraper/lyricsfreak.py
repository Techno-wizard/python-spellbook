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
# To set proxy
import socks
import socket

def clean_page_lyricsfreak(pre_processed_page):
    pre_processed_page = pre_processed_page.replace('<br />','\n')
    pre_processed_page = pre_processed_page.replace('<div id="content_h" class="dn">','')
    pre_processed_page = pre_processed_page.replace('</div>','')
    pre_processed_page = pre_processed_page.replace('&amp;','&')
    pre_processed_page = pre_processed_page.lstrip(' ')
    pre_processed_page = pre_processed_page.replace('(x5)','')
    pre_processed_page = pre_processed_page.replace('(x4)','')
    pre_processed_page = pre_processed_page.replace('(x3)','')
    pre_processed_page = pre_processed_page.replace('(x2)','')
    pre_processed_page = pre_processed_page.replace('','')

    lyrics_sent_tokens = LineTokenizer(blanklines='discard').tokenize(pre_processed_page)
    
    return lyrics_sent_tokens

def search_lyrics(query):
    
    # Set proxy
    #socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    #socket.socket = socks.socksocket
    
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

#   sit to get to is http://www.lyricsfreak.com/
    url_prexif = "http://"
    Site_Name = 'www.lyricsfreak.com/'

    full_url = url_prexif + Site_Name

    try:    
        br.open(full_url)
    except IOError: 
        print 'Failure to open site' #Handle failure 
        sys.exit(0)

    br.select_form(nr=0)
    br['q'] = query

# submit it 
    br.submit()
# get full list of possible urls    
    responce = BeautifulSoup(br.response().read())
    table =  responce.findAll('table')[1]

    lyrics = []
    for link in table.findAll('a', href=True, attrs={'class':'song'}):   
        page = BeautifulSoup(urllib2.urlopen(link['href']))
        pre_processed_page = (str(page.find('div',{'id':'content_h'})))
        processed_page = clean_page_lyricsfreak(pre_processed_page)
        lyrics.append(processed_page)
        
    if(lyrics == None):
        lyrics = 'Lyrics not found'
        
    return lyrics