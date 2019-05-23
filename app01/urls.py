from django.conf.urls import url
from app01 import views


urlpatterns = [
    url(r'add_article/',views.add_article),
        #点赞url
    url(r'up_down/',views.up_down),
    #评论
    url(r'comment/',views.comment),
    url(r'comment_tree/(\d+)/',views.comment_tree),
    #三合一url
    url(r'(\w+)/(tag|category|archive)/(.+)/',views.home),
    url(r'(\w+)/article/(\d+)/$', views.article_detail),  # 文章详情页
    url(r'(\w+)',views.home ),  #?P<xxx>关键字参数



]