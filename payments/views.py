from annoying.decorators import render_to
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

from payments.models import Order

@user_passes_test(lambda u: u.is_patient)
@render_to('payments/payment.html')
def payment(request, pk):
    order = Order.objects.get(pk=pk)
    if request.POST:
        if sum == order.sum:
            raise Exception('Wrong sum!')
        order.payed = True
        order.save()
        return redirect('orders', order.patient.id)
    return {'order': order}


@user_passes_test(lambda u: u.is_patient)
@render_to('payments/orders.html')
def orders(request, pk):
    orders = Order.objects.filter(patient__id=pk).filter(sum__gt=0).order_by('payed')
    return {'orders': orders}
