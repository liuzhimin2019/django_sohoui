from django.conf import settings    


def custom_context(request):
    return {
        ## 可能没有设置，添加默认值             
        'LOGIN_BG_IMAGE': getattr(settings, 'SOHO_LOGIN_BG_IMAGE', '/static/django_sohoui/images/logo_bg.jpg'),
        'SOHO_SITE_IMAGE': getattr(settings, 'SOHO_SITE_IMAGE', '/static/ui_template/images/soho_logo.jpg'),
    }
