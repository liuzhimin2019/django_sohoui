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
## 8、组件
统一引入：from django_sohoui.fields import *
效果：查看预览中adminform

### 输入框
类型：继承models.CharFiled
使用：UiCharField
案例：title = UiCharField(max_length=200, default='', verbose_name='标题')

### 文本框
类型：继承models.CharField
使用：UiTextField
案例：description = UiTextField(default='', null=True, blank=True, verbose_name='描述')

### 计数器
类型：继承models.IntegerField
使用：UiIntegerField
案例：count = UiIntegerField(default=0, verbose_name='计数')

## 浮点数
类型：继承models.FloatField
使用：UiFloatField
案例：price = UiFloatField(default=0.0, verbose_name='价格')

### 开关
类型：继承models.BooleanField
使用：UiSwitchField
案例：is_active = UiSwitchField(default=True, verbose_name='是否激活')

### 日期筛选器
类型：继承models.DateField
使用：UiDateField
案例：birth_date = UiDateField(null=True, blank=True, verbose_name='出生日期')

### 时间筛选器
类型：继承models.TimeField
使用：UiTimeField
案例：start_time = UiTimeField(null=True, blank=True, verbose_name='开始时间')

### 日期和时间
类型：继承models.DateTimeField
使用：UiDateTimeField
案例：created = UiDateTimeField(null=True, blank=True, verbose_name='创建时间')

### 邮箱
类型：继承models.EmailField
使用：UiEmailField
案例：email = UiEmailField(default='', null=True, blank=True, verbose_name='电子邮件')

### url连接
类型：继承models.URLField
使用：UiURLField
案例：website = UiURLField(default='', null=True, blank=True, verbose_name='网站')

### 图片
类型：继承models.TextField
使用：UiImageCharField
案例：image = UiImageCharField(max_length=200, default='', null=True, blank=True, verbose_name='图片')

### 外建
类型：继承models.fields.related.ForeignKey
使用：UiForeignKeyField
案例：adminmenus = UiForeignKeyField(AdminMenus, on_delete=models.CASCADE, null=True, blank=True, verbose_name='菜单')


## 9、预览

![登录页](https://admin.etcpu.com/static/img/login2.png)


![index](https://admin.etcpu.com/static/img/index.png)

![adminlist](https://admin.etcpu.com/static/img/adminlist.png)

![adminform](https://admin.etcpu.com/static/img/adminform.png)

