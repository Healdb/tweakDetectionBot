import requests
import json
import time
import praw
from bs4 import BeautifulSoup
import re
import traceback

#r = praw.Reddit('/r/jailbreak package description provider')
#ND - It's always good to include a version number and your username to uniqueness

botName=""
password=""
version="0.1.1"
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
def getTweak(packageName):
    link = "https://cydia.saurik.com/api/macciti?query=" + packageName
    response = requests.post(link)
    json_input = response.json()
    decoded = json.dumps(json_input)
    decoded = json.loads(decoded)
    for item in decoded["results"]:
        title=item["display"]
        if title.lower() == packageName:
            link = "http://cydia.saurik.com/package/" + str(item["name"])
            typet= item["section"]
            descrip=item["summary"]
            print link
            print descrip
            return link, descrip,typet
    return False,"error","error"
        
def assembleSuggestions(packageName):
    link = "https://cydia.saurik.com/api/macciti?query=" + packageName
    response = requests.post(link)
    json_input = response.json()
    decoded = json.dumps(json_input)
    decoded = json.loads(decoded)
    links= []
    names=[]
    for item in decoded["results"]:
        title=item["display"]
        link = str(item["name"])
        names.append(title)
        links.append(link)
    c=0
    shortest=0
    shortName=""
    for link in links:
        link = "http://planet-iphones.com/cydia/id/"+link
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
    print "checking Spaces"
    c=1
    link = "https://cydia.saurik.com/api/macciti?query=" + words
    response = requests.post(link)
    json_input = response.json()
    decoded = json.dumps(json_input)
    decoded = json.loads(decoded)
    for char in words:
        words=words.replace(" ","")
        words = words[:c] + ' ' + words[c:]
        for item in decoded["results"]:
            title=item["display"]
            if title.lower() == words:
                return title.lower()
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
                if str(submission.subreddit).lower()=="jailbreak" or str(submission.subreddit).lower()=="tweakinfo":
                    jailbreak=True
                else:
                    jailbreak=False
            except:
                print traceback.format_exc()
                jailbreak=False
            if jailbreak:
                print "Checking username mention for flag"
                text = message.body
                author =message.author
                words = findTitle(text)
                private=False
                if text.lower().find("private") != -1:
                    private=True
                pwords=words
                try:
                    link, descrip,typet= getTweak(words.lower())
                except:
                    print traceback.format_exc()
                    message.mark_as_read()
                    break
                if link==False:
                    words=checkSpaces(pwords.lower())
                    try:
                        link, descrip,typet= getTweak(words.lower())
                        text = "I assume you wanted information on: \n\n _________________________ \n\nTitle/Link: | [" + words +"](" + link + ")\n---|---\n**Category:** |**"+str(typet)+"**\n**Description:** |**" + descrip + "** \n\n _________________________ \n\nCreated by healdb. [More Information](https://www.reddit.com/r/tweakinfo/comments/3dhd98/more_information/)."
                        if private:
                            r.send_message(author.name,"Private Explanation",text)
                        else:
                            message.reply(text)
                        print "Close Match"
                    except:
                        try:
                            words = assembleSuggestions(pwords.lower())
                            link, descrip,typet= getTweak(words.lower())
                            text = "I assume you wanted information on: \n\n _________________________ \n\nTitle/Link: | [" + words +"](" + link + ")\n---|---\n**Category:** |**"+str(typet)+"**\n**Description:** |**" + descrip + "** \n\n _________________________ \n\nCreated by healdb. [More Information](https://www.reddit.com/r/tweakinfo/comments/3dhd98/more_information/)."
                            if private:
                                r.send_message(author.name,"Private Explanation",text)
                            else:
                                message.reply(text)
                            print "Close Match"
                        except:
                            print "No Match"
                            text = "Tweak not found, and there are no close matches. You may have spelled the name incorrectly. \n\n _________________________ \n\nCreated by healdb. [More Information](https://www.reddit.com/r/tweakinfo/comments/3dhd98/more_information/)."
                            if private:
                                r.send_message(author.name,"Private Explanation",text)
                            else:
                                message.reply(text)
                else:
                    text="Title/Link: | [" + words +"](" + link + ")\n---|---\n**Category:** |**"+str(typet)+"**\n**Description:** |**" + descrip + "** \n\n _________________________ \n\nCreated by healdb. [More Information](https://www.reddit.com/r/tweakinfo/comments/3dhd98/more_information/)."
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
        time.sleep(600)
