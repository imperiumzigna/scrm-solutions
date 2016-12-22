'''
Created on 11 de set de 2016

Last Update 23 nov 2016

@author: Beatriz & Abraão
'''

import sys

import emoji
import mysql.connector

from extracao.rsoservices.config import config
from extracao.rsoservices.emoji_dict import emoticon_dict


cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

add_message_table0 = ("INSERT INTO extracao_processamento_post "
                      "(post_id, page_id, workspace_id, message_origin, message_tratament, message_demojize, message) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s)")

def preprocessing_posts(workspace_id):
    con = mysql.connector.connect(**config)
    cone = con.cursor()
    cone.execute("SELECT id, page_id, message FROM extracao_post WHERE workspace_id=%s;", (workspace_id,))
    try:
        mensagens = cone.fetchall()
        for msn in mensagens:
            post_id = msn[0]
            page_id = msn[1]
            message_origin = msn[2]
            cone.execute("SELECT post_id FROM extracao_processamento_post WHERE post_id=%s;", (post_id,))
            if cone.fetchall():
                continue
            else:
                if (message_origin=='') or (message_origin == None):
                    continue
                message_tratament = tratament(message_origin)
                
                if message_tratament == message_origin:
                    message_demojize = emot(message_tratament)
                    if message_demojize == message_tratament:
                        #mensagem sem emoticon
                        message_demojize = None
                        #message = emoji_character(message_tratament)
                        message_tratament=None
                    else:
                        #mensagem com emoticon
                        message = emoji_character(message_demojize)
                    message_tratament = None
                    cone.execute(add_message_table0,(post_id, page_id, workspace_id, message_origin, message_tratament, message_demojize, message))
                    con.commit()
                    continue
                else:
                    message_demojize = emot(message_tratament)
                    if message_demojize == message_tratament:
                        #mensagem sem emoticon
                        message_demojize = None
                        message = emoji_character(message_tratament)
                    else:
                        #mensagem com emoticon
                        message = emoji_character(message_demojize)
                    cone.execute(add_message_table0,(post_id, page_id, workspace_id, message_origin, message_tratament, message_demojize, message))
                    con.commit()
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



def process_face(workspace_id):     
    preprocessing_posts(workspace_id)
        
        
if (__name__ == '__main__'):
    process_face()

        
