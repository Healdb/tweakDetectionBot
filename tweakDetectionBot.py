import requests
import feedparser
import time
import praw
from bs4 import BeautifulSoup
import re
import traceback

#r = praw.Reddit('/r/jailbreak package description provider')
#ND - It's always good to include a version number and your username to uniqueness

botName=""
password=""
version=0.0.5
#I think that this authentication method is being depreciated, it'll probably have to be changed soon

try:
    import creds
    # This is a py file in my python library which contains the
    # bot's username and password.
    # Now you can easily push code without worrying about showing creds
    botName = creds.botName
    password = creds.password
    print "Successfully imported username and password from 'creds' library"
except ImportError:
    pass


r = praw.Reddit('/r/jailbreak package description provider by Healdb. v' + version)
r.login(botName,password)
print "Logged into reddit"

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
    response = requests.get(link)
    soup = BeautifulSoup(response.text)
    tag= soup.find(id="section")
    try:
        typet = str(tag.string)
    except:
        return False
    return typet
def getTweak(packageName):
    testName = packageName.replace(" ","+")
    link = "http://planet-iphones.com/cydia/feed/homepage/" + testName
    response = requests.get(link)
    feed = feedparser.parse( response.text )
    if feed[ "items" ]==[]:
        link = "http://planet-iphones.com/cydia/feed/nameanddescription/" + testName
        response = requests.get(link)
        feed = feedparser.parse( response.text )
    for item in feed[ "items" ]:
        title = item[ "title" ]
        if title.lower() == packageName:
            link = str(item[ "link" ])
            response = requests.get(link)
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
    link = "http://planet-iphones.com/cydia/feed/homepage/" + testName
    response = requests.get(link)
    feed = feedparser.parse( response.text )
    if feed[ "items" ]==[]:
        link = "http://planet-iphones.com/cydia/feed/nameanddescription/" + testName
        response = requests.get(link)
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
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        descrip= soup.find("div", class_="ratingText").text
        re1='\((\w+)'
        rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
        m = rg.search(descrip)
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
        link = "http://planet-iphones.com/cydia/feed/homepage/" + twords
        response = requests.get(link)
        feed = feedparser.parse( response.text )
        if feed[ "items" ]==[]:
            words = words.replace(" ","")
            pass
        else:
            return assembleSuggestions(words)
        c+=1
while True:
    try:
        print "Checking inbox"
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
                print "Checking username mention for flag"
                text = message.body
                words = findTitle(text)
                pwords=words
                try:
                    link, descrip,typet= getTweak(words.lower())
                except:
                    message.mark_as_read()
                    break
                if link==False:
                    words = assembleSuggestions(words)
                    link, descrip,typet= getTweak(words.lower())
                    try:
                        text = "Tweak not found, the following is the closest match: \n\n _________________________ \n\n Title: [" + words +"](" + link + ")\n\nCategory: "+str(typet)+" \n\nDescription: " + descrip + " \n\n _________________________ \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on its accuracy. [Source Code](https://github.com/Healdb/tweakDetectionBot)"
                        if private: #ND - 'private' is never set to true, so it will never be triggered
                            r.send_message(author.name,"Private Explanation",text)
                        else:
                            message.reply(text)
                        print "Close Match"
                    except:
                        try:
                            words=checkSpaces(pwords.lower())
                            link, descrip,typet= getTweak(words.lower())
                            text = "Tweak not found, the following is the closest match: \n\n _________________________ \n\n Title: [" + words +"](" + link + ")\n\nCategory: "+str(typet)+" \n\nDescription: " + descrip + " \n\n _________________________ \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on its accuracy. [Source Code](https://github.com/Healdb/tweakDetectionBot)"
                            if private:
                                r.send_message(author.name,"Private Explanation",text)
                            else:
                                message.reply(text)
                            print "Close Match"
                        except:
                            print "No Match"
                            text ="Tweak not found, and there are no close matches. You may have spelled the name incorrectly. \n\n _________________________ \n\nCreated by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on its accuracy. [Source Code](https://github.com/Healdb/tweakDetectionBot)"
                            if private:
                                r.send_message(author.name,"Private Explanation",text)
                            else:
                                message.reply(text)
                else:
                    text="The following is a short description and link for the tweak you requested: \n\n _________________________ \n\n Title: [" + words +"](" + link + ")\n\nCategory: "+str(typet)+" \n\nDescription: " + descrip + " \n\n _________________________ \n\n Created by healdb. This bot uses http://planet-iphones.com to find its information, and therefore makes no guarantees on its accuracy. [Source Code](https://github.com/Healdb/tweakDetectionBot)"
                    if private:
                        r.send_message(author.name,"Private Explanation",text)
                    else:
                        message.reply(text)
                    print "Found post and commented, link: " + submission.permalink
            else:
                print "Username mention is not in /r/jailbreak"
            message.mark_as_read()
        print "Done checking inbox"
        time.sleep(5)
    except:
        print traceback.format_exc()
        time.sleep(600) #ND - Why are you sleeping for 10 minutes if an error is thrown? Just have it exit if you want to see the error.
