from django.shortcuts import render,redirect
from app01 import models
from django.http import HttpResponse,JsonResponse
from geetest import GeetestLib
from app01 import forms
from django.contrib import auth
from django.contrib.auth import authenticate
from django.db.models import Count





# Create your views here.
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"

#首页
def index(request):
    #查询所有文章列表
    article_list = models.Article.objects.all()

    return render(request,'index.html',{'article_list':article_list})

#个人博客配置
def home(request,username):
    #去表里把用户对象取出
    user =  models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('404')
    #如果用户存在 需要列出 他所有文章
    else:
        blog = user.blog
        #我的文章列表
        article_list = models.Article.objects.filter(user=user)
        #我的文章分类及文章数
        #先将我的文章进行分类  并统计分类后的文章个数
        # category_list= models.Category.objects.filter(Blog=blog)

    return render(request,'home.html',{
        'username':username,
        'blog':blog,
        'article_list':article_list,
    })

#文章详情
def article_detail(request,username,pk):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('访问页面不存在！')
    blog = user.blog
    #找到当前我点击的文章
    article = models.Article.objects.filter(pk=pk).first()
    # 所有评论
    comment_list = models.Comment.objects.filter(article_id=pk)

    return render(
        request,'article_detail.html',
        {
        'username':username,
        'article':article,
        'blog':blog,
        'comment_list':comment_list
        })


#点赞
from  django.db.models import F
import json
def up_down(request):
    article_id = request.POST.get('acticle_id')
    #is_up  通过json转变成python规定的bool值
    is_up = json.loads(request.POST.get('is_up'))
    user =request.user  #点赞用户
    response={'state':True}
    try:
        models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
        models.Article.objects.filter(pk=article_id).update(up_count=F('up_count')+1,down_count=F('down_count')+1)
    except Exception as e:
        response['state']=False
        response['action']=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up


    return JsonResponse(response)

#评论
def comment(request):
    parent = request.POST.get('parent')
    comment = request.POST.get('comment')
    article_id = request.POST.get('article_id')
    user_pk = request.user.pk
    response={}

    if not parent: #根评论
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=comment)
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=comment,parent_comment_id=parent)

    response['create_time']=comment_obj.create_time.strftime("%Y-%m-%d")
    response['content']=comment_obj.content
    response['username']=request.user.username
    return JsonResponse(response)


#评论树
def comment_tree(request,article_id):
    ret = list(models.Comment.objects.filter(article_id=article_id).values('pk','parent_comment_id','content'))

    return JsonResponse(ret,safe=False)


#添加文章
def add_article(request):
    if request.method=="GET":
        return render(request,'add_article.html')
    else:
        title = request.POST.get('title')
        article_content = request.POST.get('article_content')
        user = request.user
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(article_content,"html.parser")
        desc = bs.text[0:150]+"..."

        #xss攻击  过滤非法标签
        for tag in bs.find_all():
            if tag.name in ['script','link']:
                tag.decompose()


        article_obj = models.Article.objects.create(title=title,user=user,desc=desc)
        models.ArticleDetail.objects.create(article=article_obj,content=str(bs))  #存储删除非法标签后的文本
        return redirect('/index.html')




#上传图片
from boke import settings
import os
def upload(request):
    obj = request.FILES.get("upload_img")

    path =os.path.join(settings.MEDIA_ROOT,"add_article_img",obj.name)

    with open(path,"wb") as f:
      for line in obj:
          f.write(line)

    res={
         "error":0,
         "url":"/media/add_article_img/"+obj.name
     }



    return HttpResponse(json.dumps(res))



#文章标签列表
def category_list(request,username,pk):
    article2tag = models.Article2Tag.objects.filter(username=username).first()
    if not article2tag:
        return HttpResponse('访问页面不存在！')
    article_list = article2tag.article
    #找到当前我点击的标签
    Tag = models.Article2Tag.objects.filter(pk=pk).first()
    return render(request,'article_list.html',
                  {'username':username,
                   'article_list':article_list,
                   'tag':Tag
                   }
                  )



#注销
def logout(request):
    auth.logout(request)
    return redirect('index.html')



#登陆
def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    else:
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        u =  request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(username=u,password=pwd)
        if status:
            result = gt.success_validate(challenge, validate, seccode)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if user:
            auth.login(request,user)   #将登录赋值给user
            return redirect('index.html')
        else:
            return render(request,'login.html',{'msg':'用户名或密码错误'})

#注册账号
def register(request):
    if request.method =='POST':
        ret ={'status':0,'msg':''}
        obj = forms.RegForm(request.POST)
        #帮我校验
        if obj.is_valid():
            #删除数据
            obj.cleaned_data.pop('re_password')
            #接受头像
            avatar_img = request.FILES.get('avatar')
            #校验通过
            models.UserInfo.objects.create_user(**obj.cleaned_data,avatar=avatar_img)
            ret['msg']='login.html'
            return JsonResponse(ret)
        else:
            print(obj.errors)
            ret['status']=1
            ret['msg']=obj.errors
            return JsonResponse(ret)
    #生成form
    obj = forms.RegForm()
    return render(request,'register.html',{'obj':obj})

#校验用户名是否已经注册
def check_username(request):
    ret={'status':0,'msg':""}
    username = request.GET.get('username')
    print(username)
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret['status']=1
        ret['msg']='用户名已被注册！'
    return JsonResponse(ret)


#获取验证码
#处理极验验证码视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)



