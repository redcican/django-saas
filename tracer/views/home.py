import datetime

from django.shortcuts import render, redirect
from tracer import models


def index(request):
    return render(request, 'index.html')


def price(request):
    price_list = models.PricePolicy.objects.filter(category=2)
    return render(request, 'price.html', {'price_list': price_list})


def payment(request, policy_id):
    """payment page"""
    # 1. get policy id
    policy_object = models.PricePolicy.objects.filter(id=policy_id, category=2).first()
    if not policy_object:
        return redirect('tracer:price')

    # 2. get the number of payment
    number = request.GET.get('number')
    if not number or not number.isdecimal():
        return redirect('tracer:price')

    number = int(number)
    if number < 1:
        return redirect('tracer:price')

    # 3. get the total price
    original_price = policy_object.price * number

    # 4. 如果之间购买过套餐,
    balance = 0
    transaction_object = None
    if request.tracer.price_policy.category == 2:
        # 4.1 如果之前已经是付费套餐, 找到之间的订单， 总费用，开始和结束时间，还有剩余的天数
        transaction_object = models.Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id').first()
        total_timedelta = transaction_object.end_datetime - transaction_object.start_datetime
        balance_timedelta = transaction_object.end_datetime - datetime.datetime.now()

        if total_timedelta.days == balance_timedelta.days:
            balance = transaction_object.price / total_timedelta.days * (balance_timedelta.days - 1)
        else:
            balance = transaction_object.price / total_timedelta.days * balance_timedelta.days

    if balance > original_price:
        return redirect('tracer:price')

    context = {
        'policy_id': policy_object.id,
        'number': number,
        'original_price': original_price,
        'balance': round(balance, 2),
        'total_price': original_price - round(balance, 2),
    }

    context['policy_object'] = policy_object
    context['transaction'] = transaction_object

    return render(request, 'payment.html', context)

