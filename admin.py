from django.contrib import admin
from .adminsite import adminsite, BaseAdmin   
from .models import *
from .forms import *
from django.db import models
from django.contrib import messages
import csv 
from io import StringIO
from django.http import HttpResponse

class AdminMenusAdmin(BaseAdmin):
    
    form = AdminMenusForm
    list_per_page = 2
    list_display = ('name', 'url', 'icon', 'parent', 'sort', 'is_show', 'status', 'active')
    list_filter = ('parent', 'is_show', 'status', 'active')
    search_fields = ('name', 'url')
    ordering = ('sort',)
    autocomplete_fields = ['parent']

adminsite.register(AdminMenus, AdminMenusAdmin)



class ExampleItemInline(admin.TabularInline):
    model = ExampleItem
    extra = 1
    


class ExampleModelAdmin(BaseAdmin):
    
    form = ExampleModelForm
    list_per_page = 20
    
 
    @admin.display(description='图片1')
    def show_image(self, obj):
        if obj.image:
            image_list = obj.image.split(',')
            return f'<img src="{image_list[0]}" style="width: 100px; height: 100px;" />'
        else:
            return ''
        
    def updatge_is_active(self, request, queryset):
        for obj in queryset:
            if obj.is_active:
                obj.is_active = False
            else:
                obj.is_active = True
            obj.save()
        messages.success(request, '已成功提交激活/关闭信息！')
    
    updatge_is_active.short_description = '激活/关闭'
    updatge_is_active.type = 'success'
    updatge_is_active.icon = 'fas fa-solid fa-file-alt'
    
    def export_excel(self, request, queryset):
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(['标题', '描述', '数量', '价格', '金额'])
        for obj in queryset:
            writer.writerow([obj.title, obj.description, obj.count, obj.price, obj.amount])
        response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=example_model.csv'
        return response
    
    export_excel.short_description = '导出Excel'
    export_excel.type = 'warning'
    export_excel.icon = 'el-icon-share'
    
    list_display = (
        'title', 'description', 'count',  'amount', 'price', 'is_active',
        'birth_date', 'start_time', 'email', 'website', 'show_image'
    )
    list_filter = ('is_active',)
    search_fields = ('title', )
    ordering = ('-price',)
    actions = ['updatge_is_active', 'export_excel']
    inlines = [ExampleItemInline, ]

adminsite.register(ExampleModel, ExampleModelAdmin)


class DemoModelItemInline(admin.TabularInline):
    model = DemoModelItem
    extra = 0
    
class DemoModelItemInline2(admin.TabularInline):
    model = DemoModelItem2
    extra = 0

class DemoModelAdmin(BaseAdmin):
    
    form = DemoModelForm
    
    def export_excel(self, request, queryset):
        return ''
    export_excel.short_description = '导出Excel'
    export_excel.type = 'success'
    list_display = (
        'title', 'description', 'count', 'price', 'amount', 'is_active', 'adminmenus', 'birth_date', 'start_time', 'email', 'website', 'image'
    )
    list_filter = ('is_active',)
    search_fields = ('title', )
    actions = ['export_excel', ]
    autocomplete_fields = ['adminmenus']
    inlines = [DemoModelItemInline, DemoModelItemInline2]

adminsite.register(DemoModel, DemoModelAdmin)