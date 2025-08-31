from django.shortcuts import render

# Create your views here.
import requests
import os
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Payment
from .serializers import BookingSerializer
from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

class InitiatePaymentView(APIView):
    def post(self, request):
        booking_id = request.data.get('booking_id')
        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the booking belongs to the requesting user
        if booking.guest != request.user:
            return Response({'error': 'Unauthorized access to booking'}, status=status.HTTP_403_FORBIDDEN)

        # Prepare Chapa API request
        chapa_url = 'https://api.chapa.co/v1/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {os.getenv("CHAPA_SECRET_KEY")}',
            'Content-Type': 'application/json',
        }
        tx_ref = f"tx-{uuid.uuid4()}"  # Unique transaction reference
        data = {
            'amount': str(booking.total_price),
            'currency': 'ETB',
            'email': request.user.email,
            'first_name': request.user.first_name or 'Guest',
            'last_name': request.user.last_name or 'User',
            'tx_ref': tx_ref,
            'callback_url': 'http://your-domain.com/api/payment/verify/',
            'return_url': 'http://your-domain.com/payment/success/',
        }

        # Initiate payment
        try:
            response = requests.post(chapa_url, json=data, headers=headers)
            response_data = response.json()
            logger.info(f"Payment initiation response: {response_data}")

            if response_data.get('status') == 'success':
                # Store payment details
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_price,
                    transaction_id=tx_ref,
                    status='pending'
                )
                return Response({
                    'message': 'Payment initiated successfully',
                    'payment_url': response_data['data']['checkout_url'],
                    'transaction_id': tx_ref
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Payment initiation failed: {response_data.get('message')}")
                return Response({
                    'error': response_data.get('message', 'Payment initiation failed')
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            logger.error(f"Payment initiation error: {str(e)}")
            return Response({'error': f'Payment initiation error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPaymentView(APIView):
    def post(self, request):
        transaction_id = request.data.get('transaction_id')
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the booking belongs to the requesting user
        if payment.booking.guest != request.user:
            return Response({'error': 'Unauthorized access to payment'}, status=status.HTTP_403_FORBIDDEN)

        # Verify payment with Chapa
        chapa_url = f'https://api.chapa.co/v1/transaction/verify/{transaction_id}'
        headers = {
            'Authorization': f'Bearer {os.getenv("CHAPA_SECRET_KEY")}'
        }

        try:
            response = requests.get(chapa_url, headers=headers)
            response_data = response.json()
            logger.info(f"Payment verification response: {response_data}")

            if response_data.get('status') == 'success':
                payment.status = 'completed'
                payment.save()
                # Trigger email notification via Celery
                send_payment_confirmation_email.delay(payment.payment_id)
                return Response({
                    'message': 'Payment verified successfully',
                    'status': payment.status
                }, status=status.HTTP_200_OK)
            else:
                payment.status = 'failed'
                payment.save()
                logger.error(f"Payment verification failed: {response_data.get('message')}")
                return Response({
                    'error': 'Payment verification failed',
                    'status': payment.status
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            payment.status = 'failed'
            payment.save()
            logger.error(f"Verification error: {str(e)}")
            return Response({'error': f'Verification error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@shared_task
def send_payment_confirmation_email(payment_id):
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        subject = 'Payment Confirmation'
        message = f'Your payment of {payment.amount} ETB for booking {payment.booking.booking_id} has been successfully processed.'
        send_mail(
            subject,
            message,
            'from@example.com',
            [payment.booking.guest.email],
            fail_silently=False,
        )
        logger.info(f"Payment confirmation email sent for payment {payment_id}")
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email for payment {payment_id}: {str(e)}")