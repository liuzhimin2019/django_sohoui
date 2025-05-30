django admin ui 

## 1、在INSTALLED_APPS中添加django_sohoui

```
INSTALLED_APPS = [
    'django_sohoui',
    'django.contrib.admin',
    ....
]
```
## 2、克隆静态资源到项目的静态目录
```
python manage.py collectstatic
```
## 3、执行makemigrations

```
python manage.py makemigrations
python manage.py migrate      
```      

## 4、在TEMPLATES中添加context_processor 

```
'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    ## 添加custom_context
    'django_sohoui.context_processors.custom_context',
]
```

## 5、在project/urls.py中添加django_sohoui
```
from django_sohoui.adminsite import adminsite
urlpatterns = [
    ## 添加django_sohoui
    path('admin/', adminsite.urls),
    path('django_sohoui/', include('django_sohoui.urls')),
]

```
## 6、 在project/settings.py中添加LOGIN_BG_IMAGE(自定义登录页背景图片)

```
SOHO_LOGIN_BG_IMAGE = '/static/custom/images/logo_bg.jpg'
```


## 7、 在project/settings.py中添加SOHO_MENU_LIST

```
SOHO_MENU_LIST = {
    'show_system_menu': True,
    'models':[
        {
            'name': '自定义页面',
            'models':[
                {
                    'name': '自定义页面',
                    'admin_url': '/django_sohoui/custom_url/'
                }
            ],
        }
    ]
}

X_FRAME_OPTIONS = 'SAMEORIGIN'

# 配置首页路由地址
LOGIN_REDIRECT_URL = '/django_sohoui/home/'
```

## 8、预览

![登录页](assets/WX20250530-094921.png)


![index](assets/index.png)

![adminlist](assets/adminlist.png)

![adminform](assets/adminform.png)

