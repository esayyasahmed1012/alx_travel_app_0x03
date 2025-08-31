from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(booking_id, user_email, listing_title):
    subject = 'Booking Confirmation'
    message = (
        f'Dear Customer,\n\n'
        f'Your booking for "{listing_title}" (Booking ID: {booking_id}) has been confirmed.\n'
        f'Thank you for choosing our service!\n\n'
        f'Regards,\nTravel App Team'
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error (consider adding a logger)
        print(f"Error sending email for booking {booking_id}: {str(e)}")