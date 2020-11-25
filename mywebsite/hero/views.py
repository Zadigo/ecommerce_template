from django.views.generic import TemplateView

class HeroView(TemplateView):
    template_name = 'pages/hero.html'
