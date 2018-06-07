from annoying.decorators import render_to
from payments.models import Order, Payment


@render_to('payments/payment.html')
def payment(request):
    return {'fee': 10234}


@render_to('payments/payment.html')
def orders(request, pk):
    orders = Order.objects.filter(client__id=pk)
    payments = Payment.objects.filter(client__id=pk)
    return {'orders': orders,
            'payments': payments}