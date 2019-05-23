"""boke URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url,include
from app01 import views
from app01 import urls as blog_urls
from django.views.static import serve #需要导入
from boke import settings


urlpatterns = [
    url(r'^admin/',(admin.site.urls)),

    url(r'^index.html$',(views.index)),
    url(r'^register.html$',(views.register)),
    url(r'^login.html$', (views.login)),
    url(r'^logout.html$', (views.logout)),

#将所有以blog开头的url 都交给app01下的urls.py处理
    url(r'^blog/',include(blog_urls)),

    url(r'^check_username$',(views.check_username)),


    url(r'^pc-geetest/register', (views.get_geetest)),

    url(r'^upload/', (views.upload)),

    url(r'^media/(?P<path>.*)$', serve, {'document_root':settings.MEDIA_ROOT}),#这部分很重要


]
