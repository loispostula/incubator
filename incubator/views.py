from datetime import datetime

from django.views.generic.edit import CreateView
from users.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from actstream.models import Action

from space.djredis import get_redis, space_is_open
from events.models import Event


def home(request):
    client = get_redis()
    stream = []
    if request.user.is_authenticated():
        stream = Action.objects.filter(public=True)
        stream = stream.prefetch_related('target')
        stream = stream.prefetch_related('actor')
        stream = stream.prefetch_related('action_object')
        stream = stream[:20]

    return render(request, "home.html", {
        "space_open": space_is_open(client),
        "message": FlatPage.objects.filter(url="/message/").first(),
        "events": Event.objects.filter(stop__gt=datetime.now(), status__exact="r"),
        "stream": stream,
    })


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = '/'

    def get_initial(self):
        initial = super(RegisterView, self).get_initial()
        initial = initial.copy()
        initial['username'] = self.request.GET.get("username")
        return initial

    def form_valid(self, form):
        ret = super(RegisterView, self).form_valid(form)
        user = form.auth_user()
        if user:
            login(self.request, user)
        return ret
