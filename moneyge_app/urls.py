from django.contrib import admin
from django.urls import path, include  # includeをインポートする必要があります

urlpatterns = [
    path('admin/', admin.site.urls, name=admin),
    path('myapp/', include('myapp.urls')),  # 'myapp/' にアクセスがあったら myapp.urls に振り分ける
    path('', include('myapp.urls')),
]
