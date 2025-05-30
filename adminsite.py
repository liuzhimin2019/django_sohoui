from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy

from django.conf import settings
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.urls import reverse, NoReverseMatch
from django.utils.text import capfirst
from django.apps import apps
import datetime
import copy
from django.contrib.admin import helpers, widgets
from .fields import *
from django.db.models.fields import *
from django.db.models.fields.files import ImageField
from django.db.models import ForeignKey
from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import unquote
from django.contrib.admin.options import get_content_type_for_model
from django.shortcuts import redirect

class NotRegistered(Exception):
    pass



icon_dict = {
    '首页': 'fas fa-solid fa-house',
    '认证和授权': 'fas fa-solid fa-user',
    '用户': 'fas fa-solid fa-user',
    '组': 'fas fa-solid fa-users',
    '菜单': 'fas fa-solid fa-bars',
    '权限': 'fas fa-solid fa-key',
    '角色': 'fas fa-solid fa-user-tag',
    '日志': 'fas fa-solid fa-file-alt',
    '示例模型': 'fas fa-solid fa-file-alt',
}

class MyAdminSite(admin.AdminSite):

    # URL for the "View site" link at the top of each admin page.
    site_url = "/"

    enable_nav_sidebar = True

    # 登录页&首页的标题
    site_header = '登录页&首页的标题'
    # 浏览器的标题
    site_title = '浏览器的标题'
    # 正文的标题
    index_title = '正文的标题'
    
    index_template = 'admin/index.html'
    # index_template = 'admin/index.html'
    
    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {
                m: m_a
                for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry
        for model, model_admin in models.items():
            app_label = model._meta.app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                "model": model,
                "name": capfirst(model._meta.verbose_name_plural),
                "object_name": model._meta.object_name,
                "perms": perms,
                "admin_url": None,
                "add_url": None,
            }
            if perms.get("change") or perms.get("view"):
                model_dict["view_only"] = not perms.get("change")
                try:
                    model_dict["admin_url"] = reverse(
                        "admin:%s_%s_changelist" % info, current_app=self.name
                    )
                except NoReverseMatch:
                    pass
            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse(
                        "admin:%s_%s_add" % info, current_app=self.name
                    )
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]["models"].append(model_dict)
            else:
                app_dict[app_label] = {
                    "name": apps.get_app_config(app_label).verbose_name,
                    "app_label": app_label,
                    "app_url": reverse(
                        "admin:app_list",
                        kwargs={"app_label": app_label},
                        current_app=self.name,
                    ),
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        return app_dict
    
    
    def get_app_list(self, request, app_label=None):
    
        app_dict = self._build_app_dict(request, app_label)
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
        ## 插入首页
        app_list.insert(0, {
            'name': '首页',
            'icon': icon_dict.get('首页', '') if icon_dict.get('首页', '') else icon_dict.get('首页', ''),
            'admin_url': settings.LOGIN_REDIRECT_URL
        })
        
        # Sort the models alphabetically within each app.
        # for app in app_list:
        #     app["models"].sort(key=lambda x: x["name"])
        for app in app_list:
            app['icon'] = icon_dict.get(app['name'], '') if icon_dict.get(app['name'], '') else icon_dict.get(app['name'], '')
            if app.get('models', []):
                for model in app['models']:
                    model['icon'] = icon_dict.get(model['name'], '') if icon_dict.get(model['name'], '') else icon_dict.get(model['name'], '')

        ## 如果配置了不显示系统菜单，则只显示配置的菜单
        if not settings.SOHO_MENU_LIST['show_system_menu']:
            app_list = settings.SOHO_MENU_LIST.get('models', [])
        else:
            print(3131)
            for sohoui_model in settings.SOHO_MENU_LIST.get('models', []):
                default_app_dict = {
                    'name': sohoui_model['name'],
                    'models': [],
                    'icon': sohoui_model.get('icon', '') if sohoui_model.get('icon', '') else  icon_dict.get(sohoui_model['name'], '')
                }
                ## 判断用户是否有权限model访问，有则添加到app_list   
                for model in sohoui_model.get('models', []):
                    if model.get('permission', ''):
                        if  request.user.has_perm(model.get('permission')):
                            default_app_dict['models'].append(model)
                    else:
                        # 判断用户是否有权限model访问，有则添加到app_list   
                        default_app_dict['models'].append(model)
                if default_app_dict['models']:
                    app_list.append(default_app_dict)
        print(app_list)
        return {
            # 站点标题
            'app_list': app_list
        }
    
    
    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.

        For sites running on a subpath, use the SCRIPT_NAME value if site_url
        hasn't been customized.
        """
        script_name = request.META["SCRIPT_NAME"]
        site_url = (
            script_name if self.site_url == "/" and script_name else self.site_url
        )
        return {
            "site_title": self.site_title,
            "site_header": self.site_header,
            "site_url": site_url,
            "has_permission": self.has_permission(request),
            # "available_apps": self.get_app_list(request),
            "is_popup": False,
            "is_nav_sidebar_enabled": self.enable_nav_sidebar,
        }
        
    def index(self, request, extra_context=None):
        # app_list = self.get_app_list(request)
        context = {
            **self.each_context(request),
            "title": self.index_title,
            "subtitle": None,
            **(extra_context or {}),
        }
        
        print('MyAdminSite')
        context.update({
            'app_list': self.get_app_list(request)['app_list'],
        })
        context.update({
            'available_apps': context['app_list'],
        })

        request.current_app = self.name
        return TemplateResponse(
            request, self.index_template or "admin/index.html", context
        )
        
adminsite = MyAdminSite()

from django.contrib.admin.utils import (
    label_for_field,
)
def result_headers(cl):
    """
    Generate the list column headers.
    """
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        yield {
            "text": text,
            "sortable": True,
        }

from django.utils.safestring import mark_safe


def get_custom_result_headers(cl):
    result_headers = []
    field_names = []
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        field_names.append(field_name)
        result_headers.append(text)
    return result_headers, field_names

def get_custom_result_list(self, cl, field_names):

    model = self.model 
    
    result_list = []
    for obj, form in zip(cl.result_list, cl.formset.forms):
        result_dict = {}
        ## 获取model的change链接拼接id
        change_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        result_dict['id'] = obj.id
        result_dict['change_url'] = change_url
        
        index = 1
        
        for i in items_for_result(cl, obj, form)[1:]:
            field_name = field_names[index]
            
            if hasattr(self, field_name):
                # 调用admin func
                field_value = i
            else:
            
                if field_name != '__str__':
                    if model._meta.get_field(field_name):
                        field = model._meta.get_field(field_name)
                    else:
                        field = None
                else:
                    field = None
                    
                if field_name == '__str__':
                    field_value = obj.__str__()
                
                elif hasattr(obj, 'get_%s_display' % field_name):
                    # 如果是IntegerField，直接获取字段值
                    field_value = getattr(obj, 'get_%s_display' % field_name)()
                # 判断是否ForeignKey
                elif isinstance(field, (ForeignKey, UiForeignKeyField)):
                    # 获取foreighkey的__str__
                    if getattr(obj, field_name).__str__() and getattr(obj, field_name).__str__() != 'None':
                        field_value = getattr(obj, field_name).__str__()
                    else:
                        field_value = ''
                # 判断是否BooleanField/日期格式
                elif isinstance(field, (ImageField)):
                    if getattr(obj, field_name):
                        field_value = '<img src="/static%s" style="width: 100px; height: 100px;" />' % getattr(obj, field_name).url
                    else:
                        field_value = ''
                else:
                    if isinstance(getattr(obj, field_name), bool):
                        if str(getattr(obj, field_name)) == 'True':
                            field_value = 'True'
                        elif str(getattr(obj, field_name)) == 'False':
                            field_value = 'False'
                        else:
                            field_value = str(getattr(obj, field_name))
                    elif isinstance(field, (DateField, UiDateField)):
                        if getattr(obj, field_name):
                            # 尝试解析字符串为日期
                            try:
                                field_value = getattr(obj, field_name).strftime('%Y-%m-%d')
                            except ValueError:
                                try:
                                    field_value = getattr(obj, field_name).strftime('%Y-%m-%d')
                                except ValueError:
                                    field_value = getattr(obj, field_name)
                        else:
                            field_value = ''
                    elif isinstance(field, (TimeField, UiTimeField)):
                        if getattr(obj, field_name):
                        # 尝试解析字符串为日期
                            try:
                                field_value = getattr(obj, field_name).strftime('%H:%M:%S')
                            except ValueError:
                                try:
                                    field_value = getattr(obj, field_name).strftime('%H:%M:%S')
                                except ValueError:
                                    field_value = getattr(obj, field_name)
                        else:
                            field_value = ''
                                
                    elif isinstance(field, (DateTimeField, UiDateTimeField)):
                        if getattr(obj, field_name):
                            # 尝试解析字符串为日期
                            try:
                                field_value = getattr(obj, field_name).strftime('%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                try:
                                    field_value = getattr(obj, field_name).strftime('%Y-%m-%d')
                                except ValueError:
                                    field_value = getattr(obj, field_name)
                        else:
                            field_value = ''
                    else:
                        field_value = getattr(obj, field_name)
            if type(field_value) == str:
                if field_value: 
                    result_dict[field_name] = field_value
                else:
                    result_dict[field_name] = ''
            elif type(field_value) in [float, int]:
                result_dict[field_name] = field_value
            else:
                if field_value:
                    result_dict[field_name] = field_value
                else:
                    result_dict[field_name] = ''
            index += 1
        result_list.append(result_dict)
    return result_list

from django.db import models
def get_filter_choices(self, field_name):
    # 获取过滤器的选择项
    choices = []
    
    # 动态获取模型类
    model = self.model  # 当前 ModelAdmin 关联的模型
    field = model._meta.get_field(field_name)  # 获取字段对象

    if isinstance(field, models.ForeignKey):
        # 如果是外键，获取所有相关模型的实例
        related_model = field.related_model
        for obj in related_model.objects.all():
            choices.append({'value': obj.id, 'label': str(obj)})
    elif isinstance(field, models.BooleanField):
        # 如果是布尔字段，提供 True 和 False 选项
        choices = [{'value': 1, 'label': '是'}, {'value': 0, 'label': '否'}]
    elif isinstance(field, models.CharField) or isinstance(field, models.TextField) or isinstance(field, models.IntegerField):
        # 如果是字符字段，获取所有唯一值
        # 判断是否设置了choices
        if field.choices:
            if isinstance(field, models.IntegerField):
                for choice in field.choices:
                    choices.append({'value': choice[0], 'label': choice[1]})
            else:
                for choice in field.choices:
                    choices.append({'value': int(choice[0]), 'label': choice[1]})
        else:
            unique_values = model.objects.values_list(field_name, flat=True).distinct()
            for value in unique_values:
                choices.append({'value': value, 'label': value})

    return choices

def get_custom_filters(self, list_filter):
    
    # 创建一个字典来存储筛选器的键值对
    filter_list = []
    
    for filter_item in list_filter:
        # 处理字符串类型的过滤器
        if isinstance(filter_item, str):
            filter_list.append({
                'field': filter_item,
                'field_name': self.model._meta.get_field(filter_item).verbose_name, # 获取field verbose_name
                'choices': get_filter_choices(self, filter_item)
            })
        else:
            # 处理其他类型的过滤器（如元组）
            field_name = filter_item if isinstance(filter_item, tuple) else filter_item[0]
            filter_list.append({
                'field': filter_item,
                'field_name': self.model._meta.get_field(field_name).verbose_name, # 获取field verbose_name
                'choices': get_filter_choices(self, field_name)
            })
    return filter_list

from django.contrib.admin.utils import (
    display_for_field,
    display_for_value,
    get_fields_from_path,
    label_for_field,
    lookup_field,
)

from django.contrib.admin.templatetags.admin_list import ResultList, _coerce_field_name, lookup_field, display_for_value
from django.core.exceptions import ObjectDoesNotExist

def items_for_result(cl, result, form):
    """
    Generate the actual list of data.
    """
    result_list = []
    for field_index, field_name in enumerate(cl.list_display):
        empty_value_display = cl.model_admin.get_empty_value_display()
        row_classes = ["field-%s" % _coerce_field_name(field_name, field_index)]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(
                attr, "empty_value_display", empty_value_display
            )
            if f is None or f.auto_created:
                if field_name == "action_checkbox":
                    row_classes = ["action-checkbox"]
                boolean = getattr(attr, "boolean", False)
                # Set boolean for attr that is a property, if defined.
                if isinstance(attr, property) and hasattr(attr, "fget"):
                    boolean = getattr(attr.fget, "boolean", False)
                result_repr = display_for_value(value, empty_value_display, boolean)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f, empty_value_display)
                if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")
        
        result_list.append(result_repr)
    return result_list
        
def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield ResultList(form, items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield ResultList(None, items_for_result(cl, res, None))
            
from django.utils.html import format_html
from django.db.models.constants import LOOKUP_SEP
from django.contrib.admin.views.main import (
    ALL_VAR,
    ORDER_VAR,
)
from django.utils.translation import gettext as _

def result_headers(cl):
    """
    Generate the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        is_field_sortable = cl.sortable_by is None or field_name in cl.sortable_by
        if attr:
            field_name = _coerce_field_name(field_name, i)
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == "action_checkbox":
                aria_label = _("Select all objects on this page for an action")
                yield {
                    "text": mark_safe(
                        f'<input type="checkbox" id="action-toggle" '
                        f'aria-label="{aria_label}">'
                    ),
                    "class_attrib": mark_safe(' class="action-checkbox-column"'),
                    "sortable": False,
                }
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            # Set ordering for attr that is a property, if defined.
            if isinstance(attr, property) and hasattr(attr, "fget"):
                admin_order_field = getattr(attr.fget, "admin_order_field", None)
            if not admin_order_field and LOOKUP_SEP not in field_name:
                is_field_sortable = False

        if not is_field_sortable:
            # Not sortable
            yield {
                "text": text,
                "field_name": field_name,
                "class_attrib": format_html(' class="column-{}"', field_name),
                "sortable": False,
            }
            continue

        # OK, it is sortable if we got this far
        th_classes = ["sortable", "column-{}".format(field_name)]
        order_type = ""
        new_order_type = "asc"
        sort_priority = 0
        # Is it currently being sorted on?
        is_sorted = i in ordering_field_columns
        if is_sorted:
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append("sorted %sending" % order_type)
            new_order_type = {"asc": "desc", "desc": "asc"}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field

        def make_qs_param(t, n):
            return ("-" if t == "desc" else "") + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "text": text,
            "field_name": field_name,
            "sortable": True,
            "sorted": is_sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string({ORDER_VAR: ".".join(o_list_primary)}),
            "url_remove": cl.get_query_string({ORDER_VAR: ".".join(o_list_remove)}),
            "url_toggle": cl.get_query_string({ORDER_VAR: ".".join(o_list_toggle)}),
            "class_attrib": (
                format_html(' class="{}"', " ".join(th_classes)) if th_classes else ""
            ),
        }


