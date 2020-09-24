from django.http import HttpResponseRedirect

class IsAlreadyAuthenticatedMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)
