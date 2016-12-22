from __future__ import unicode_literals

from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.db import models


class Workspace(models.Model):
    face_choice = (
        (u'Facebook: fanpage', u'fanpage'),
        (u'Facebook: tagged', u'tagged'),
    )
    
    tweet_choice = (
        (u'twitter', u'twitter'),
    )
    user = models.ForeignKey(User, default=1)
    extracao_facebook = models.CharField(max_length=50, choices=face_choice)
    user_token = models.CharField(max_length=100)
    extracao_twitter = models.CharField(max_length=50, choices=tweet_choice)
    ckey = models.CharField(max_length=50)
    csecret = models.CharField(max_length=50)
    atoken = models.CharField(max_length=50)
    asecret = models.CharField(max_length=50)
    #is_favorite = models.BooleanField(default=False)
        
    def __str__(self):
        return self.extracao_facebook + self.extracao_twitter + ' | ' + str(self.user)

class Fanpage(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    page_id = models.CharField(max_length=30, null=True)
    page = models.CharField(max_length=100)
    page_name =  models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.page

class Post(models.Model):
    post_choice = (
        (u'Post: atualizar_base', u'Atualizar Base'),
        (u'Post: extracao_completa', u'Extração Completa'),
    )
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    page = models.ForeignKey(Fanpage, on_delete=models.CASCADE)
    tipo_extracao = models.CharField(max_length=50, choices=post_choice)
    post_id = models.CharField(max_length=50)
    created_time =  models.DateTimeField()
    message =  models.TextField()
    shares = models.IntegerField()
    likes = models.IntegerField()
    reactions = models.IntegerField()
    comment = models.IntegerField()
    post_type =  models.CharField(max_length=10)
    media_type =  models.TextField()
    
    def __str__(self):
        return str(self.page)
    
    def get_absolute_url(self):
        return reverse("extracao:detail_face", kwargs={"workspace_id": self.workspace})

class Post_comment(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)    
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_id = models.CharField(max_length=50)
    created_time =  models.DateTimeField()
    message =  models.TextField()
    from_id =  models.CharField(max_length=30)
    from_name =  models.CharField(max_length=255)
    comment_count = models.IntegerField()
    like_count = models.IntegerField()
    
    def __str__(self):
        return str(self.post)
    
class Post_like(models.Model):    
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    id_user = models.CharField(max_length=50)
    name_user =  models.CharField(max_length=255)
    imagem_profile = models.TextField()
    
    def __str__(self):
        return str(self.post)    
    
class Post_reaction(models.Model):    
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    id_user = models.CharField(max_length=50)
    name_user =  models.CharField(max_length=255)
    reaction_type = models.CharField(max_length=20)
    
    def __str__(self):
        return str(self.post) 
    
class Processamento_post(models.Model):    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    page = models.ForeignKey(Fanpage, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    message_origin =  models.TextField()
    message_tratament =  models.TextField(null=True)
    message_demojize =  models.TextField(null=True)
    message =  models.TextField(null=True)
    
    def __str__(self):
        return str(self.post) 
    
class Processamento_comment(models.Model):    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    page = models.ForeignKey(Fanpage, on_delete=models.CASCADE)
    comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    message_origin =  models.TextField()
    message_tratament =  models.TextField(null=True)
    message_demojize =  models.TextField(null=True)
    message =  models.TextField(null=True)
    
    def __str__(self):
        return str(self.post)                    

class Tagged(models.Model):
    post_choice = (
        (u'Post: Atualizar Base', u'atualizar base'),
        (u'Post: Extração Completa', u'extração completa'),
    )
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    page = models.ForeignKey(Fanpage, on_delete=models.CASCADE)
    tipo_extracao = models.CharField(max_length=50, choices=post_choice)
    post_id = models.CharField(max_length=50)
    created_time =  models.DateTimeField()
    message =  models.TextField()
    shares = models.IntegerField()
    likes = models.IntegerField()
    reactions = models.IntegerField()
    comment = models.IntegerField()
    post_type =  models.CharField(max_length=10)
    media_type =  models.TextField()
    
    def __str__(self):
        return str(self.page)

# MODELS DO TWITTER

class Tweet(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    termo_consulta = models.CharField(max_length=50)
    criacao = models.CharField(max_length=19, null=True)
    tweet_id = models.CharField(max_length=20, null=True)
    tweet = models.TextField(null=True)
    usuario = models.CharField(max_length=20, null=True)
    lingua = models.CharField(max_length=10, null=True)
    seguidores = models.CharField(max_length=10, null=True)
    amigos = models.CharField(max_length=10, null=True)
    localidade = models.CharField(max_length=50, null=True)
    #is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.termo_consulta
    
class Processamento_tweet(models.Model): 
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)   
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    tweet_origin =  models.TextField()
    tweet_tratament =  models.TextField(null=True)
    tweet_demojize =  models.TextField(null=True)
    tweet_process =  models.TextField(null=True)
    
    def __str__(self):
        return str(self.post) 

# FIM MODELS TWITTER

class Contact(models.Model):
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=False)
    message = models.TextField(max_length=100, null=False)
    phone = models.CharField(max_length=11, null=False)



