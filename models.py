from django.db import models
from .fields import *
from .fields import UiDateTimeField
from django.db.models.fields.files import FileField

class AdminMenus(models.Model):
    
    STATUS_CHOICES = (
        ('1', '正常'),
        ('2', '禁用'),
    )
    ACTIVE_CHOICES = (
        (1, '是'),
        (2, '否'),
    )
    
    name = UiCharField(max_length=100, verbose_name='菜单名称' )
    url = UiCharField(verbose_name='菜单链接', max_length=255,)
    icon = UiCharField(max_length=100, verbose_name='菜单图标icon', null=True, blank=True,)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父级菜单')
    sort = UiIntegerField(verbose_name='排序', null=True, blank=True, default=0)
    status = models.CharField(max_length=100, default='1', choices=STATUS_CHOICES, verbose_name='状态', null=True, blank=True,)
    active = models.IntegerField(default=1, choices=ACTIVE_CHOICES, verbose_name='是否激活')
    is_show = UiSwitchField(verbose_name='是否显示', null=True, blank=True,)
    
    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'System菜单设置'
        verbose_name_plural = 'System菜单设置'
        ordering = ['sort']


## 创建一个model，需要包含所有字段类型
class ExampleModel(models.Model):
    title = UiCharField(max_length=200, default='', verbose_name='标题')
    description = UiTextField(default='', null=True, blank=True, verbose_name='描述')
    count = UiIntegerField(default=0, verbose_name='计数')
    price = UiFloatField(default=0.0, verbose_name='价格')
    amount = UiFloatField(default=0.0, verbose_name='金额')
    is_active = UiSwitchField(default=True, verbose_name='是否激活')
    birth_date = UiDateField(null=True, blank=True, verbose_name='出生日期')
    start_time = UiTimeField(null=True, blank=True, verbose_name='开始时间')
    created = UiDateTimeField(null=True, blank=True, verbose_name='创建时间')
    email = UiEmailField(default='', null=True, blank=True, verbose_name='电子邮件')
    website = UiURLField(default='', null=True, blank=True, verbose_name='网站')
    # file_test = models.FileField(upload_to='upload/', null=True, blank=True, default='', verbose_name='文件')
    image = UiImageCharField(max_length=200, default='', null=True, blank=True, verbose_name='图片')
    adminmenus = UiForeignKeyField(AdminMenus, on_delete=models.CASCADE, null=True, blank=True, verbose_name='菜单')
    # adminmenus1 = models.ForeignKey(AdminMenus, on_delete=models.CASCADE, null=True, blank=True, verbose_name='菜单')
    # test_field = models.CharField(max_length=200, default='', null=True, blank=True, verbose_name='测试字段')
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '示例模型'
        verbose_name_plural = '示例模型'
        

class ExampleItem(models.Model):
    item = UiForeignKeyField(ExampleModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name='示例模型')
    title = UiCharField(max_length=200, default='', verbose_name='标题')
    price = UiFloatField(default=0.0, verbose_name='价格')
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '示例模型item'
        verbose_name_plural = '示例模型item'

   
import os
import uuid
import time
def get_product_image_upload_path(instance, filename):
    # return os.path.join('photos', str(instance.id), filename)
    fn, ext = os.path.splitext(filename)
    if not ext:
        ext = '.jpg'
    # name = time.strftime('%y-%m/%d',time.localtime(time.time()))
    name = str(uuid.uuid4())
    return os.path.join('pimg', name[0:3], name[3:] + ext)
   
class DemoModel(models.Model):
    title = models.CharField(max_length=200, default='', verbose_name='标题')
    description = models.TextField(default='', verbose_name='描述')
    count = models.IntegerField(default=0, verbose_name='计数')
    price = models.FloatField(default=0.0, verbose_name='价格')
    amount = models.FloatField(default=0.0, verbose_name='金额')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    start_time = models.TimeField(null=True, blank=True, verbose_name='开始时间')
    created = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    email = models.EmailField(default='', null=True, blank=True, verbose_name='电子邮件')
    website = models.URLField(default='', null=True, blank=True, verbose_name='网站')
    image = models.ImageField(upload_to=get_product_image_upload_path, null=True, blank=True, default='', verbose_name='图片')
    adminmenus = models.ForeignKey(AdminMenus, on_delete=models.CASCADE, null=True, blank=True, verbose_name='菜单')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = '示例模型admin'
        verbose_name_plural = '示例模型admin'


class DemoModelItem(models.Model):
    item = models.ForeignKey(DemoModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name='示例模型')
    title = models.CharField(max_length=200, default='', verbose_name='标题')
    price = models.FloatField(default=0.0, verbose_name='价格')
    
    def __str__(self):
        return self.title
    
class DemoModelItem2(models.Model):
    item = models.ForeignKey(DemoModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name='示例模型')
    title = models.CharField(max_length=200, default='', verbose_name='标题')
    price = models.FloatField(default=0.0, verbose_name='价格')
    
    def __str__(self):
        return self.title
