from django.core.urlresolvers import reverse, resolve
from django.conf import settings

from models import MP
from pombola.core.models import Person


def process(request):
    rs = resolve(request.path_info)
    if rs.url_name is 'person':
        slug = rs.kwargs['slug']

        try:
            person = Person.objects.get(slug=slug)
            return dict(mp=MP.objects.get(person=person))
        except:
            pass
    return {}


def add_ghost(request):
    return {
            'ghost': {
                'URL': settings.GHOST_BLOG_FEED,
                'SECRET': settings.GHOST_BLOG_SECRET
            }
    }
