from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from mnc.models import Urllist, Taglist


# Create your views here.
def mnc(request):
    return render(request, "mnc.html", {})


def Taglist_func(request):
    if request.method == "GET":
        try:
            code = 0
            Obj = Taglist.objects.all()
            data = []
            for item in Obj:
                d = {}
                d['tagid'] = item.tagid
                d['label'] = item.label
                d['attr_key'] = item.attr_key
                d['attr_value'] = item.attr_value
                d['src'] = item.src
                d['datatime'] = item.datatime
                data.append(d)
            msg = "获取数据成功"
        except Exception as e:
            data = None
            code = 1
            msg = str(e)
        count = len(data)
        if request.GET.get('page'):
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            # 拿到切片的起始值和终止值
            start = (page - 1) * limit
            end = page * limit
            data = data[start:end]
        result = {'code': code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)
    elif request.method == "DELETE":
        request_date = QueryDict(request.body)
        if request_date.get("tagid"):
            tagid = request_date.get("tagid")
            try:
                Taglist.objects.filter(tagid=tagid).delete()
                code = 0
                msg = "删除数据成功"
            except Exception as e:
                code = 1
                msg = str(e)
            result = {'code': code, 'msg': msg}
            return JsonResponse(result)
        else:
            code = 1
            msg = "未找到对应删除对象！"
            result = {'code': code, 'msg': msg}
            return JsonResponse(result)
    elif request.method == "PUT":
        request_data = QueryDict(request.body)
        tagid = request_data.get("tagid")
        try:
            taglist_obj = Taglist.objects.get(tagid=tagid)
            taglist_obj.label = request_data.get("label")
            taglist_obj.attr_key = request_data.get("attr_key")
            taglist_obj.attr_value = request_data.get("attr_value")
            taglist_obj.src = request_data.get("src")
            taglist_obj.save()

            code = 0
            msg = "更改数据成功"
        except Exception as e:
            code = 1
            msg = str(e)

        result = {'code': code, 'msg': msg}
        return JsonResponse(result)
    elif request.method == "POST":
        label = request.POST.get("label", None)
        attr_key = request.POST.get("attr_key", None)
        attr_value = request.POST.get("attr_value", None)
        src = request.POST.get("src", None)
        try:
            Taglist.objects.create(
                label=label,
                attr_key=attr_key,
                attr_value=attr_value,
                src=src
            )
            code = 0
            msg = "新增数据成功"
        except Exception as e:
            code = 1
            msg = str(e)

        result = {'code': code, 'msg': msg}
        return JsonResponse(result)


def Urllist_func(request):
    if request.method == "GET":
        try:
            Obj = Urllist.objects.all()
            data = []
            for item in Obj:
                d = {}
                d['urlid'] = item.urlid
                d['name'] = item.name
                d['type'] = item.type
                d['area'] = item.area
                d['para'] = item.para
                d['url'] = item.url
                d['frequency'] = item.frequency
                d['table_name'] = item.table_name
                d['tagid'] = item.taglist.tagid
                d['datatime'] = item.datatime
                data.append(d)
            code = 0
            msg = "获取数据成功"
            count = len(data)
        except Exception as e:
            data = None
            code = 1
            msg = str(e)
            count = None
        if request.GET.get('page'):
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            start = (page - 1) * limit
            end = page * limit
            data = data[start:end]

        result = {'code': code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)
    elif request.method == "DELETE":
        request_date = QueryDict(request.body)
        urlid = request_date.get("urlid")
        try:
            Urllist.objects.filter(urlid=urlid).delete()
            code = 0
            msg = "删除数据成功"
        except Exception as e:
            code = 1
            msg = str(e)
        result = {'code': code, 'msg': msg}
        return JsonResponse(result)
    elif request.method == "PUT":
        request_data = QueryDict(request.body)
        urlid = request_data.get("urlid")
        tagid = request_data.get("tagid")
        try:
            taglist_obj = Taglist.objects.get(tagid=tagid)
            urllist_obj = Urllist.objects.get(urlid=urlid)
            urllist_obj.name = request_data.get("name")
            urllist_obj.type = request_data.get("type")
            urllist_obj.area = request_data.get("area")
            urllist_obj.para = request_data.get("para")
            urllist_obj.url = request_data.get("url")
            urllist_obj.frequency = request_data.get("frequency")
            urllist_obj.table_name = request_data.get("table_name")
            urllist_obj.taglist = taglist_obj
            urllist_obj.save()

            code = 0
            msg = "更改数据成功"
        except Exception as e:
            code = 1
            msg = str(e)

        result = {'code': code, 'msg': msg}
        return JsonResponse(result)
    elif request.method == "POST":
        name = request.POST.get("name", None)
        type = request.POST.get("type", None)
        area = request.POST.get("area", None)
        para = request.POST.get("para", None)
        url = request.POST.get("url", None)
        frequency = request.POST.get("frequency", None)
        table_name = request.POST.get("table_name", None)
        tagid = request.POST.get("tagid", None)
        try:
            taglist_obj = Taglist.objects.get(tagid=tagid)
            Urllist.objects.create(
                name=name,
                type=type,
                area=area,
                para=para,
                url=url,
                frequency=frequency,
                table_name=table_name,
                taglist=taglist_obj
            )
            code = 0
            msg = "新增数据成功"
        except Exception as e:
            code = 1
            msg = str(e)

        result = {'code': code, 'msg': msg}
        return JsonResponse(result)


def Urllist_create(request):
    taglist_id = []
    try:
        Obj = Taglist.objects.all()
        for item in Obj:
            taglist_id.append(item.tagid)
    except Exception as e:
        print(str(e))
    if request.GET.get('urlid'):
        urlid = request.GET.get('urlid')
        name = request.GET.get('label')
        type = request.GET.get('type')
        area = request.GET.get('area')
        para = request.GET.get('para')
        url = request.GET.get('url')
        frequency = request.GET.get('frequency')
        table_name = request.GET.get('table_name')
        tag_id = request.GET.get('tag_id')

        return render(request, "urllist_create.html",
                      {'urlid': urlid, 'name': name, 'type': type, 'area': area, 'para': para, 'url': url,
                       'frequency': frequency, 'table_name': table_name, 'tag_id': tag_id, 'taglist_id': taglist_id})
    else:
        return render(request, "urllist_create.html", {'urlid': 'False', 'taglist_id': taglist_id})


def Taglist_create(request):
    if request.GET.get('tagid'):
        tagid = request.GET.get('tagid')
        label = request.GET.get('label')
        attr_key = request.GET.get('attr_key')
        attr_value = request.GET.get('attr_value')
        src = request.GET.get('src')

        return render(request, "taglist_create.html",
                      {'tagid': tagid, 'label': label, 'attr_key': attr_key, 'attr_value': attr_value, 'src': src})
    else:
        return render(request, "taglist_create.html", {'tagid': 'False'})
