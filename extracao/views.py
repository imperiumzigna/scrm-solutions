#!/usr/bin/env python
# -*- coding: utf-8 -*-
import calendar
import codecs
from datetime import datetime, timedelta
from email.utils import parsedate
import json
import sys
import threading
from time import sleep, strftime
import time
from urllib.parse import urlparse, parse_qs

from dateutil import parser
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Page
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from facebook import GraphAPI
from mysql.connector import errorcode
import mysql.connector

from extracao.rsoservices.config import config, fields_posts
from extracao.rsoservices.service_facebook_graphAPI_v1 import main_facebook
from extracao.rsoservices.service_preprocessing_facebook_v1 import process_face
from extracao.rsoservices.service_preprocessing_twitter_v1 import process_tweet
from extracao.rsoservices.service_twitter_streamingAPI_v1 import main_twitter

from .forms import UserForm, WorkspaceFacebookForm, WorkspaceTwitterForm, FacebookFanpageForm, FacebookPostForm, FacebookTaggedForm, TwitterPostForm, ContactForm
from .models import Workspace, Fanpage, Post, Post_comment, Post_like, Post_reaction, Processamento_post, Processamento_comment, Tweet, Contact

from django.http import HttpResponse
from .resources import ProcessamentoPostResource
from .resources import ProcessamentoTweetResource


def home(request):
    return render(request, 'index.html', {})
    
def extracao(request):
    return render(request, 'extracao/index.html', {})

def select_social(request):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        return render(request, 'extracao/select_social.html', {})

def create_workspace_facebook(request):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        form = WorkspaceFacebookForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.user = request.user
            workspace.save()
            return render(request, 'extracao/detail.html', {'workspace': workspace})
        context = {
            "form": form,
        }
        return render(request, 'extracao/create_workspace.html', context)
    
def create_workspace_twitter(request):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        form = WorkspaceTwitterForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.user = request.user
            workspace.save()
            return render(request, 'extracao/detail.html', {'workspace': workspace})
        context = {
            "form": form,
        }
        return render(request, 'extracao/create_workspace.html', context)
    
def delete_workspace(request, workspace_id):
    workspace = Workspace.objects.get(pk=workspace_id)
    workspace.delete()
    workspaces = Workspace.objects.filter(user=request.user)
    return render(request, 'extracao/index.html', {'workspaces': workspaces})

def update_workspace_facebook(request, workspace_id):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        workspace = Workspace.objects.get(pk=workspace_id)
        form = WorkspaceFacebookForm(request.POST or None, instance=workspace)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.save()
            return render(request, 'extracao/detail.html', {'workspace': workspace, 'form':form})
        context = {
            "form": form,
        }
        return render(request, 'extracao/update_workspace.html', context)

def update_workspace_twitter(request, workspace_id):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        form = WorkspaceTwitterForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.user = request.user
            workspace.save()
            return render(request, 'extracao/detail.html', {'workspace': workspace})
        context = {
            "form": form,
        }
        return render(request, 'extracao/update_workspace.html', context)

def delete_post_fanpage(request, workspace_id, post_id):
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    post = Post.objects.get(pk=post_id)
    post.delete()
    return render(request, 'extracao/detail.html', {'workspace': workspace})

def delete_post_tagged(request, workspace_id, tagged_id):
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    tagged = Tagged.objects.get(pk=tagged_id)
    tagged.delete()
    return render(request, 'extracao/detail.html', {'workspace': workspace})

def delete_post_tweet(request, workspace_id, tweet_id):
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    tweet = Tweet.objects.get(pk=tweet_id)
    tweet.delete()
    return render(request, 'extracao/detail.html', {'workspace': workspace})

def detail(request, workspace_id):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        user = request.user
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        return render(request, 'extracao/detail.html', {'workspace': workspace, 'user': user})

