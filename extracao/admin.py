from django.contrib import admin

from .models import Workspace, Fanpage, Post, Post_comment, Post_like, Post_reaction, \
                    Processamento_post, Processamento_comment, Tagged, Tweet


class FacebookWorkspaceAdmin(admin.ModelAdmin):
    model = Workspace
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('user','extracao_facebook','user_token','extracao_twitter','ckey','csecret','atoken','asecret')
    
    list_filter = ()
    # pesquisa em campos
    search_fields = ()
    
admin.site.register(Workspace, FacebookWorkspaceAdmin)

class FacebookFanpageAdmin(admin.ModelAdmin):
    model = Fanpage
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('workspace','page')
    
    list_filter = ('workspace','page')
    # pesquisa em campos
    search_fields = ('workspace','page')
    
admin.site.register(Fanpage, FacebookFanpageAdmin)

class FacebookPostAdmin(admin.ModelAdmin):
    model = Post
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('workspace','page')
    
    list_filter = ('workspace','page')
    # pesquisa em campos
    search_fields = ('workspace','page')
    
admin.site.register(Post, FacebookPostAdmin)

class FacebookPostCommentAdmin(admin.ModelAdmin):
    model = Post_comment
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('post','message')
    
    list_filter = ('post','message')
    # pesquisa em campos
    search_fields = ('post','message')
    
admin.site.register(Post_comment, FacebookPostCommentAdmin)

class FacebookPostLikeAdmin(admin.ModelAdmin):
    model = Post_like
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('post','name_user')
    
    list_filter = ('post','name_user')
    # pesquisa em campos
    search_fields = ('post','name_user')
    
admin.site.register(Post_like, FacebookPostLikeAdmin)

class FacebookPostReactionAdmin(admin.ModelAdmin):
    model = Post_reaction
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('post','name_user')
    
    list_filter = ('post','name_user')
    # pesquisa em campos
    search_fields = ('post','name_user')

admin.site.register(Post_reaction, FacebookPostReactionAdmin)

class FacebookProcessamentoPostAdmin(admin.ModelAdmin):
    model = Processamento_post
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('page','post','message')
    
    list_filter = ('page','post','message')
    # pesquisa em campos
    search_fields = ('page','post','message')
    
admin.site.register(Processamento_post, FacebookProcessamentoPostAdmin)

class FacebookProcessamentoCommentAdmin(admin.ModelAdmin):
    model = Processamento_comment
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ('page','comment','message')
    
    list_filter = ('page','comment','message')
    # pesquisa em campos
    search_fields = ('page','comment','message')
    
admin.site.register(Processamento_comment, FacebookProcessamentoCommentAdmin)    
    
class FacebookTaggedAdmin(admin.ModelAdmin):
    model = Tagged
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ()
    
    list_filter = ()
    # pesquisa em campos
    search_fields = ()
    
admin.site.register(Tagged, FacebookTaggedAdmin)

class TweetPostAdmin(admin.ModelAdmin):
    model = Tweet
    # exclui campos de cadastro
    exclude = ()
    # nao permite edicao de campos
    readonly_fields = ()
    #date_hierarchy = 'criacao'
    list_display = ()
    
    list_filter = ()
    # pesquisa em campos
    search_fields = ()
    
admin.site.register(Tweet, TweetPostAdmin)
