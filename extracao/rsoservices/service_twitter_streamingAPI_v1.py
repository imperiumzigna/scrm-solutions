#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
from email.utils import parsedate
from http.client import IncompleteRead
import json
import sys
from time import strftime
import time

from mysql.connector import errorcode
import mysql.connector
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

from extracao.rsoservices.config import config


add_message = ("INSERT INTO extracao_tweet (workspace_id, termo_consulta) VALUES (%s,%s)")

update_message = ("UPDATE extracao_tweet SET criacao=%s, tweet_id=%s, tweet=%s, usuario=%s, lingua=%s, seguidores=%s, amigos=%s, localidade=%s WHERE id=%s")

def update_post(created_at, id_str, tweet, username, lang, user_followers, user_friends, location):
        conex = mysql.connector.connect(**config)
        cnx = conex.cursor()
        cnx.execute("SELECT MAX(id) FROM extracao_tweet;")
        dados = cnx.fetchall()
        for d in dados:
            id_post=d[0]
        cnx.execute("SELECT workspace_id, termo_consulta FROM extracao_tweet where id=%s;", (id_post,))    
        dados = cnx.fetchall()
        for d in dados:    
            works=d[0]
            termo=d[1]
        cnx.execute("SELECT * FROM extracao_tweet where tweet_id=%s and workspace_id=%s;", (id_str, works,))
        if cnx.fetchall():
            print("Tweet já foi salvo")
            return False
        else:
            print('Tweet: %s' %tweet)        
            cnx.execute(update_message, (created_at, id_str, tweet, username, lang, user_followers, user_friends, location, id_post))
            cnx.execute(add_message, (works, termo))
            conex.commit()


class listener(StreamListener):

    def on_data(self, data):
        try:
            all_data = json.loads(data)
            created_at = parsedate(all_data["created_at"])
            created_at = strftime("%d-%m-%Y %H:%M:%S", created_at)
            id_str = all_data["id_str"]
            tweet = all_data["text"]
            tweet = tweet.replace('\n', ' ').replace('\r', '')
            tweet = tweet.encode('utf-8')
            username = all_data["user"]["screen_name"]
            lang = all_data["lang"]
            user_followers = all_data["user"]["followers_count"]
            user_friends = all_data["user"]["friends_count"]
            location = all_data["user"]["location"]
            update_post(created_at, id_str, tweet, username, lang, user_followers, user_friends, location)
            return True
        except Exception as e:
            print(e)    
            return True

    def on_error(self, status):
            print(status)

def main_twitter(termo_consulta, ckey, csecret, atoken, asecret):       
    
    while True:
        try:
            l = listener()
            auth = OAuthHandler(ckey, csecret)
            auth.set_access_token(atoken, asecret)
            # Connect/reconnect the stream
            stream = Stream(auth, l)
            # DON'T run this approach async or you'll just create a ton of streams!
            stream.filter(track=[termo_consulta])          
        except IncompleteRead:
            # Oh well, reconnect and keep trucking
            continue
        except KeyboardInterrupt:
            # Or however you want to exit this loop
            stream.disconnect()
            break
        except Exception as e:
            print(e)
            l = listener()
            auth = OAuthHandler(ckey, csecret)
            auth.set_access_token(atoken, asecret)
            # Connect/reconnect the stream
            stream = Stream(auth, l)
            # DON'T run this approach async or you'll just create a ton of streams!
            stream.filter(track=[termo_consulta])     
                
if __name__ == '__main__':
    main_twitter()       