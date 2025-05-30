
from django.shortcuts import render

from django.http import JsonResponse
from django.core.paginator import Paginator

from django.contrib.auth.models import User
from django_sohoui.adminsite import UserAdmin
from django.db.models import Q

def dashboard(request):
    return render(request, 'admin/dashboard.html')

def dashboard1(request):
    return render(request, 'admin/dashboard1.html')


def get_data(request):
    
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 1))
    search_value = request.GET.get('search[value]', '')
    
    # 获取数据并进行分页
    queryset = User.objects.all()  # 替换为你的查询集
    
    if search_value:
        queryset = queryset.filter(
            Q(username__icontains=search_value)
        )
        
        
    total_records = queryset.count()
    paginator = Paginator(queryset, length)
    page_number = start // length + 1
    page_obj = paginator.get_page(page_number)
    
    data = []
    
    list_display = UserAdmin.list_display
    ## 获取list_display中的字段
    for item in page_obj:
        row = []
        row.append('<input type="checkbox" name="id" value="{}">'.format(item.id))
        for field in list_display:
            row.append(getattr(item, field))
        data.append(row)
   
        
    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_records,  # 如果有过滤条件，更新此值
        'data': data
    })
    
## 文件导入
from django.views.decorators.csrf import csrf_exempt
from project import settings
import os
import uuid

@csrf_exempt
def upload(request):
    ## 获取上传的文件并保存到media中
    print(request.FILES)
    try:
        print(request.FILES)
        filename = request.FILES.get('file')
        fn, ext = os.path.splitext(str(filename))
        name = str(uuid.uuid4())
        if not os.path.exists('{}/static/media/{}'.format(settings.BASE_DIR, name[0:3])):
            os.makedirs('{}/static/media/{}'.format(settings.BASE_DIR, name[0:3]))
            
        with open('{}/static/media/{}'.format(settings.BASE_DIR, os.path.join(name[0:3], name[:15]+ext)), 'wb') as f:
            f.write(filename.read())
        message = '上传成功'
        file_url = os.path.join('/static/media', os.path.join(name[0:3], name[:15]+ext))
    except Exception as e:
        file_url = ''
        message = '未选中文件'
    ## 返回文件路径
    return JsonResponse({
        'code': 200,
        'message': message,
        'url': file_url
    })
    


def delete_selected_confirmation(request):
    return render(request, 'admin/delete_selected_confirmation.html')


def custom_url(request):
    return render(request, 'custom_url.html')



def home(request):

    name = [
        {"number": "125.12", "percent": "-12.32%", "description": "订单统计信息", "icon": "/ui_template/images/bg1.webp"},
        {"number": "653.33", "percent": "+42.32%", "description": "月度计划信息", "icon": "/ui_template/images/bg1.webp"},
        {"number": "125.65", "percent": "+17.32%", "description": "年度计划信息", "icon": "/ui_template/images/bg1.webp"},
        {"number": "520.43", "percent": "-10.01%", "description": "访问统计信息", "icon": "/ui_template/images/bg1.webp"},
    ]
    
    colors = ['#FFCCCB', '#ADD8E6', '#90EE90']  # 示例颜色
    
    context = {
        "subtitle": None,
        "name": name,
        "colors": colors,  # 确保颜色列表被传递
    }

    return render(request, "admin/home-dev.html", context)


def test(request):
    data = {}
    return render(request, 'test.html', data)
