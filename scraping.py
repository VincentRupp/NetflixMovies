# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 11:50:59 2015

@author: Vincent
"""
#Get all the film titles on 
generic = 'http://www.allflicks.net/wp-content/themes/responsive/processing/processing_us.php'
#specifics = '?category=Action%20%26%20Adventure&movies=true&shows=false&min=0&max=100'
specifics = '?movies=true&shows=false&min=0&max=10000'

link = generic + specifics

import urllib,json
#url = link
response=urllib.urlopen(link)
films = json.loads(response.read())
#print films
#films["data"][1]["title"] #this returns the second title

netflix_titles = []
netflix_info = []

#UnicodeEncodeError fix:
#unicodeData.encode('ascii', 'ignore')

for film in films["data"]:
#    print film["title"]
    #titles += [str(film["title"])]
    netflix_titles += [str(film["title"].encode('ascii','ignore'))]
    netflix_info += [(str(film["title"].encode('ascii','ignore')),film["year"].encode('ascii','ignore'))]

#output the list of titles so I don't have to grab it again
#write_path = 'E:\Netflix Movies\\'
write_path = 'C:\Other Projects\Netflix Movies\\'
write_file = "titles.csv"
f = write_path+write_file

with open(f, 'w+') as my_file:
    my_file.write('\n'.join(netflix_titles))

#Read back in the csv file:
netflix_titles = [line.rstrip('\n') for line in open(f)]

#set up RT api package
from rottentomatoes import RT
rt = RT('4cbst6rnnvresrd9e8q83hhs')

#just testing how RT's API works
fight_clubs = rt.search('101 dalmations')
for club in fight_clubs:
    print "title="+club["title"]+" & ID="+club["id"] + " & released="+str(club["year"])
    print "Critics' Score: "+str(club["ratings"]["critics_score"])
    print "Audience Score: "+str(club["ratings"]["audience_score"])
    if club["title"] in netflix_titles:
        print "On Netflix!"

#scrape http://www.rottentomatoes.com/top/bestofrt/?year=2012 for best movies

from lxml import html
import requests

#let's scrape the top 100 movies from 2008 - present
top_movies = []
for i in range(10,15):
    link = 'http://www.rottentomatoes.com/top/bestofrt/?year=20'
    link = link + str(i)
    page = requests.get(link)
    tree = html.fromstring(page.text)
    top_list = tree.xpath('//tr[@class="" or @class="alt_row"]//a[@class=""]/text()')
    for movie in top_list:
        top_movies += [(movie,'20'+str(i))]

#Get rid of the trailing year values in the titles:
top_movies = [(title[0:-7],year) for (title,year) in top_movies]

#find the top-500 titles that are on Netflix
top_titles = []
for title,year in top_movies:
    if title in netflix_titles:
        top_titles += [title]


#create a list of those top 500 that are on netflix
v = [(movie,year) for movie,year in netflix_info if (movie,year) in top_movies]
v += [(movie,year) for movie,year in netflix_info if (movie,str(int(year)-1)) in top_movies]
v += [(movie,year) for movie,year in netflix_info if (movie,str(int(year)+1)) in top_movies]

#this list is just the titles, which is also useful apparently
v2 = [title for title,year in v]

missing = [movie for movie in top_titles if movie not in v2]

#count movies on netflix in the top 500 by year
b3 = [year for title,year in v]
b4 = set(b3)
for year in b4:
    print str(year) + ': ' + str(b3.count(year))

#look at just 2014 for some reason    
print [(title,year) for title,year in v if year=='2014']

#Look up Netflix movies on RT and compare ratings
#need yet another list for this, it turns out, so go back to original JSON return
c_info = []
for film in films["data"]:
    c_info += [(str(film["title"].encode('ascii','ignore')),film["year"].encode('ascii','ignore'),film["rating"].encode('ascii','ignore'),film["category"].encode('ascii','ignore'))]

test_info = c_info[5266:]
#get RT info for all search results for netflix movies

from time import sleep

#define tuple to contain all the info we want in the average netflix rating:
#0 title
#1 netflix year
#2 netflix rating
#3 netflix category
#4 RT year
#5 RT audience score
together = []
gotten = 5265
for title,n_year,n_rating,category in test_info:
    sleep(0.1)    
    gotten += 1
    s_result = rt.search(title)
    print "%s: Searching now for %s" % (gotten,title)
    for film in s_result:
        p_year = film["year"]
        if film["year"]=='':
            p_year=0
            #print "The movie without a year is %s" % (film["title"])
        if (title==film["title"] and int(n_year)-1<=int(p_year)<=int(n_year)+1):
            #print title + " has an audience rating of " + str(film["ratings"]["audience_score"])
            together += [(title,n_year,n_rating,category,p_year,film["ratings"]["audience_score"])]

together_0_996 = together
together_997_1648 = together  #this and the next one have duplicates because of math
together_1648_3082 = together
together_3083_3581 = together
together_3582_5265 = together
together_5266_end = together

together=[]
together += together_0_996
together += together_997_1648
together += together_1648_3082
together += together_3083_3581
together += together_5266_end

#okay that was tedious and I accidentally grabbed a bunch of duplicates
together_nodupes = []
for t,y,r,c,p,s in together:
    if (t,y,r,c,p,s) not in together_nodupes:
        together_nodupes += [(t,y,r,c,p,s)]

len(together_nodupes)

netflix_matching = []
for film in films["data"]:
    netflix_matching += [(str(film["title"].encode('ascii','ignore')),film["year"].encode('ascii','ignore'),film["rating"].encode('ascii','ignore'))]

matched_titles = [(title,y,r) for title,y,r,c,p,s in together_nodupes]
unmatched_titles = []
for title,y,r in netflix_matching:
    if (title,y,r) not in matched_titles:
        unmatched_titles += [(title,y,r)]

#still too many, 6113 vs. 5993
#how did that even happen
len(matched_titles) + len(unmatched_titles)
    
from collections import Counter
x = Counter(matched_titles)
#turns out that 106 movies are repeated

uncredible = []
for item in x.most_common(106):
    uncredible += [item[0][0]]
    
#now take these movies out of the netflix_matching and out of together_nodupes
#then recalculate 
credible_nm = [(title,y,r) for title,y,r in netflix_matching if title not in uncredible]  
credible_together_nd = [(title,y,r,c,p,s) for title,y,r,c,p,s in together_nodupes if title not in uncredible]  

matched_titles_cred = [(title,y,r) for title,y,r,c,p,s in credible_together_nd]
unmatched_titles_cred = []
for title,y,r in credible_nm:
    if (title,y,r) not in matched_titles_cred:
        unmatched_titles_cred += [(title,y,r)]

print len(matched_titles_cred)
print len(unmatched_titles_cred)

import numpy

#compare netflix ratings for matched and unmatched
matched_mean = numpy.mean([float(n_rating) for title,year,n_rating in matched_titles_cred])
matched_sd = numpy.std([float(n_rating) for title,year,n_rating in matched_titles_cred])
unmatched_mean = numpy.mean([float(n_rating) for title,year,n_rating in unmatched_titles_cred])
unmatched_sd = numpy.std([float(n_rating) for title,year,n_rating in unmatched_titles_cred])

#now get the RT ratings for the matched set and calculate the average
matched_rt_mean = numpy.mean([float(s) for title,y,r,c,p,s in credible_together_nd])

categories = set([c for t,y,r,c,p,s in credible_together_nd])
for c in categories:
    count = numpy.count_nonzero([n_rating for title,y,n_rating,cat,p,rt_rating in credible_together_nd if c==cat])
    n_mean = round(numpy.mean([float(n_rating) for title,y,n_rating,cat,p,rt_rating in credible_together_nd if c==cat]),3)
    rt_mean = round(numpy.mean([float(rt_rating) for title,y,n_rating,cat,p,rt_rating in credible_together_nd if c==cat]),2)
    print c,count,n_mean,rt_mean

year_mean = numpy.mean([float(year) for title,year,n_rating in matched_titles_cred])
year_sd = numpy.std([float(year) for title,year,n_rating in matched_titles_cred])

numpy.histogram([float(year) for title,year,n_rating in matched_titles_cred],range(1900,2030,10))

numpy.histogram([float(rt_rating) for title,y,n_rating,cat,p,rt_rating in credible_together_nd],range(0,105,5))

#output the 'together' list so I never have to run that code again:
#write_path = 'E:\Netflix Movies\\'
write_path = 'C:\Other Projects\Netflix Movies\\'
write_file = "together_ltcomma.csv"
f = write_path+write_file

with open(f, 'w+') as my_file:
    my_file.write('\n'.join('%s<,%s<,%s<,%s<,%s<,%s' % x for x in together))




#just some code to do regex
#import re
#for item in top_:
#    if re.search("Crazy",item):
#        print item

