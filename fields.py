from django.db import models
from django import forms
from .widgets import (
    TextInput, TextareaInput, NumberInput, FloatInput, SwitchInput,
    DateInput, TimeInput, EmailInput, DateTimeInputNew, ImageInput,
    ForeignKeyInput, URLInput
)

class CharFormField(forms.fields.CharField):
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = TextInput()
        super(CharFormField, self).__init__(*args, **kwargs)


class UiCharField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {'form_class': CharFormField}
        defaults.update(kwargs)
        return super(UiCharField, self).formfield(**defaults)

class TextFormField(forms.fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = TextareaInput()
        super(TextFormField, self).__init__(*args, **kwargs)

class UiTextField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'form_class': TextFormField}
        defaults.update(kwargs)
        return super(UiTextField, self).formfield(**defaults)
    

class NumberFormField(forms.fields.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = NumberInput()
        super(NumberFormField, self).__init__(*args, **kwargs)


class UiIntegerField(models.IntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': NumberFormField}
        defaults.update(kwargs)
        return super(UiIntegerField, self).formfield(**defaults)


class FloatFormField(forms.fields.FloatField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = FloatInput()
        super(FloatFormField, self).__init__(*args, **kwargs)


class UiFloatField(models.FloatField):
    def formfield(self, **kwargs):
        defaults = {'form_class': FloatFormField}
        defaults.update(kwargs)
        return super(UiFloatField, self).formfield(**defaults)


class SwitchFormField(forms.fields.BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = SwitchInput()
        super(SwitchFormField, self).__init__(*args, **kwargs)


class UiSwitchField(models.BooleanField):
    def formfield(self, **kwargs):
        defaults = {'form_class': SwitchFormField}
        defaults.update(kwargs)
        return super(UiSwitchField, self).formfield(**defaults)


class DateFormField(forms.fields.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DateInput()
        super(DateFormField, self).__init__(*args, **kwargs)


class UiDateField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {'form_class': DateFormField}
        defaults.update(kwargs)
        return super(UiDateField, self).formfield(**defaults)
    
    
class TimeFormField(forms.fields.TimeField):
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = TimeInput(format="%H:%M:%S")
        super(TimeFormField, self).__init__(*args, **kwargs)    


class UiTimeField(models.TimeField):
    
    def formfield(self, **kwargs):
        defaults = {'form_class': TimeFormField}
        defaults.update(kwargs)
        
        return super(UiTimeField, self).formfield(**defaults)


class UiDateTimeFormField(forms.fields.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DateTimeInputNew(format="%Y/%m/%d %H:%M:%S")
        super(UiDateTimeFormField, self).__init__(*args, **kwargs)


class UiDateTimeField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {'form_class': UiDateTimeFormField}
        defaults.update(kwargs)
        return super(UiDateTimeField, self).formfield(**defaults)


class EmailFormField(forms.fields.EmailField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = EmailInput()
        super(EmailFormField, self).__init__(*args, **kwargs)


class UiEmailField(models.EmailField):
    def formfield(self, **kwargs):
        defaults = {'form_class': EmailFormField}
        defaults.update(kwargs)
        return super(UiEmailField, self).formfield(**defaults)

class UiImageInput(ImageInput):
    def __init__(self, *args, **kwargs):
        self.upload_to = kwargs.pop('upload_to', '')  # 获取并移除 upload_to
        super().__init__(*args, **kwargs)
        
class ImageCharFormField(forms.fields.CharField):
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = UiImageInput()
        super(ImageCharFormField, self).__init__(*args, **kwargs)


class UiImageCharField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ImageCharFormField}
        defaults.update(kwargs)
        return super(UiImageCharField, self).formfield(**defaults)


class URLFormField(forms.fields.URLField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = URLInput()
        super(URLFormField, self).__init__(*args, **kwargs)


class UiURLField(models.URLField):
    def formfield(self, **kwargs):
        defaults = {'form_class': URLFormField}
        defaults.update(kwargs)
        return super(UiURLField, self).formfield(**defaults)


class UiForeignKey(ForeignKeyInput):
    def __init__(self, *args, **kwargs):
        self.field_name = kwargs.pop('label', '')  # 获取并移除 upload_to
        self.foreigh_choices = kwargs.pop('foreigh_choices', [])
        super().__init__(*args, **kwargs)
        

class ForeignKeyFormField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        foreigh_choices = []
        try:
            for obj in kwargs.get('queryset'):
                foreigh_choices.append({
                    'label': obj.__str__(),
                    'value': obj.id
                })
            kwargs['widget'] = UiForeignKey(label=kwargs.pop('label', ''), foreigh_choices=foreigh_choices)
        except:
            pass
        
        super(ForeignKeyFormField, self).__init__(*args, **kwargs)


class UiForeignKeyField(models.fields.related.ForeignKey):
    def formfield(self, **kwargs):
        defaults = {'form_class': ForeignKeyFormField}
        defaults.update(kwargs)
        return super(UiForeignKeyField, self).formfield(**defaults)