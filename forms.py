from django import forms
from .models import *
# from .widgets import *
import os
from project.settings import BASE_DIR
from .widgets import ForeignKeyInput

from django.contrib.admin.helpers import AdminReadonlyField
from django_sohoui import fields as sohoui_fields
from django_sohoui import widgets as sohoui_widgets


class UIBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        print(self.current_user)
        print('UIBaseForm')
        ## 当页面只读时，获取base_fields, 获取model所有字段，并添加对应的FormField
        for field in self._meta.model._meta.fields:
            # 判断field是否是sohoui_fields
            if field.__class__.__module__ == 'django_sohoui.fields':
                if isinstance(field, sohoui_fields.UiCharField):
                    self.base_fields[field.name] = sohoui_fields.CharFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiTextField):
                    self.base_fields[field.name] = sohoui_fields.TextFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiForeignKeyField):
                    self.base_fields[field.name] = sohoui_fields.ForeignKeyFormField(queryset=field.related_model.objects.all(), required=not field.blank)
                elif isinstance(field, sohoui_fields.UiURLField):
                    self.base_fields[field.name] = sohoui_fields.URLFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiIntegerField):
                    self.base_fields[field.name] = sohoui_fields.NumberFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiFloatField):
                    self.base_fields[field.name] = sohoui_fields.FloatFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiSwitchField):
                    self.base_fields[field.name] = sohoui_fields.SwitchFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiDateField):
                    self.base_fields[field.name] = sohoui_fields.DateFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiTimeField):
                    self.base_fields[field.name] = sohoui_fields.TimeFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiDateTimeField):
                    self.base_fields[field.name] = sohoui_fields.UiDateTimeFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiEmailField):
                    self.base_fields[field.name] = sohoui_fields.EmailFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiImageCharField):
                    self.base_fields[field.name] = sohoui_fields.ImageCharFormField(required=not field.blank)
                elif isinstance(field, sohoui_fields.UiForeignKeyField):
                    self.base_fields[field.name] = sohoui_fields.ForeignKeyFormField(required=not field.blank)
                    self.base_fields[field.name].queryset = field.related_model.objects.all()
            # else:
            #     # 根据base_fields的类型，设置对应的formfield
            #     field_type = type(field)
            #     form_field_class = getattr(forms, field_type.__name__, forms.CharField)
            #     self.base_fields[field.name] = form_field_class()
            
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.field_name = self._meta.model._meta.get_field(field).verbose_name
            self.fields[field].field_name = self._meta.model._meta.get_field(field).verbose_name
            self.fields[field].widget.class_name = self._meta.model._meta.get_field(field).name
            if self.has_change_permission:
                self.fields[field].widget.el_disabled = False
                if field in self.readonly_fields:
                    self.fields[field].widget.el_disabled = True
                else:
                    self.fields[field].widget.el_disabled = False
            else:
                self.fields[field].widget.el_disabled = True
            

                
class AdminMenusForm(UIBaseForm):
   
    class Meta:
        model = AdminMenus
        fields = '__all__'
      

class ExampleModelForm(UIBaseForm):

    class Meta:
        model = ExampleModel
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      

class DemoModelForm(UIBaseForm):
    class Meta:
        model = DemoModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ## 获取提交内容
        # if self.is_bound:
        #     for field in self.fields:
        #         self.fields[field].initial = self.data.get(field)
               
               