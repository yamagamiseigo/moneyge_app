from django.db import models

class Debt_Information(models.Model):
    name_lender = models.CharField(max_length=30, verbose_name='借入先名')
    current_balance = models.DecimalField(max_digits=20, decimal_places=0, verbose_name='現在の残高')
    annual_interest_rate = models.DecimalField(max_digits=6, decimal_places=3, verbose_name='年間利率')
    monthly_repayment = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='月次の返済額')
    monthly_payment_date = models.DateField(verbose_name='毎月の返済日', blank=True, null=True)
    editor_owner = models.CharField(max_length=30, verbose_name='更新者')

    def calc_annual_interset(self):
        return int(self.current_balance * (self.annual_interest_rate)/100)

class DebtHistory(models.Model):
    debt = models.ForeignKey(Debt_Information, on_delete=models.CASCADE, verbose_name="対象の借金")
    record_date = models.DateField(verbose_name="記録年月")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="当月返済額")
    interest_amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="当月発生利息")
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="返済後残高")

    def __str__(self):
        # 管理画面やデバッグでパッと見で分かりやすいようにする文字列化
        return f"{self.debt.name_lender} - {self.record_date.strftime('%Y年%m月')} (残高: {self.remaining_balance}円)"

class RepaymentRecord(models.Model):
    debt = models.ForeignKey(Debt_Information, on_delete=models.CASCADE, verbose_name='借入先')
    repayment_amount = models.IntegerField(verbose_name='返済額')
    repayment_date = models.DateField(verbose_name='返済日', auto_now_add=True)

    def _str__(self):
        return f'{self.dabt.name_lender} - {self.repayment_amount}円 ({self.repayment_date})'
    