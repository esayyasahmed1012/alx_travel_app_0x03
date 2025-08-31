from celery import shared_task
from django.core.mail import send_mail
from .models import Payment

@shared_task
def send_payment_confirmation_email(payment_id):
    payment = Payment.objects.get(id=payment_id)
    subject = 'Payment Confirmation'
    message = f'Your payment of {payment.amount} ETB for booking {payment.booking.id} has been successfully processed.'
    send_mail(
        subject,
        message,
        'from@example.com',
        [payment.booking.user.email],
        fail_silently=False,
    )