'''
Created on 11 de set de 2016

Last Update on 23 nov 2016

@author: Beatriz & Abraão
'''


import sys

import emoji
import mysql.connector

from extracao.rsoservices.config import config
from extracao.rsoservices.emoji_dict import emoticon_dict


add_message_table0 = ("INSERT INTO extracao_processamento_tweet "
                      "(tweet_id, workspace_id, tweet_origin, tweet_tratament, tweet_demojize, tweet_process) "
                      "VALUES (%s, %s, %s, %s, %s, %s)")

def preprocessing_tweets(workspace_id):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT id, tweet FROM extracao_tweet WHERE workspace_id=%s;", (workspace_id,))
    try:
        mensagens = con.fetchall()
        for msn in mensagens:
            id_tweet=msn[0]
            tweet_origin=msn[1]
            con.execute("SELECT tweet_id FROM extracao_processamento_tweet WHERE tweet_id=%s;", (id_tweet,))
            if con.fetchall():
                continue
            else:
                tweet_tratament = tratament(tweet_origin)
                if tweet_tratament == None:
                    tweet_origin = None
                elif tweet_tratament == tweet_origin:
                    ##Mudei a partir daqui
                    tweet_demojize = emot(tweet_tratament)
                    
                    if tweet_demojize == tweet_tratament:
                        #mensagem sem emoticon
                        tweet_demojize = None
                        #tweet = emoji_character(tweet_tratament)
                        tweet_tratament=None
                    else:
                        #mensagem com emoticon
                        tweet = emoji_character(tweet_demojize)
                    tweet_tratament = None
                    con.execute(add_message_table0,( id_tweet, workspace_id,tweet_origin, tweet_tratament, tweet_demojize, tweet))
                    conex.commit()
                    continue
                else:
                    tweet_demojize = emot(tweet_tratament)
                    if tweet_demojize == tweet_tratament:
                        #mensagem sem emoticon
                        tweet_demojize = None
                        tweet = emoji_character(tweet_tratament)
                    else:
                        #mensagem com emoticon
                        tweet = emoji_character(tweet_demojize)
                    con.execute(add_message_table0,( id_tweet, workspace_id, tweet_origin, tweet_tratament, tweet_demojize, tweet))
                    conex.commit()
                    continue
            continue
    except Exception as e:
         print("Erro", e)
    con.close()
    print("Fim")     

    
def tratament(s):
    if (s=='') or (s == None):
        s=None
    else:   
        s = s.replace('\n', ' ')
        s = s.replace('\r', ' ')
        s = s.replace('\t', ' ')
        s = s.replace('\v', ' ')
        s = s.replace(",),", ' ')
        s = s.replace("('", ' ')
        s = s.replace(",)]", ' ')
        s = s.replace("'", ' ')
        s = s.replace('("', ' ')
        #Se a mensagem nao estivem em lowercase
        if not s.islower():
            s = s.lower()
        print(s)
  
    return s
    
def emot(s):
    emotic = emoji.demojize(s)
    if s != emotic:
        print(emotic)

    return emotic


def emoji_character(s):
    dic = emoticon_dict
    emo = dic.items()
    for key, value in emo:
        if key in s:
            s = s.replace(key, value)        
    return s



def process_tweet(workspace_id):     
        preprocessing_tweets(workspace_id)
            
if (__name__ == '__main__'):
    process_tweet()

        