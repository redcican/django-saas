import datetime
import json
from django.http import HttpResponse
from django_redis import get_redis_connection

from django.shortcuts import render, redirect
from tracer import models
from utils.encrypt import uid
from django.conf import settings
from utils.alipay import AliPay


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
        transaction_object = models.Transaction.objects.filter(user=request.tracer.user, status=2).order_by(
            '-id').first()
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

    conn = get_redis_connection()
    key = f'payment_{request.tracer.user.mobile_phone}'
    conn.set(key, json.dumps(context), ex=60 * 30)

    context['policy_object'] = policy_object
    context['transaction'] = transaction_object

    return render(request, 'payment.html', context)


def pay(request):
    """pay page for ali pay"""
    conn = get_redis_connection()
    key = f'payment_{request.tracer.user.mobile_phone}'

    context_string = conn.get(key)
    if not context_string:
        return redirect('tracer:price')

    context = json.loads(context_string.decode('utf-8'))

    # 1. 数据库中生成交易记录(待支付), 支付成功后更新交易记录(已支付，开始和结束时间)
    order_id = uid(request.tracer.user.mobile_phone)
    total_price = context['total_price']

    models.Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.tracer.user,
        price_policy_id=context['policy_id'],
        count=context['number'],
        price=total_price,
    )
    # 2. 跳转支付宝支付页面
    ali_pay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=settings.ALIPAY_NOTIFY_URL,
        return_url=settings.ALIPAY_RETURN_URL,
        app_private_key_path=settings.ALIPAY_PRIVATE_KEY_PATH,
        alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH
    )
    query_params = ali_pay.direct_pay(
        subject="tracer system payment",  # 商品简单描述
        out_trade_no=order_id,  # 商户订单号
        total_amount=total_price
    )
    pay_url = "{}?{}".format(settings.ALIPAY_GATEWAY, query_params)
    return redirect(pay_url)

    """
    params = {
        'app_id': settings.ALIPAY_APPID,
        'method': 'alipay.trade.page.pay',
        'format': 'JSON',
        'return_url': 'http://127.0.0.1:8000/pay/notify/',
        'notify_url': 'http://127.0.0.1:8000/pay/notify/',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'biz_content': json.dumps({
            'out_trade_no': order_id,
            'product_code': 'FAST_INSTANT_TRADE_PAY',
            'total_amount': total_price,
            'subject': 'Buy tracer plan',
        }, separators=(',', ':')),
    }

    unsigned_string = "&".join(["{0}={1}".format(k, params[k]) for k in sorted(params)])
    # singed with SHA256WithRSA
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import encodebytes
    from pathlib import Path

    # key_path = Path(__file__).parent.parent.parent / 'files'/ 'privatekey2048.txt'
    key_path = Path(settings.ALIPAY_PRIVATE_KEY_PATH)

    private_key = RSA.importKey(open(key_path).read())
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(SHA256.new(unsigned_string.encode("utf8")))

    # base64 encode
    sign_string = encodebytes(signature).decode("utf8").replace("\n", "")

    from urllib.parse import quote_plus
    result = "&".join(["{0}={1}".format(k, quote_plus(params[k])) for k in sorted(params)])
    result += "&sign=" + quote_plus(sign_string)

    # gate_way = "https://openapi.alipaydev.com/gateway.do"
    gate_way = settings.ALIPAY_GATEWAY
    ali_pay_url = "{}?{}".format(gate_way, result)
    # 2.1 生成支付宝支付链接
    # 2.2 跳转到支付宝支付页面

    return redirect(ali_pay_url)
    """


def pay_notify(request):
    """pay notify page for ali pay"""
    ali_pay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=settings.ALIPAY_NOTIFY_URL,
        return_url=settings.ALIPAY_RETURN_URL,
        app_private_key_path=settings.ALIPAY_PRIVATE_KEY_PATH,
        alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH
    )
    if request.method == 'GET':
        # 只做跳转, 判断是否支付成功，不做订单的更新
        # 支付宝会把订单号返回，获取订单ID，然后更新订单状态 和 认证
        # 支付宝公钥对支付宝返回的数据request.GET进行检查，通过则表示这是支付宝返回的接口
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = ali_pay.verify(params, sign)
        if status:
            return HttpResponse('Paid Successful')
        else:
            return HttpResponse("Paid Fail")
    else:
        # 做订单的更新
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        sign = post_dict.pop('sign', None)
        status = ali_pay.verify(post_dict, sign)
        if status:
            order_id = post_dict['out_trade_no']
            _object = models.Transaction.objects.filter(order=order_id).first()

            _object.status = 2
            _object.start_datetime = datetime.datetime.now()
            _object.end_datetime = datetime.datetime.now() + datetime.timedelta(days=365 * _object.count)
            _object.save()
            return HttpResponse('success')

        return HttpResponse('error')