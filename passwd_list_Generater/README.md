This code is poc.

The concepts used are still being evaluated.

The grammar section comes from this paper, the rest are idea's i am trying.

http://www.cs.cmu.edu/~agrao/paper/Effect_of_Grammar_on_Security_of_Long_Passwords.pdf

There is no help other than google or possible irc.

The code assume installed and working tor proxy.

There are severay python modual used the main ones being 

nltk
http://nltk.org/

beautifulsoup
http://en.wikipedia.org/wiki/Beautiful_Soup

socket
http://docs.python.org/2/library/socket.html

urllib2
http://docs.python.org/2/library/urllib2.html

collections
http://docs.python.org/2/library/collections.html


This code crawls web pages from a starting url, on each page attems to extract words, sentances.
It will then attempt to perform variuos analys of the word or sentances. 
Generating word lists from these outputs.


command line options

-u		--url	Web crawl starting url.
-ex		--external_links	Weather of not to follow external links found in a web page.
-d		--depth_of_links	Depth of links to follow 
-f		--file_name	Root file name for lists if an option is choosen an extersion is add.
-m		--max_char	Maximum length of characters to add to list
-lc		--lower_case	Flag for lower case all text
-wl		--words_flag	Flag for word list
-ph		--phrase_flag	Flag for phrase list
-pl		--pair_flag	Flag for pair list
-bl		--bi_flag	Flag for bi word list
-tl		--tri_flag	Flag for  tri word list
-gl		--gramma_flag	Flag for  gramma rule word list
-np		--no_socks_proxy	Do not use local Tor socks proxy
-v		--verbosity	How much to display on screen 0 - 10 (default 5)



