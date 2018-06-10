from annoying.decorators import render_to
from payments.models import Order


@render_to('payments/payment.html')
def payment(request, pk):
    order = Order.objects.get(pk=pk)
    if request.POST:
        if sum == order.sum:
            raise Exception('Wrong sum!')
        order.payed = True
        order.save()
    return {'order': order}


@render_to('payments/orders.html')
def orders(request, pk):
    orders = Order.objects.filter(patient__id=pk).order_by('payed')
    return {'orders': orders }