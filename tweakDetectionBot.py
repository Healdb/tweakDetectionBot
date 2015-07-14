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
        type = str(tag.string)
    except:
        return False
    if type == "Tweaks" or type=="Addons":
        return True
    return False
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
            soup = BeautifulSoup(response.text)
            descrip= soup.find("div", { "class" : "package_description" }).text
            link = "http://cydia.saurik.com/package/" + link.replace("http://planet-iphones.com/cydia/id/", "")
            if checkType(link):
                response = requests.post(link)
                soup = BeautifulSoup(response.text)
                link= soup.iframe['src']
                print link
                print descrip
                return link, descrip
            else:
                print "bad type"
        else:
            print "bad title"
    return False,"error"
def assembleSuggestions(packageName):
    testName = packageName.replace(" ","+")
    link = "http://planet-iphones.com/cydia/feed/name/" + testName
    response = requests.post(link)
    feed = feedparser.parse( response.text )
    c=0
    text="Tweak not found! Did you mean...\n\n "
    for item in feed[ "items" ]:
        if c>3:
            break
        title = item[ "title" ]
        text = text + "* "+title.lower()+"\n\n "
        c+=1
    return text
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
            link, descrip = getTweak(words.lower())
            if link==False:
                print traceback.format_exc()
                print "\n\n"
                print "tweak not found " + str(words)
                text = assembleSuggestions(words)
                message.reply(text)
            else:
                message.reply("The following is short description and link for the tweak you requested: \n\n Title: [" + words +"](" + link + ") \n\nDescription: " + descrip + " \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on it's accuracy.")
                print "Found post and commented, link: " + submission.permalink
        else:
            print "not met"
        message.mark_as_read()
    print "check done"
    time.sleep(5)
