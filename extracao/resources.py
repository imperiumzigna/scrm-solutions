from import_export import resources
from .models import Processamento_post
from .models import Processamento_tweet

class ProcessamentoPostResource(resources.ModelResource):
    class Meta:
        model = Processamento_post
        
class ProcessamentoTweetResource(resources.ModelResource):
    class Meta:
        model = Processamento_tweet