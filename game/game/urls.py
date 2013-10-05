from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'stopgame.views.home'),
    url(r'^game-configuration/$', 'stopgame.views.game_configuration'),
    url(r'^play/$', 'stopgame.views.game_play'),
    url(r'^results/$', 'stopgame.views.results'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
