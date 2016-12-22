#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, timedelta
from time import sleep
from urllib.parse import urlparse, parse_qs

from dateutil import parser
from facebook import GraphAPI
import mysql.connector

from extracao.rsoservices.config import config, fields_posts, fields_tagged


add_message_table0 = ("INSERT INTO extracao_fanpage "
                      "(page_id, page, page_name, workspace_id) "
                      "VALUES (%s, %s, %s, %s)")

add_message_table1 = ("INSERT INTO extracao_post "
                      "(page_id, workspace_id, tipo_extracao, post_id, created_time, message, shares, likes, reactions, comment, post_type, media_type) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

add_message_table2 = ("INSERT INTO extracao_post_comment "
                      "(post_id, comment_id, created_time, message, from_id, from_name, comment_count, like_count, workspace_id) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

add_message_table3 = ("INSERT INTO extracao_post_reaction "
                      "(post_id, id_user, name_user, reaction_type) "
                      "VALUES (%s, %s, %s, %s)")

add_message_table4 = ("INSERT INTO extracao_post_like "
                      "(post_id, id_user, name_user, imagem_profile) "
                      "VALUES (%s, %s, %s, %s)")

add_message_table5 = ("INSERT INTO extracao_tagged "
                      "(page_id, post_id, created_time, message) "
                      "VALUES (%s, %s, %s, %s)")
    
def insere_fanpage(page_id, page, page_name, workspace_id):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT * FROM extracao_fanpage WHERE page_id=%s and workspace_id=%s;", (page_id, workspace_id,))
    if con.fetchall():
        return False
    try:
        con.execute(add_message_table0, (page_id, page, page_name, workspace_id))
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.commit()
    conex.close()
    
def insere_post(page, workspace_id, tipo_extracao, post_id, created_time, message, shares, likes, reactions, comment, post_type, media_type):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT * FROM extracao_post WHERE post_id=%s and workspace_id=%s;", (post_id, workspace_id,))
    if con.fetchall():
        return False
    try:
        con.execute("SELECT id FROM extracao_fanpage WHERE page=%s;", (page,))
        all_ids = con.fetchall()
        for ids in all_ids:
            fanpage=ids[0]
        con.execute(add_message_table1, (fanpage, workspace_id, tipo_extracao, post_id, created_time, message, shares, likes, reactions, comment, post_type, media_type))
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.commit()
    conex.close()
    
def insere_comment(post_id, comment_id, created_time, message, from_id, from_name, comment_count, like_count, workspace_id):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT * FROM extracao_post_comment WHERE comment_id=%s and workspace_id=%s;", (comment_id, workspace_id,))
    if con.fetchall():
        return False
    try:
        con.execute("SELECT id FROM extracao_post WHERE post_id=%s and workspace_id=%s;", (post_id, workspace_id,))
        all_ids = con.fetchall()
        for ids in all_ids:
            post_comment_id=ids[0]
        con.execute(add_message_table2, (post_comment_id, comment_id, created_time, message, from_id, from_name, comment_count, like_count, workspace_id))
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.commit()
    
def insere_reaction(post_id, id_user, name_user, reaction_type):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT a.post_id, a.id_user "
                "FROM extracao_post_reaction as a "
                "JOIN extracao_post as b "
                "ON b.id = a.post_id "
                "WHERE b.post_id=%s and a.id_user=%s;", (post_id, id_user,))
    if con.fetchall():
        return False
    try:
        con.execute("SELECT id FROM extracao_post WHERE post_id=%s;", (post_id,))
        all_ids = con.fetchall()
        for ids in all_ids:
            post=ids[0]
        con.execute(add_message_table3, (post, id_user, name_user, reaction_type))
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.commit()
    
def insere_like(post_id, id_user, name_user, imagem_profile):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT id FROM extracao_post WHERE post_id=%s;", (post_id,))
    all_ids = con.fetchall()
    for ids in all_ids:
        post=ids[0]
    con.execute("SELECT * FROM extracao_post_like WHERE post_id=%s and id_user=%s;", (post, id_user,))
    if con.fetchall():
        return False
    try:
        con.execute(add_message_table4, (post, id_user, name_user, imagem_profile))
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.commit()
  
def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def save_comment(graph, post_id, posts_restantes, workspace_id):
    arguments2={}
    proximo2 = None 
    parada = ''     
    total=0
    total_comentarios=0
    atualiza_comment=False    
    while parada != proximo2:  
        try:
            comentarios = graph.get_connections(id= post_id, connection_name='comments', limit=100, fields = 'id,message,created_time,from,comment_count,like_count', **arguments2)
        except Exception as e:
            print(e)
            break
        if 'paging' in comentarios:
            paging = comentarios['paging']        
            if 'next' in paging:
                proximo2 = paging['next']
            else:    
                parada = proximo2    
        else:    
            parada = proximo2
        comments_data = comentarios['data']
           
        for comment in comments_data:   
            created_time = parser.parse(comment['created_time'])
            created_time = utc_to_local(created_time)             
            if posts_restantes and not atualiza_comment:
                conex = mysql.connector.connect(**config)
                con = conex.cursor()
                con.execute("SELECT id FROM extracao_post WHERE post_id=%s and workspace_id=%s;", (post_id, workspace_id))
                all_ids = con.fetchall()
                for ids in all_ids:
                    post=ids[0]
                    con.execute("SELECT min(created_time) FROM extracao_post_comment WHERE post_id=%s;", (post,))
                    created_timeBd_comment = con.fetchall()
                    conex.close()
                            
                    for date in created_timeBd_comment:
                        min_dateBd=date[0]
                    if not atualiza_comment and min_dateBd != None:
                        if min_dateBd < created_time:
                            continue
                        else:
                            atualiza_comment=True
            
            if 'message' in comment:
                    #message = make_it_good(comment['message'])
                    message = comment['message']
                    #print("Mensagem: "+ message)
            else:
                message = ''
                #print("Mensagem: "+ message)
               
            comment_id = str(comment['id'])
            from_id = str(comment['from']['id'])
            from_name = str(comment['from']['name'])  
            like_count = comment['like_count']
            comment_count = comment['comment_count']
            
            insere_comment(post_id, comment_id, created_time, message, from_id, from_name, comment_count, like_count, workspace_id)
            total+=1
            
            if total == len(comments_data):
                total_comentarios += total
                total=0
                #print('Comentarios salvos:'+str(total_comentarios))
            #else:
                #comentario=total_comentarios + total
                #print('Comentario: '+ str(comentario))    
        if proximo2:
            qs = parse_qs(urlparse(proximo2).query)
            arguments2 = {'after': qs['after'][0]}
            proximo2 = None
        elif proximo2 == parada:
            break
        else:
            #print('Total Comentarios salvos:'+ str(len(comments_data)))
            break
    print('Terminado!Total de comentarios salvos', total_comentarios)
    
def save_reaction(graph, post_id, posts_restantes):
    arguments3={}
    proximo3 = None 
    parada = ''     
    total=0
    total_reacoes=0    
    while parada != proximo3:  
        try:
            reacoes = graph.get_connections(id= post_id, connection_name='reactions', limit=100, fields = 'id,type,name', **arguments3)
        except Exception as e:
            print(e)
            break
        if 'paging' in reacoes:
            paging = reacoes['paging']        
            if 'next' in paging:
                proximo3 = paging['next']
            else:    
                parada = proximo3    
        else:    
            parada = proximo3
        reactions_data = reacoes['data']   
        for react in reactions_data:
            id_user=str(react['id'])
            name_user=str(react['name'])
            reaction_type=str(react['type'])

            insere_reaction(post_id, id_user, name_user, reaction_type)
            total+=1
            
            if total == len(reactions_data):
                total_reacoes += total
                total=0
                #print('reacoes salvas:'+str(total_reacoes))
            #else:
                #reacao=total_reacoes + total
                #print('reacao: '+ str(reacao))    
        if proximo3:
            qs = parse_qs(urlparse(proximo3).query)
            arguments3 = {'after': qs['after'][0]}
            proximo3 = None
        elif proximo3 == parada:
            break
        else:
            #print('Total reacoes salvas:'+ str(len(reactions_data)))
            break
    print('Terminado!Total de reacoes salvas', total_reacoes)
    
def save_like(graph, post_id,posts_restantes):
    arguments4={}
    proximo4 = None 
    parada = ''     
    total=0
    total_likes=0    
    while parada != proximo4:  
        try:
            likes = graph.get_connections(id= post_id, connection_name='likes', limit=100, fields = 'id,name,pic_large', **arguments4)
        except Exception as e:
            print(e)
            break
        if 'paging' in likes:
            paging = likes['paging']        
            if 'next' in paging:
                proximo4 = paging['next']
            else:    
                parada = proximo4    
        else:    
            parada = proximo4
        likes_data = likes['data']   
        for joinha in likes_data:   
            id_user=str(joinha['id'])
            name_user=str(joinha['name'])
            imagem_profile=str(joinha['pic_large'])

            insere_like(post_id, id_user, name_user, imagem_profile)
            total+=1
            
            if total == len(likes_data):
                total_likes += total
                total=0
                #print('likes salvos:'+str(total_likes))
            #else:
                #like=total_likes + total
                #print('like: '+ str(like))    
        if proximo4:
            qs = parse_qs(urlparse(proximo4).query)
            arguments4 = {'after': qs['after'][0]}
            proximo4 = None
        elif proximo4 == parada:
            break
        else:
            #print('Total likes salvos:'+ str(len(likes_data)))
            break
    print('Terminado!Total de likes salvos', total_likes)     

def save_posts_pagina(page, workspace_id, tipo_extracao, access_token, num_post=None, posts_recentes=False, posts_restantes=False):
    if not num_post:
        num_post = 10000000
    graph = GraphAPI(access_token)
    arguments = {}
    num_saved = 0
    proximo = None 
    parada = ''
    atualiza = False
    extracao_diaria = False
    while parada != proximo:
        try:
            posts = graph.get_connections(page, fields_posts, **arguments)
        except Exception as e:
            print("ocorreu o seginte erro:", e)
            break
        if 'paging' in posts:
            proximo = posts['paging']['next']
            if proximo == parada:
                print("Todas as Postagens foram extraídas.")
                break
            parada = proximo
        posts = posts['data']
        for post in posts:  
            created_time = parser.parse(post['created_time'])
            created_time = utc_to_local(created_time) 
            if posts_restantes and not atualiza:
                conex = mysql.connector.connect(**config)
                con = conex.cursor()
                con.execute("SELECT id FROM extracao_fanpage WHERE page=%s;", (page,))
                all_ids = con.fetchall()
                for ids in all_ids:
                    fanpage=ids[0]
                    con.execute("SELECT min(created_time) FROM extracao_post WHERE page_id=%s;", (fanpage,))
                try:
                    created_timeBd_post = con.fetchall()
                    for date in created_timeBd_post:
                        min_dateBd=date[0]
                    if not atualiza and min_dateBd != None:
                        if min_dateBd < created_time:
                            print("Aguarde"+" \t!!!!")
                            #save_comment(graph, post['id'], posts_restantes, workspace_id)
                            #save_like(graph, post['id'], posts_restantes)    
                            #save_reaction(graph, post['id'], posts_restantes)
                            continue
                        else:
                            atualiza=True
                except Exception as e:
                    print(e) 
                          
            page_id = str(post['from']['id'])
            page_name = str(post['from']['name'])
            
            insere_fanpage(page_id, page, page_name, workspace_id)
            
            if 'message' in post:
                message = post['message']
                #print("Mensagem: "+ message)
            else:
                message = ''
                print("Mensagem: "+ message)

            post_type = post['type']
            
            if 'source' in post:
                media_type = post['source']
                print("Tipo de midia: "+ post_type + '\n url:'+ media_type)    
            else:        
                if post_type == 'link':
                    media_type = post['link']
                    print("Tipo de midia:  "+ post_type + '\n url:'+ media_type) 
                elif post_type == "photo":
                    media_type = post['full_picture']
                    print("Tipo de midia:  "+ post_type + '\n url:'+ media_type)    
                else:
                    media_type = ''
            
            if 'shares' in post:
                shares = post['shares']['count']
                print("shares: " + str(shares))
            else:
                shares = 0
                print("Shares: "+str(shares))
            
            if 'likes' in post:
                likes = post['likes']['summary']['total_count']
                print("Likes:"+str(likes))
            else:
                likes = 0
                print("Likes: "+str(likes))
                
            if 'reactions' in post:
                reactions = post['reactions']['summary']['total_count']
                print("Reactions:"+ str(reactions))
            else:
                reactions = 0
                print("Reactions: "+str(reactions))    
            
            if 'comments' in post:
                if 'total_count' not in post['comments']['summary']:
                    comment = 0
                    continue
                comment = post['comments']['summary']['total_count']
                print("Comentarios: " + str(comment))
            else:
                comment = 0
                print(str(comment))
            
            if posts_recentes and not extracao_diaria:
                conex = mysql.connector.connect(**config)
                con = conex.cursor()
                con.execute("SELECT id FROM extracao_fanpage WHERE page=%s;", (page,))
                all_ids = con.fetchall()
                for ids in all_ids:
                    fanpage=ids[0]
                    con.execute("SELECT max(created_time) FROM extracao_post WHERE page_id=%s;", (fanpage,))
                max_created_timeBd = con.fetchall()          
                for date in max_created_timeBd:
                    max_dateBd = date[0]
                if max_dateBd != None:
                    if max_dateBd < created_time:
                        extracao_diaria=True
                    else:
                        break
                else:
                    print('Nenhuma postagem extraida ainda!Realizando extração')
            if posts_recentes and extracao_diaria:
                if max_dateBd < created_time:
                    num_saved += 1
                    #Inserir postagens antes dos comentários Foreing Key post_id --> id
                    insere_post(page, workspace_id, tipo_extracao, post['id'], created_time, message, shares, likes, reactions, comment, post_type, media_type)
                    #Chama método pra salvar comentários
                    #save_comment(graph, post['id'], posts_restantes, workspace_id)
                    #save_like(graph, post['id'])    
                    #save_reaction(graph, post['id'])
                else:
                    extracao_diaria=False
                    break    
            else:
                num_saved += 1
                #Inserir postagens antes dos comentários Foreing Key post_id --> id
                insere_post(page, workspace_id, tipo_extracao, post['id'], created_time, message, shares, likes, reactions, comment, post_type, media_type)
                # Chama método pra salvar comentários
                #save_comment(graph, post['id'], posts_restantes,workspace_id)
                #save_like(graph, post['id'], posts_restantes)
                #save_reaction(graph, post['id'], posts_restantes)
            
            print('\n\nTotal de postagens salvas: %d ' % num_saved)
        if posts_recentes:
            if extracao_diaria:
                pass
            else:
                print('Atualizado, recentes')
                break
        if proximo:
            qs = parse_qs(urlparse(proximo).query)
            arguments = {'limit': qs['limit'][0], 'until': qs['until'][0]}
            proximo = None
        else:
            break
    print('Terminado!Total salvo %d posts' % num_saved)


def main_facebook(fanpage, workspace_id, access_token, tipo_postagem, tipo_extracao):     
        atualiza_base=False
        extracao_completa=False
        
        if tipo_postagem == 'Facebook: fanpage':
            if tipo_extracao =='Post: atualizar_base':
                atualiza_base=True
                save_posts_pagina(fanpage, workspace_id, tipo_extracao, access_token, "", atualiza_base, extracao_completa)
                '''
                #utilizar apenas um como true
                #os dois como False extrai tudo: recentes + todo conteudo
                #(nome_da_pagina + postagens recentes + postagens restantes[quando interrompe a extração])
                '''
            else:
                save_posts_pagina(fanpage, workspace_id, tipo_extracao, access_token, "", atualiza_base, extracao_completa)
        else:
            if tipo_extracao =='Post: atualizar_base':
                atualiza_base=True
                save_posts_tagged(fanpage, workspace_id, tipo_extracao, access_token, "", atualiza_base, extracao_completa)
            else:
                save_posts_pagina(fanpage, workspace_id, tipo_extracao, access_token, "", atualiza_base, extracao_completa)

if (__name__ == '__main__'):
    main_facebook()
