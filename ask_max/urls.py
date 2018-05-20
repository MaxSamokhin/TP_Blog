"""ask_max URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    url(r'^ask/?', views.ask, name='ask'),
    url(r'^login/?', views.login, name='login'),
    url(r'^signup/?', views.signup, name='signup'),
    url(r'^hot/?', views.hot, name='hot'),
    url(r'^question/(?P<question_id>\d+)/?$', views.question, name='question'),
    url(r'^settings/?', views.settings.as_view(), name='settings'),
    url(r'^tag/(?P<tag>\w+)/?$', views.tag, name='tag'),

    url(r'^/?$', views.base, name='base'),
    url(r'^getpost/', views.getpost),
    url(r'^admin/', admin.site.urls),
    url(r'^logout/?$', views.logout, name = 'logout'),



    url(r'^question/like/(?P<id>\d+)/?$', views.ajax_question_like, name='ajax_question_like'),
    url(r'^answer/like/(?P<id>\d+)/?$', views.ajax_answer_like, name='ajax_answer_like'),
    url(r'^answer/vote/(?P<id>\d+)/?$', views.ajax_answer_correct, name='ajax_answer_correct')
]
if settings.DEBUG is False:
    urlpatterns += [url(r'^uploads/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, })]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
