from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'stopgame.views.home'),
    url(r'^game-configuration/$', 'stopgame.views.game_configuration'),
    url(r'^play/(?P<room_id>\d+)$', 'stopgame.views.game_play'),
    url(r'^pre-play/(?P<room_id>\d+)$', 'stopgame.views.pre_play'),
    url(r'^can-play/(?P<room_id>\d+)$', 'stopgame.views.can_play'),
    url(r'^results/$', 'stopgame.views.results'),
    url(r'^fim/$', 'stopgame.views.end_of_round'),
    url(r'^send-answers/$', 'stopgame.views.receive_ans_ajax'),
    url(r'^everyone-answers/$', 'stopgame.views.everyone_answers'),
    url(r'^rooms/$', 'stopgame.views.rooms'),
    url(r'^enter/(?P<room_id>\d+)$', 'stopgame.views.enter_room'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
