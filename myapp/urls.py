from django.urls import path
from . import views  # 同じフォルダ内にある views.py をインポート

urlpatterns = [
    # http://127.0.0.1:8000/myapp/ にアクセスしたときの処理
    path('', views.index, name='index'),
    path('debts/', views.debts, name='debts'),
    path('debts/<int:debts_id>', views.detail, name='detail'),
    path('debt_create/', views.debt_create, name='debt_create'),
    path('debt_repay/', views.debt_repay, name='debt_repay'),
]