from django.views.generic.base import TemplateResponseMixin, ContextMixin, View

class LegalPagesResponseMixin(TemplateResponseMixin):
    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )


class TemplateView(LegalPagesResponseMixin, ContextMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
