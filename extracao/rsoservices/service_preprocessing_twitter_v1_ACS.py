# -*- coding: UTF-8 -*-
import sys

import emoji
import mysql.connector

from extracao.rsoservices.config import config
from extracao.rsoservices.emoji_dict import emoticon_dict
from extracao.rsoservices.preprocessing_dict import EMOJI_CARACTER


add_message_table0 = ("INSERT INTO extracao_processamento_tweet "
                      "(tweet_id, workspace_id, tweet_origin, tweet_tratament, tweet_demojize, tweet_process) "
                      "VALUES (%s, %s, %s, %s, %s, %s)")

def preprocessamento_tweets(workspace_id):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT id, tweet FROM extracao_tweet WHERE workspace_id=%s;", (workspace_id,))
    try:
        mensagens = con.fetchall()
        for msn in mensagens:
            id_tweet=msn[0]
            message_origin=msn[1]
            con.execute("SELECT tweet_id FROM extracao_processamento_tweet WHERE tweet_id=%s;", (id_tweet,))
            if con.fetchall():
                continue
            else:
                message_tratament = tratament(message_origin)
                if message_tratament == None:
                    message_origin=None
                elif message_tratament == message_origin:
                    message = emoji(message_tratament)
                    message_demojize = None
                    message_tratament=None
                    con.execute(add_message_table0, (id_tweet, workspace_id, message_origin, message_tratament, message_demojize, message))
                    conex.commit()
                else:
                    message_demojize = None
                    message = emoji(message_tratament)
                    con.execute(add_message_table0, (id_tweet, workspace_id, message_origin, message_tratament, message_demojize, message))
                    conex.commit()
                    continue
            continue  
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.close()
    print("fim")
 


def tratament(s):
    if (s == '') or (s == None):
        s = None
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
    
    return s
    
def emoji(origin): 
    try:
        import emoji
        s = emoji.demojize(origin)
        s = s.replace('::', ': :')
        lista_texto = s.split()
        print(lista_texto)
        lista_demoj=[]
        for palavra in lista_texto:            
            parada=False
            cont=0
            while not parada:
                for group in EMOJI_CARACTER.items():
                    cont+=1
                    qtd_emojis=EMOJI_CARACTER.__len__()
                    chave=group[0]
                    valor=group[1]     
                    if chave != palavra:
                        if chave in palavra:
                            palavra=palavra.split(chave)
                            palavra=''.join(palavra)
                            lista_demoj.append(palavra)
                            lista_demoj.append(valor)
                            #print(lista_demoj)
                            #demoj=''.join(lista_demoj)
                            parada=True
                            break
                        else:
                            if palavra in lista_demoj:
                                parada=True
                                break
                            elif palavra==chave:
                                lista_demoj.append(valor)
                                parada=True
                                break
                            elif chave not in palavra and cont <= qtd_emojis:
                                continue
                            else:        
                                lista_demoj.append(palavra)
                                #demoj=''.join(lista_demoj)
                                parada=True
                                break    
                        #print(lista_demoj)
                        #demoj=''.join(lista_demoj)
                        #print(demoj)        
                    else:
                        lista_demoj.append(valor)
                        #print(lista_demoj)
                        #demoj=''.join(lista_demoj)  
                        parada=True
                        break          
        demoj=' '.join(lista_demoj)
        print(origin)
        print(demoj)
        if demoj == origin:
            demoj=None
            return demoj
        else:   
            return demoj
    except Exception as e:
        print(e)

def process_tweet(workspace_id):     
        preprocessamento_tweets(workspace_id)
            
if (__name__ == '__main__'):
    process_tweet()