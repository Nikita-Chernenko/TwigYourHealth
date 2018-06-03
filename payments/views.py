from annoying.decorators import render_to


@render_to('payments/payment.html')
def payment(request):
    return {'fee': 10234}