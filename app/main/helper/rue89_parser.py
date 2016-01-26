from bs4 import BeautifulSoup

__author__ = 'ThinkPad'

import urllib
import sys
import io
import json


prefix = 'http://api.riverains.rue89.nouvelobs.com/user/'
suffix = '/commentaires/0/6000/nojs'

# users_dic = {68450:'lictor', 75415:'Ben85',202771:'dzerjinski1917',167433:"mordraal", 185722:'specht', 218348:'HansiK', 211722:'DRLGHN', 220212:'DOCTEUR YuL',220915:'DEAMONN', 161554:'LAOJINHU', 65781:'YVON LE ZeBULON', 9562:'ENKI', 118642:'DANIEL SCHNEIDERMANN'}
users_dic = {68450:'lictor'}

class Rue89Analyzer():


    def main(self):
        if len(sys.argv)>1 :
            self.parseUrl(sys.argv[1])
        else :
            for user in users_dic.keys():
                self.parseUrl(user)

    def parseUrl(self, userName=None):
        urlToParse = ''
        if userName == None :
            urlToParse = 'http://api.riverains.rue89.nouvelobs.com/lictor/commentaires'
        else :
            urlToParse = prefix + str(userName) + suffix
        r = urllib.urlopen(urlToParse)
        soup = BeautifulSoup(r, from_encoding="utf-8")
        posts = soup.find_all("li", class_="clearfix")
        posts_dic = {}
        id = 0


        for post in posts:
            topic = post.find_all('a')[3].get_text()
            id +=1

            comment = post.find_all('div')[2].get_text()
            posts_dic[id]=topic, comment



        self.writeTextToFile(posts_dic, userName)

    def writeTextToFile(self, posts, userName):
        with io.open(str(userName)+'.json', 'w') as json_file:
            data = json.dumps(posts)
            json_file.write(unicode(data))







if __name__ == "__main__":
    Rue89Analyzer().main()