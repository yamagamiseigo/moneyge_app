from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, F
from .models import Debt_Information, DebtHistory
from .form import DebtForm

def index(request):
    return HttpResponse("test")

def debts(request):
    # 借入先一覧を取得
    debt_lists = Debt_Information.objects.all()
    for debt in debt_lists:
        if debt.current_balance == 0:
            debt.delete()

    
    #現在残高の合計を計算する※データがない場合は0を返す
    total_balance = debt_lists.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    
    context ={
        'debt_lists': debt_lists,
        'total_balance': total_balance,
    }
    return render(request, 'debt_lists.html', context)

def debt_create(request):
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('debts')
    else:
        form = DebtForm()
    context = {
        'form': form
    }
    return render(request, 'debt_form.html', context)


def debt_repay(request):
    #借入先の全データを取得
    debt_lists = Debt_Information.objects.all()
    if request.method == 'POST':
        for debt in debt_lists:
            field_name = f'repay_{debt.id}'
            repayment_str = request.POST.get(field_name)

            if repayment_str and repayment_str.isdigit():
                repayment_amount = int(repayment_str)
                debt.current_balance = max(0, debt.current_balance - repayment_amount)
                debt.save()
                if debt.current_balance == 0:
                    debt.delete()
        return redirect('debts')
    context = {
        'debt_lists': debt_lists,
    }
    return render(request, 'repayment_form.html', context)

def detail(request, debt_id):
    edit = get_object_or_404(Debt_Information, pk=debt_id)
    debt_lists = Debt_Information.objects.all()
    context = {
        'edit': edit,
        'debt_lists': debt_lists,
    }

    return render(request, 'detail.html', context)
