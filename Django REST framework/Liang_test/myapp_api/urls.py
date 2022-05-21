from django.urls import path, re_path, include
from myapp_api import views
from rest_framework import routers

# 自注册路由
router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
