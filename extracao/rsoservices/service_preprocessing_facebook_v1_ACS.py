# -*- coding: UTF-8 -*-

import mysql.connector

from face_v05_config import conexao, config
from preprocessing_dict import EMOJI_CARACTER


table0 = ("CREATE TABLE `extracao_processamento_posts` ("
         "  `id` int(11) NOT NULL AUTO_INCREMENT,"
         "  `post` int(11) NOT NULL,"
         "  `message_origin` LONGTEXT,"
         "  `message_tratament` LONGTEXT,"
         "  `message_demojize` LONGTEXT,"
         "  `message` LONGTEXT,"
         "  PRIMARY KEY (`id`),"
         "  FOREIGN KEY (post) REFERENCES extracao_posts(id)"
         ") ENGINE=InnoDB")

table1 = ("CREATE TABLE `extracao_processamento_comments` ("
         "  `id` int(11) NOT NULL AUTO_INCREMENT,"
         "  `comment` int(11) NOT NULL,"
         "  `message_origin` LONGTEXT,"
         "  `message_tratament` LONGTEXT,"
         "  `message_demojize` LONGTEXT,"
         "  `message` LONGTEXT,"
         "  PRIMARY KEY (`id`),"
         "  FOREIGN KEY (comment) REFERENCES extracao_posts_comments(id)"
         ") ENGINE=InnoDB")

add_message_table0 = ("INSERT INTO extracao_processamento_posts "
                      "(post, message_origin, message_tratament, message_demojize, message) "
                      "VALUES (%s, %s, %s, %s, %s)")

add_message_table1 = ("INSERT INTO extracao_processamento_comments "
                      "(comment, message_origin, message_tratament, message_demojize, message) "
                      "VALUES (%s, %s, %s, %s, %s)")

def create_db_table():
    verifica_bd = True
    cnx = mysql.connector.connect(**conexao)
    cursor = cnx.cursor()
    cursor.execute('SHOW DATABASES;')
    all_dbs = cursor.fetchall()
    for db in all_dbs:
        if db == (config['database'],):
            verifica_bd=False        
            continue            
    if verifica_bd:
        print("Schema nao existe \n Criando schema")
        cursor.execute("CREATE DATABASE {} CHARACTER SET {} COLLATE utf8mb4_unicode_ci".format(config['database'],config['charset']))  
        cnx.close()
    else:
        print("Database selecionada:",config['database'])                    
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute('USE %s;' % config['database'])
    con.execute("SHOW TABLES;")
    all_tables = con.fetchall()

    if all_tables.count(('extracao_processamento_posts',)) == 0:
        print("Tabela nao exite \n Criando tabela")
        con.execute(table0)
    if all_tables.count(('extracao_processamento_comments',)) == 0:
        print("Tabela nao exite \n Criando tabela")
        con.execute(table1)
    conex.commit()
    conex.close()

def preprocessamento_posts(page):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT id FROM extracao_fanpages WHERE page=%s;", (page,))
    all_ids = con.fetchall()
    for ids in all_ids:
        page_id=ids[0]
        con.execute("SELECT id, message FROM extracao_posts WHERE page=%s;", (page_id,))
    try:
        mensagens = con.fetchall()
        for msn in mensagens:
            message_origin=msn[1]
            con.execute("SELECT message_origin FROM extracao_processamento_posts WHERE message_origin=%s;", (message_origin,))
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
                    con.execute(add_message_table0, (page_id, message_origin, message_tratament, message_demojize, message))
                    conex.commit()
                else:
                    message_demojize = None
                    message = emoji(message_tratament)
                    con.execute(add_message_table0, (page_id, message_origin, message_tratament, message_demojize, message))
                    conex.commit()
                    continue
            continue  
    except Exception as e:
        print("EXCECAO!!!!!!!Insert no db", e)
    conex.close()
    print("fim")
 
def preprocessamento_comments(page):
    conex = mysql.connector.connect(**config)
    con = conex.cursor()
    con.execute("SELECT a.id "
                "FROM extracao_posts as a "
                "JOIN extracao_fanpages as b "
                "ON b.id = a.page "
                "WHERE b.page=%s;", (page,))
    all_ids = con.fetchall()
    for ids in all_ids:
        id_comen=ids[0]
        con.execute("SELECT id, message FROM extracao_posts_comments WHERE post=%s;", (id_comen,))
        try:
            mensagens = con.fetchall()
            for msn in mensagens:
                comment_id=msn[0]
                con.execute("SELECT comment FROM extracao_processamento_comments WHERE comment=%s;", (comment_id,))
                if con.fetchall():
                    continue
                else:
                    message_origin=msn[1]
                    print(message_origin)
                    message_tratament = tratament(message_origin)
                    if message_tratament == None:
                        message_origin=None
                    elif message_tratament == message_origin:
                        message_demojize = emoji.demojize(message_tratament)
                        message = emoji(message_tratament)
                        message_tratament=None
                        con.execute(add_message_table1, (comment_id, message_origin, message_tratament, message_demojize, message))
                        conex.commit()
                    else:
                        message_demojize = emoji.demojize(message_tratament)
                        message = emoji(message_tratament)
                        con.execute(add_message_table1, (comment_id, message_origin, message_tratament, message_demojize, message))
                        conex.commit()
                        continue
                continue
        except Exception as e:
            print("EXCECAO!!!!!!!Insert no db", e)
        continue
        conex.close()
        print("fim")    

def tratament(s):
    if s == '':
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

def main():
    #emoji('ReageTuna❤ ?❤❤ Reage❤ Tuna')             
    create_db_table()
    preprocessamento_posts("rio2016pt")
    #preprocessamento_comments("rio2016pt")

    
if (__name__ == '__main__'):
    main()