def detail_process(request, workspace_id):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        user = request.user
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        return render(request, 'extracao/detail_process.html', {'workspace': workspace, 'user': user})

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        workspaces = Workspace.objects.filter(user=request.user)
        results_post = Post.objects.all()
        results_tagged = Post.objects.all()
        results_tweet = Tweet.objects.all()
        query_post = request.GET.get("q")
        query_tagged = request.GET.get("q")
        query_tweet = request.GET.get("q")
        if query_post or query_tweet:
            workspaces = workspaces.filter(Q(extracao_facebook__icontains=query_post)).distinct()
            workspaces_tweet = workspaces.filter(Q(extracao_twitter__icontains=query_tweet)).distinct()
            results_post = results_post.filter(Q(post_id__icontains=query_post)).distinct()
            results_tweet = results_tweet.filter(Q(tweet_id__icontains=query_tweet)).distinct()
            return render(request, 'extracao/index.html', {
                'workspaces': workspaces,
                'posts_post': results_post,
                'posts_tagged': results_tagged,
                'tweets': workspaces,
            })
        else:
            return render(request, 'extracao/index.html', {'workspaces': workspaces}, {'tweets':workspaces})

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'extracao/login.html', context)

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                workspaces = Workspace.objects.filter(user=request.user)
                return render(request, 'extracao/index.html', {'workspaces': workspaces})
            else:
                return render(request, 'extracao/login.html', {'error_message': 'Sua conta foi desativada'})
        else:
            return render(request, 'extracao/login.html', {'error_message': 'Login invalido'})
    return render(request, 'extracao/login.html')

def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                workspaces = Workspace.objects.filter(user=request.user)
                return render(request, 'extracao/index.html', {'workspaces': workspaces})
    context = {
        "form": form,
    }
    return render(request, 'extracao/register.html', context)

def create_twitter_post(request, workspace_id):
    form = TwitterPostForm(request.POST or None)
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    if form.is_valid():  
        pesquisa = form.save(commit=False)
        
        pesquisa.termo_consulta = form.cleaned_data['termo_consulta']   
        pesquisa.workspace_id = workspace_id             
        
        termo=pesquisa.termo_consulta
        ckey=workspace.ckey
        csecret=workspace.csecret
        asecret=workspace.asecret
        atoken=workspace.atoken
        
        pesquisa.save()
    
        class Twitter_Thread (threading.Thread):
            def __init__(self, termo, ckey, csecret, atoken, asecret):
                threading.Thread.__init__(self)
                self.termo =termo
                self.ckey= ckey
                self.csecret=csecret
                self.atoken=atoken
                self.asecret=asecret
            
            def run(self):
                print ("Starting " + self.termo)
                extrai_twitter(self.termo, self.ckey, self.csecret, self.atoken, self.asecret)
                print ("Exiting " + self.termo)
        
        def extrai_twitter(termo, ckey, csecret, atoken, asecret):
            main_twitter(termo, ckey, csecret, atoken, asecret)
                
        thread_tweet = Twitter_Thread(termo, ckey, csecret, atoken, asecret)    
        thread_tweet.start()
        
        return render(request, 'extracao/detail.html', {'workspace': workspace})
                
    context = {
        'workspace': workspace,
        'form': form,
    }
    return render(request, 'extracao/create_twitter_post.html', context)

def processing_twitter_post(request, workspace_id):
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    
    class Twitter_Thread (threading.Thread):
        def __init__(self, workspace_id):
            threading.Thread.__init__(self)
            self.workspace_id=workspace_id
            
        def run(self):
            print ("Starting Processamento")
            processa_twitter(self.workspace_id)
            print ("Exiting Processamento")
    
    def processa_twitter(workspace_id):
        process_tweet(workspace_id)
            
    thread_tweet = Twitter_Thread(workspace_id)    
    thread_tweet.start()
    
    return render(request, 'extracao/detail_process.html', {'workspace': workspace})

