from django.conf.urls import url  
from django.contrib import admin

from . import views


app_name = 'extracao'

urlpatterns = [
    url(r'^admin/', admin.site.urls),           
    
    url(r'^$', views.index, name='index'),
    
    url(r'^register/$', views.register, name='register'),
    
    url(r'^login_user/$', views.login_user, name='login_user'),
    
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    
    url(r'^(?P<workspace_id>[0-9]+)/$', views.detail, name='detail'),
    
    url(r'^(?P<workspace_id>[0-9]+)/process/$', views.detail_process, name='detail_process'),
      
    url(r'^select_social/$', views.select_social, name='select_social'),
    
    url(r'^add_workspace_facebook/$', views.create_workspace_facebook, name='create_workspace_facebook'),
    
    url(r'^add_workspace_twitter/$', views.create_workspace_twitter, name='create_workspace_twitter'),
    
    url(r'^(?P<workspace_id>[0-9]+)/create_facebook_post/$', views.create_facebook_post, name='create_facebook_post'),
    
    url(r'^(?P<workspace_id>[0-9]+)/create_twitter_post/$', views.create_twitter_post, name='create_twitter_post'),
    
    url(r'^(?P<workspace_id>[0-9]+)/processing_twitter_post/$', views.processing_twitter_post, name='processing_twitter_post'),
    
    url(r'^(?P<workspace_id>[0-9]+)/processing_facebook_post/$', views.processing_facebook_post, name='processing_facebook_post'),
    
    url(r'^(?P<workspace_id>[0-9]+)/delete_post_fanpage/(?P<post_id>[0-9]+)/$', views.delete_post_fanpage, name='delete_post_fanpage'),
    
    url(r'^(?P<workspace_id>[0-9]+)/delete_post_tagged/(?P<tagged_id>[0-9]+)/$', views.delete_post_fanpage, name='delete_post_tagged'),
    
    url(r'^(?P<workspace_id>[0-9]+)/delete_post_tweet/(?P<tweet_id>[0-9]+)/$', views.delete_post_tweet, name='delete_post_tweet'),
         
    url(r'^(?P<workspace_id>[0-9]+)/delete_workspace/$', views.delete_workspace, name='delete_workspace'),
    
    url(r'^(?P<workspace_id>[0-9]+)/update_workspace_facebook/$', views.update_workspace_facebook, name='update_workspace_facebook'),
    
    url(r'^(?P<workspace_id>[0-9]+)/update_workspace_twitter/$', views.update_workspace_twitter, name='update_workspace_twitter'),
      
    url(r'^(?P<tipo>.+)export_process_post/$', views.export_process_post, name='export_process_post'),
    
    url(r'^(?P<tipo>.+)export_process_tweet/$', views.export_process_tweet, name='export_process_tweet'),
    
    url(r'^(?P<workspace_id>[0-9]+)/testejs/$', views.testejs, name='testejs'),   
    
]