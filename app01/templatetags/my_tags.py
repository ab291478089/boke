from django import template
from app01 import models
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('left_menu.html')
#左侧导航标签分类
def get_left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 我的文章分类及文章数
    # 先将我的文章进行分类  并统计分类后的文章个数
    category_list = models.Category.objects.filter(Blog=blog).annotate(c=Count('article')).values('title', 'c')
    # 先将我的文章进行分类标签  并统计分类后的文章个数
    tag_list = models.Tag.objects.filter(Blog=blog).annotate(c=Count('article')).values('title', 'c')
    # 时间归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_tm": "date_format(create_time,'%%Y-%%m')"}
    ).values('archive_tm').annotate(c=Count('title')).values('archive_tm', 'c')
    return {
        'category_list': category_list,
        'tag_list': tag_list,
        'archive_list': archive_list,
    }