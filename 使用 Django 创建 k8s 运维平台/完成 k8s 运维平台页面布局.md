# 完成 k8s 运维平台页面布局

### 根据布局创建对象的 django 应用
```python
python manage.py startapp <应用名称>
```

应用规划：
- dashboard ：平台概述
- k8s
    - node
    - namespace
    - pv
- workload
    - deployments
    - daemonsets
    - statefulsets
    - pods
- loadbalancer
    - service
    - ingresses
- storage
    - pvc
    - configmaps
    - secrets

将每个应用的的 url 转移到本应用内
```python
# devops.urls.py
urlpatterns = [
    # ... 忽略之前的代码块
    re_path('^kubernetes/', include('k8s.urls')),
    re_path('^workload/', include('workload.urls')),
    re_path('^loadbalancer/', include('loadbalancer.urls')),
    re_path('^storage/', include('storage.urls')),
]
```
```python
# workload.urls.py
from django.urls import path,re_path
from workload import views

urlpatterns = [
    re_path('^deployment/$', views.deployment, name="deployment"),
    re_path('^deployment_api/$', views.deployment_api, name="deployment_api"),
    re_path('^daemonset/$', views.daemonset, name="daemonset"),
    re_path('^daemonset_api/$', views.daemonset_api, name="daemonset_api"),
    re_path('^statefulset/$', views.statefulset, name="statefulset"),
    re_path('^statefulset_api/$', views.statefulset_api, name="statefulset_api"),
    re_path('^pod/$', views.pod, name="pod"),
    re_path('^pod_api/$', views.pod_api, name="pod_api")
]

```
将创建的各应用所需页面资源放置于资源路径 templates 内
