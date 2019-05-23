//登陆界面JS
var handlerEmbed = function (captchaObj) {
    $("#embed-submit").click(function (e) {
        var validate = captchaObj.getValidate();
        if (!validate) {
            $("#notice")[0].className = "show";
            setTimeout(function () {
                $("#notice")[0].className = "hide";
            }, 2000);
            e.preventDefault();
        }
    });
    // 将验证码加到id为captcha的元素里，同时会有三个input的值：geetest_challenge, geetest_validate, geetest_seccode
    captchaObj.appendTo("#embed-captcha");
    captchaObj.onReady(function () {
        $("#wait")[0].className = "hide";
    });
    // 更多接口参考：http://www.geetest.com/install/sections/idx-client-sdk.html
};
$.ajax({
    // 获取id，challenge，success（是否启用failback）
    url: "/pc-geetest/register?t=" + (new Date()).getTime(), // 加随机数防止缓存
    type: "get",
    dataType: "json",
    success: function (data) {
        // 使用initGeetest接口
        // 参数1：配置参数
        // 参数2：回调，回调的第一个参数验证码对象，之后可以使用它做appendTo之类的事件
        initGeetest({
            gt: data.gt,
            challenge: data.challenge,
            product: "embed", // 产品形式，包括：float，embed，popup。注意只对PC版验证码有效
            offline: !data.success // 表示用户后台检测极验服务器是否宕机，一般不需要关注
            // 更多配置参数请参见：http://www.geetest.com/install/sections/idx-client-sdk.html#config
        }, handlerEmbed);
    }
});


//注册页面JS
//找到头像的input标签绑定change事件
$('#id_avatar').change(function () {
    //创建一个读取文件的对象
    var fileReader = new FileReader();
    //读取当前选中的头像文件
    console.log(this.files[0]);
    //读取你选中的文件
    fileReader.readAsDataURL(this.files[0]);//读取文件需要时间
    //文件读取完之后才能加载出来
    fileReader.onload = function () {
        //加载到img标签中
        $('#avatar_img').attr("src", fileReader.result);
    };
});

//Ajax提交注册数据
$('#reg_submit').click(function () {
    //取到提取数据向后端发送数据
    var formData = new FormData();
    formData.append("username", $("#id_username").val());
    formData.append("password", $("#id_password").val());
    formData.append("re_password", $("#id_re_password").val());
    formData.append("email", $("#id_email").val());
    formData.append("avatar", $("#id_avatar")[0].files[0]);
    // formData.append("csrfmiddlewaretoken",$("[name='csrfmiddlewaretoken']").val());

    $.ajax({
        url: '/register.html',
        type: 'POST',
        processData: false,  //告诉JQuery不要处理我的数据
        contentType: false,   //告诉Jquery不要设置content类型
        data: formData,
        success: function (data) {
            if (data.status) {
                //有错误展示错误
                //console.log(data.msg);
                // 返回的是一个对象   将报错信息填写出来
                $.each(data.msg, function (k, v) {
                    //console.log("id_"+k,v[0]);
                    $('#id_' + k).next('span').text(v[0]).parent().parent().addClass("has-error")
                })
            } else {
                //没有就跳转到指定页面
                location.href = data.msg;
            }
        }
    })
});

//将所有input绑定获取焦点的事件，将所有错误信息清空
$('form input').focus(function () {
    $(this).next().text("").parent().parent().removeClass("has-error");
});


//给username  input绑定失去焦点的事件，失去之后校验用户名是否已被注册
$('#id_username').on('input', function () {
    //取到用户填写的值
    var username = $(this).val();
    //发请求
    $.ajax(
        {
            url: '/check_username',
            type: 'get',
            data: {'username': username},
            success: function (data) {
                if (data.status) {
                    //用户已注册
                    $('#id_username').next().text(data.msg).parent().parent().addClass("has-error");
                }

            }

        }
    )
});

//文章详情页中的点赞踩JS
$('#div_digg .action').click(function () {
    //判断用户是否登录
    if ($('.info').attr('username')) {
        //点赞或熄灭
        var is_up = $(this).hasClass('diggit');
        var acticle_id = $('.info').attr('article_id');

        $.ajax({
            url: '/blog/up_down/',
            type: 'post',
            data: {
                is_up: is_up,
                acticle_id: acticle_id
            },
            success: function (data) {
                console.log(data);
                //如果赞或灭成功
                if (data.state) {
                    //如果点击赞
                    if (is_up) {
                        var val = $('#digg_count').text();
                        val = parseInt(val) + 1;
                        //将val赋值给图标
                        $('#digg_count').text(val);

                    } else {
                        var cal = $('#bury_count').text();
                        cal = parseInt(cal) + 1;
                        //将val赋值给图标
                        $('#bury_count').text(cal);
                    }


                }
                //重复提交
                else {

                    if (data.action) {
                        $('#digg_tips').html("您已经推荐过");


                    } else {
                        $('#digg_tips').html("您已经反对过");
                    }

                    //1秒过后消失
                    setTimeout(function () {
                        $('#digg_tips').html("")
                    }, 1000)
                }
            }
        })
    }
//没登录
    else {
        location.href = '/login.html'
    }

});