def create_facebook_post(request, workspace_id):
    form_fanp = FacebookFanpageForm(request.POST or None)
    form_post = FacebookPostForm(request.POST or None)
    
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    if form_fanp.is_valid() and form_post.is_valid():
        
        postagem = form_post.save(commit=False)
        fanp = form_fanp.save(commit=False)

        page = form_fanp.cleaned_data['page']
                
        tipo_extracao = form_post.cleaned_data['tipo_extracao']     
        tipo_postagem = workspace.extracao_facebook
        user_token = workspace.user_token
        
        arguments = {}
        try:
            graph = GraphAPI(workspace.user_token)
            graph.get_connections(page, fields_posts, **arguments)
        except Exception as e:
            print("Ocorreu o seginte erro:\n", e)
            if e.code == 190:
                context = {
                    'workspace': workspace,
                    'form_fanp': form_fanp,
                    'form_post': form_post,
                    'error_message': 'Token invalido',
                }
                return render(request, 'extracao/create_facebook_post.html', context)
            elif e.code == 803:
                context = {
                    'workspace': workspace,
                    'form_fanp': form_fanp,
                    'form_post': form_post,
                    'error_message': 'Pagina invalida',
                }
                return render(request, 'extracao/create_facebook_post.html', context)
            elif e.code == 12:
                context = {
                    'workspace': workspace,
                    'form_fanp': form_fanp,
                    'form_post': form_post,
                    'error_message': 'Versão do facebooksdk desatualizada - Envie um e-mail informando.',
                }
                return render(request, 'extracao/create_facebook_post.html', context)
            else:
                context = {
                    'workspace': workspace,
                    'form_fanp': form_fanp,
                    'form_post': form_post,
                    'error_message': 'Erro de extração',
                }
                return render(request, 'extracao/create_facebook_post.html', context)
        
        '''Usada para renderizar página enquando extração fica em bacground'''
        class Facebook_Thread(threading.Thread):
            def __init__(self, page, workspace_id, user_token, tipo_postagem, tipo_extracao):
                threading.Thread.__init__(self)
                self.page = page
                self.workspace_id = workspace_id
                self.user_token = user_token
                self.tipo_postagem = tipo_postagem
                self.tipo_extracao = tipo_extracao
                            
            def run(self):
                print ("Starting " + self.page)
                extrai_facebook(self.page, self.workspace_id, self.user_token, self.tipo_postagem, self.tipo_extracao)
                print ("Exiting " + self.page)
        
        def extrai_facebook(page, workspace_id, user_token, tipo_postagem, tipo_extracao):
            main_facebook(page, workspace_id, user_token, tipo_postagem, tipo_extracao)
        
        thread_face = Facebook_Thread(page, workspace_id, user_token, tipo_postagem, tipo_extracao)
                        
        thread_face.start()
        
        return render(request, 'extracao/detail.html', {'workspace': workspace})
               
    context = {
        'workspace': workspace,
        'form_fanp': form_fanp,
        'form_post': form_post,
    }
    return render(request, 'extracao/create_facebook_post.html', context)

def processing_facebook_post(request, workspace_id):
    workspace = get_object_or_404(Workspace, pk=workspace_id)

    class Facebook_Thread (threading.Thread):
        def __init__(self, workspace_id):
            threading.Thread.__init__(self)
            self.workspace_id=workspace_id
            
        def run(self):
            print ("Starting Processamento")
            processa_facebook(self.workspace_id)
            print ("Exiting Processamento")
    
    def processa_facebook(workspace_id):
        process_face(workspace_id)
            
    thread_face = Facebook_Thread(workspace_id)    
    thread_face.start()
    
    return render(request, 'extracao/detail_process.html', {'workspace': workspace})

def email(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            mesmail = "Mensagem: "+ message + " \nE-mail: " + email  + " \nTelefone:" + phone
            try:
                send_mail(name, mesmail, 'escreva o email aqui',['escreva o email aqui'], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Campo Inválido.')

        return render(request, "index.html")
    
def thanks(request):
    return HttpResponse('Obrigado por sua mensagem!')

def export_process_post(request, tipo):
    if tipo =="csv":
        post_resource = ProcessamentoPostResource()
        dataset = post_resource.export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="postsProcessados.csv"'
        return response
    elif tipo =="json":        
        post_resource = ProcessamentoPostResource()
        dataset = post_resource.export()
        response = HttpResponse(dataset.json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="postsProcessados.json"'
        return response
    elif tipo=="xls":
        post_resource = ProcessamentoPostResource()
        dataset = post_resource.export()
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="postsProcessados.xls"'
        return response
    
def export_process_tweet(request, tipo):
    if tipo =="csv":
        tweet_resource = ProcessamentoTweetResource()
        dataset = tweet_resource.export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tweetsProcessados.csv"'
        return response
    elif tipo =="json":        
        tweet_resource = ProcessamentoTweetResource()
        dataset = tweet_resource.export()
        response = HttpResponse(dataset.json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="tweetsProcessados.json"'
        return response
    elif tipo=="xls":
        tweet_resource = ProcessamentoTweetResource()
        dataset = tweet_resource.export()
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="tweetsProcessados.xls"'
        return response    
        

def testejs(request, workspace_id):
    if not request.user.is_authenticated():
        return render(request, 'extracao/login.html')
    else:
        user = request.user
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        return render(request, 'extracao/testejs.html', {'workspace': workspace, 'user': user})