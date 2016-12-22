'''
config={
    'user':'root',
    'host':'127.0.0.1',
    'password':'',
    'database':'scrm_solutions_homolog',
    'charset':'utf8mb4',
    'use_unicode':'True'
}

'''
# USAR EM PRODUÇÃO
config={
    'user':'root',
    'host':'127.0.0.1',
    'password':'',
    'database':'scrm_solutions',
    'charset':'utf8mb4',
    'use_unicode':'True'
}


''' Conexão com Graph Api Facebook '''

fields_posts = 'posts?fields=from,id,message,created_time,type,full_picture,source,link,shares,reactions.summary(true),comments.summary(true)%7Bid,message,created_time,from,comment_count,like_count%7D,likes.summary(true)%7Bid,name,pic_large%7D'

fields_tagged = 'tagged'
