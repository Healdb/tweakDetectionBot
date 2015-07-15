import requests
import feedparser
import time
import praw
from bs4 import BeautifulSoup
import re
import traceback

r = praw.Reddit('/r/jailbreak package description provider')
username="USERNAME"
password="PASSWORD"
#I think that this authentication method is being depreciated, it'll probably have to be changed soon
r.login(username,password)
botName=username
def findTitle(txt):
    txt=txt.replace("+/u/","")
    re1=''+botName+'\s\[(.*)\]'
    rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        word1=m.group(1)
        print word1
        return word1
def checkType(link):
    response = requests.post(link)
    soup = BeautifulSoup(response.text)
    tag= soup.find(id="section")
    try:
        typet = str(tag.string)
    except:
        return False
    return typet
def getTweak(packageName):
    testName = packageName.replace(" ","+")
    link = "http://planet-iphones.com/cydia/feed/name/" + testName
    response = requests.post(link)
    feed = feedparser.parse( response.text )
    for item in feed[ "items" ]:
        title = item[ "title" ]
        if title.lower() == packageName:
            link = str(item[ "link" ])
            response = requests.post(link)
            soup = BeautifulSoup(response.text, "html.parser")
            descrip= soup.find("div", { "class" : "package_description" }).text
            link = "http://cydia.saurik.com/package/" + link.replace("http://planet-iphones.com/cydia/id/", "")
            typet= checkType(link)
            print link
            print descrip
            return link, descrip,typet
    return False,"error","error"
def assembleSuggestions(packageName):
    testName = packageName.replace(" ","+")
    link = "http://planet-iphones.com/cydia/feed/name/" + testName
    response = requests.post(link)
    feed = feedparser.parse( response.text )
    names=[]
    links=[]
    for item in feed[ "items" ]:
        title = item[ "title" ]
        link = item["link"]
        names.append(title)
        links.append(link)
    shortest=0
    shortName=""
    c=0
    for link in links:
        response = requests.post(link)
        soup = BeautifulSoup(response.text, "html.parser")
        half= soup.iframe['src']
        link = "http://planet-iphones.com"+half
        response = requests.post(link)
        soup = BeautifulSoup(response.text, "html.parser")
        descrip= soup.find("div", class_="ratingText").text
        re1='\((\w+)'
        rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
        m = rg.search(descrip)
        #Chooses most likely package by its popularity
        if m:
            int1=m.group(1)
            if int1>shortest:
                shortest=int1
                shortName=names[c]
        c+=1
    return shortName
def checkSpaces(words):
    c=1
    for char in words:
        words = words[:c] + ' ' + words[c:]
        twords= words.replace(" ","+")
        link = "http://planet-iphones.com/cydia/feed/name/" + twords
        response = requests.post(link)
        feed = feedparser.parse( response.text )
        if feed[ "items" ]==[]:
            words = words.replace(" ","")
            pass
        else:
            return assembleSuggestions(words)
        c+=1
while True:
    print "checking"
    messages = r.get_unread('mentions')
    for message in messages:
        print message.body
        try:
            submission= message.submission
            title = submission.title
            if str(submission.subreddit).lower()=="jailbreak":
                jailbreak=True
            else:
                jailbreak=False
        except:
            print traceback.format_exc()
            jailbreak=False
        if jailbreak:
            print "checking name.."
            text = message.body
            words = findTitle(text)
            permWords=words
            try:
                link, descrip,typet= getTweak(words.lower())
            except:
                message.mark_as_read()
                break
            if link==False:
                words = assembleSuggestions(words)
                link, descrip,typet= getTweak(words.lower())
                try:
                    text = "Tweak not found, the following is the closest match: \n\n Title: [" + words +"](" + link + ")\n\nCategory: "+str(typet)+" \n\nDescription: " + descrip + " \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on it's accuracy."
                    message.reply(text)
                    print "Close Match"
                except:
                    try:
                        words=checkSpaces(permWords.lower())
                        link, descrip,typet= getTweak(words.lower())
                        text = "Tweak not found, the following is the closest match: \n\n Title: [" + words +"](" + link + ")\n\nCategory: "+str(typet)+" \n\nDescription: " + descrip + " \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on it's accuracy."
                        message.reply(text)
                        print "Close Match"
                    except:
                        print "No Match"
                        message.reply("Tweak not found, and there are no close matches. You may have spelled the name incorrectly. \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on it's accuracy.")
            else:
                message.reply("The following is short description and link for the tweak you requested: \n\n Title: [" + words +"](" + link + ")\n\nCategory: "+str(typet)+" \n\nDescription: " + descrip + " \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on it's accuracy.")
                print "Found post and commented, link: " + submission.permalink
        else:
            print "not met"
        message.mark_as_read()
    print "check done"
    time.sleep(5)