from .fields import *
from django.core.paginator import Paginator


def pagination(cl):
    """
    Generate the series of links to the pages in a paginated list.
    """
    pagination_required = (not cl.show_all or not cl.can_show_all) and cl.multi_page
    page_range = (
        cl.paginator.get_elided_page_range(cl.page_num) if pagination_required else []
    )
    need_show_all_link = cl.can_show_all and not cl.show_all and cl.multi_page
    return {
        "cl": cl,
        "pagination_required": pagination_required,
        "show_all_url": need_show_all_link and cl.get_query_string({ALL_VAR: ""}),
        "page_range": page_range,
        "ALL_VAR": ALL_VAR,
        "1": 1,
    }
    
    
from django.contrib.admin.helpers import AdminReadonlyField
class CustomReadonlyField(AdminReadonlyField):
    def contents(self):
        field, obj, model_admin = (
            self.field["field"],
            self.form.instance,
            self.model_admin,
        )
        if field == "title":  # 替换为你的字段名
            return "自定义内容"  # 返回你想要显示的内容
        
        # 调用父类的内容处理逻辑
        return super().contents()
    
class BaseAdmin(admin.ModelAdmin):
    ## 重写DateTimeField的form_class
    
    delete_confirmation_template = 'admin/delete_selected_confirmation.html'

    def get_app_list(self, request):
        # 使用 Django 的内置方法获取 app_list
        # from django.contrib.admin import site
        return adminsite.get_app_list(request)
    
    
    def changelist_view(self, request, extra_context=None):
        print('changelist_view')
        # app_list = self.get_app_list(request)
        # app_list = MyAdminSite().get_app_list(request)
        # # 将 app_list 添加到上下文中
        extra_context = extra_context or {}
        # extra_context['app_list'] = app_list['app_list']
        # extra_context['available_apps'] = app_list['app_list']
        cl = self.get_changelist_instance(request)
        
        pagination_result = pagination(cl)
        
        FormSet = self.get_changelist_formset(request)
        cl.formset = FormSet(queryset=cl.result_list)
        
        # 获取admin中自定义func
        verbose_names = ','.join([str(self.model._meta.get_field(field).verbose_name) for field in self.search_fields])
        list_filters = self.get_list_filter(request)
        filter_list = get_custom_filters(self, list_filters)
        ## 获取不同app的result_headers
        result_headers1, field_names = get_custom_result_headers(cl)
        ## 获取result_list
        
        result_list = get_custom_result_list(self, cl, field_names)
        result_headers_result = []
        result_headers_index = 0
        for obj in result_headers(cl):
            if result_headers_index == 0:
                result_headers_index += 1
                continue
            
            result_headers_result.append({
                'text': obj['text'],
                'prop': obj['field_name']
            })
            result_headers_index += 1
            
        ## 获取actions
        actions = self.get_actions(request)
        actions_result = []
        for func, name, desc in actions.values():
            if name in ['delete_selected']:
                actions_result.append({
                    'name': 'delete_selected',
                    'desc': '删除选中',
                    'type': 'danger',
                    'icon': 'el-icon-delete'
                })
                continue
            actions_result.append({
                'name': name,
                'desc': desc,
                'type': func.type if hasattr(func, 'type') else 'primary',
                'icon': func.icon if hasattr(func, 'icon') else 'fa-solid fa-check'
            })

        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
        actions = self.get_actions(request)
        if (
            actions
            and request.method == "POST"
            and "index" in request.POST
            and "_save" not in request.POST
        ):
            if selected:
                
                response = self.response_action(
                    request, queryset=cl.get_queryset(request)
                )
                if response:
                    response_json  = response.__dict__
                    return TemplateResponse(
                        request,
                        self.delete_confirmation_template,
                        {
                            'context_data':{key: value.strip() if type(value) == str else value for key, value in response_json['context_data'].items()},
                            'objects_name':response_json['context_data']['objects_name']
                        }
                    )
                    return response
                
                data = request.POST.copy()
                data.pop(helpers.ACTION_CHECKBOX_NAME, None)
                data.pop("index", None)
                action_form = self.action_form(data, auto_id=None)
                action_form.fields["action"].choices = self.get_action_choices(request)

                # # If the form's valid we can handle the action.
                if action_form.is_valid():
                    action = action_form.cleaned_data["action"]
                    select_across = action_form.cleaned_data["select_across"]
                    func = self.get_actions(request)[action][0]

                    selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
                    
                    queryset = cl.get_queryset(request)
                    
                    if not select_across:
                        # Perform the action only on the selected objects
                        queryset = queryset.filter(pk__in=selected)
                    
                response = func(self, request, queryset=queryset)
                
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _(
                    "Items must be selected in order to perform "
                    "actions on them. No items have been changed."
                )
                from django.contrib import messages
                self.message_user(request, msg, messages.WARNING)
                action_failed = True
            if action_failed:
                # Redirect back to the changelist page to avoid resubmitting the
                # form if the user refreshes the browser or uses the "No, take
                # me back" button on the action confirmation page.
                # return HttpResponseRedirect(request.get_full_path())
                from django.http import HttpResponse
                import json
                admin_messages = []
                for message in getattr(request, "_messages", []):
                    admin_messages.append({
                        'message': message.message,
                        'tags': message.tags
                    })
                    
                return HttpResponse(json.dumps({'messages': admin_messages}))
            
        if (
            actions
            and request.method == "POST"
            and helpers.ACTION_CHECKBOX_NAME in request.POST
            and "index" not in request.POST
            and "_save" not in request.POST
        ):
            if selected:
                response = self.response_action(
                    request, queryset=cl.get_queryset(request)
                )
                if response:
                    return response
                else:
                    action_failed = True
        
        extra_context.update({
            'result_list': result_list,
            'result_headers': result_headers_result,
            'filter_list': filter_list,
            'search_placeholder': verbose_names,
            'total': pagination_result['cl'].paginator.count,
            'page_size': pagination_result['cl'].list_per_page,
            'current_page': pagination_result['cl'].page_num,
            'actions_result': actions_result,
            ## 获取新增链接
            'add_url': reverse('admin:%s_%s_add' % (self.model._meta.app_label, self.model._meta.model_name)),
            'messages_info': {'tag': 'success', 'message': '操作成功！'},
            'index_url': settings.LOGIN_REDIRECT_URL,
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
            'has_view_permission': self.has_view_permission(request),
        })
        return super().changelist_view(request, extra_context=extra_context)
    
    def _changeform_view(self, request, object_id, form_url, extra_context):
        response = super()._changeform_view(request, object_id, form_url, extra_context)
        
        add = object_id is None
        
        try:
            for fieldset in response.context_data['adminform']:
                for line in fieldset:
                    for field in line:
                        if field.field.field.__class__.__module__ == 'django_sohoui.fields':
                            field.field.field_type = 'django_sohoui'
                        else:
                            field.field.field_type = 'django'
        except:
            print('error')
        return response

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        fieldsets = self.get_fieldsets(request)
        fieldsets_dict = {}
        for header, fields in fieldsets:
            for field in fields['fields']:
                
                # 获取不同字段的verbose_name
                try:
                    field_name = self.model._meta.get_field(field).verbose_name
                    fieldsets_dict[field] = field_name
                except:
                    field_name = field
                    fieldsets_dict[field] = field_name
                # 判断是否存在UiImageField
                # if isinstance(self.model._meta.get_field(field), UiImageField):
                #     context['has_file_field_custom'] = True
        
        context.update({
            'back_url': reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name)),
            'django_ui_fields': fieldsets_dict,
            'index_url': settings.LOGIN_REDIRECT_URL,
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
            'has_view_permission': self.has_view_permission(request),
        })
        
        
        ## 获取app_list
        app_list = self.get_app_list(request)
        context['app_list'] = app_list['app_list']
        
        ## 获取object history
        if obj:
            object_id = obj.id
            app_label = self.opts.app_label
            app_logs = (
                LogEntry.objects.filter(
                    object_id=object_id,
                    content_type=get_content_type_for_model(self.model),
                )
                .select_related()
                .order_by("action_time")
            )
            action_list = []
            for app_log in app_logs[0:20]:
                if app_log.user.get_full_name():
                    user_name =  '%s(%s)' % (app_log.user.get_username(), app_log.user.get_full_name())
                else:
                    user_name = app_log.user.get_username() 
                action_list.append({
                    'action_time': app_log.action_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'user': user_name,
                    'action': app_log.get_change_message()
                })
            
            context['action_list'] = action_list
        if obj:
            field_value = getattr(obj, 'title', None)
            
        for inline_admin_formsets in context['inline_admin_formsets']:
            print(inline_admin_formsets.__dict__)
            # for key, field in inline_admin_formsets.fields:
            #     print(field)
        return super().render_change_form(request, context, add, change, form_url, obj)
    
   
    def get_form(self, request, obj=None, **kwargs):
        # 在这里传递当前用户
        form = super().get_form(request, obj, **kwargs)
        
        form.current_user = request.user  # 将当前用户传递给表单
        form.has_change_permission = self.has_change_permission(request, obj)
        form.readonly_fields = self.get_readonly_fields(request, obj)
        return form
    

# 注册用户模型

from django.contrib.auth.admin import UserAdmin

class UserAdmin(BaseAdmin, UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2"),
            },
        ),
    )
    
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

adminsite.register(User, UserAdmin)

# 注册组模型
class GroupAdmin(BaseAdmin):
    filter_horizontal = ['permissions']

adminsite.register(Group, GroupAdmin)
