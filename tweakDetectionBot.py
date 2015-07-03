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

def findTitle(txt):
    txt=txt.replace("+/u/","")
    re1='^'+username+' (.*)'
    rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        word1=m.group(1)
        return word1
    else:
        return "ERROR"
def checkType(link):
    print link
    response = requests.post(link)
    soup = BeautifulSoup(response.text)
    tag= soup.find(id="section")
    try:
        type = str(tag.string)
    except:
        return False
    if type == "Tweaks":
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
            descrip = str(item[ "description" ])
            link = "http://cydia.saurik.com/package/" + link.replace("http://planet-iphones.com/cydia/id/", "")
            if checkType(link):
                response = requests.post(link)
                soup = BeautifulSoup(response.text)
                link= soup.iframe['src']
                print link
                print descrip
                return link, descrip
            else:
                "bad type"
        else:
            print "bad title"
while True:
    print "checking"
    messages = r.get_unread('mentions')
    for message in messages:
        obj = open('seen_posts.txt', 'ab+')
        try:
            submission= message.submission
            title = submission.title
            if str(submission.subreddit).lower()=="jailbreak":
                jailbreak=True
            else:
                jailbreak=False
        except:
            jailbreak=False
        if message.id not in open("seen_posts.txt").read() and jailbreak:
            print "checking name.."
            text = message.body
            words = findTitle(text)
            try:
                link, descrip = getTweak(words.lower())
                message.reply("The following is short description and link to the tweak: \n\n Title: [" + words +"](" + link + ") \n\nDescription: " + descrip + " \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on it's accuracy")
                print "Found post and commented, link: " + submission.permalink
            except:
                print traceback.format_exc()
                print "\n\n"
                print "Tweak not found " + str(words)
        else:
            if message.id in open("seen_posts.txt").read():
                print "Already seen"
            print "Does not meet qualifications"
        message.mark_as_read()
        obj.write(message.id)
        obj.close()
    print "Check done"
    time.sleep(5)
