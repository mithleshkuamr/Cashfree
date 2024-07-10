import json
import logging
import requests
from datetime import datetime, timedelta
from uuid import uuid4
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import render, get_object_or_404
from Events.models import EventCouponModel
from Events.models import EventTransactionModel
import logging

CASHFREE_APP_ID = 'TEST10023041ddc0462a33f2e3da7f3514032001'
CASHFREE_APP_KEY = 'TEST120b9d7057466ca666a83251b5382fa32279b94b'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            # Set order_expiry_time to 30 days from now
            order_expiry_time = datetime.now() + timedelta(days=30)

            # Check if cf_order_id already exists, generate a new one if needed
            cf_order_id = data.get('cf_order_id') or str(uuid4())

            # Create order in your local database
            order = Order.objects.create(
                cf_order_id=cf_order_id,
                created_at=datetime.now(),
                customer_id=data['customer_details']['customer_id'],
                customer_name=data['customer_details']['customer_name'],
                customer_email=data['customer_details']['customer_email'],
                customer_phone=data['customer_details']['customer_phone'],
                order_amount=data['order_amount'],
                order_currency=data['order_currency'],
                order_note=data.get('order_note', ''),
                order_id=data['order_id'],
                return_url=data.get('return_url', ''),
                notify_url=data.get('notify_url', ''),
                payment_methods=data.get('payment_methods', ''),
                order_status='SUCCESS',
                payment_session_id='',
                order_expiry_time=order_expiry_time  # Set the order_expiry_time
            )

            # Interface with Cashfree to create the order
            cf_order = create_cashfree_order(data)
            
            if cf_order:
                # Update local order with Cashfree response
                order.cf_order_id = cf_order['cf_order_id']
                order.order_status = cf_order['order_status']
                order.payment_session_id = cf_order['payment_session_id']
                order.save()

                # Fetch data from EventCouponModel based on certain conditions
                # For example, fetch coupons valid for the current event/order
                event_coupons = EventCouponModel.objects.filter(
                    expiry_date__gte=datetime.now(),
                    allow_all_events=True  # Example condition, adjust as needed
                )

                # Process the fetched data from EventCouponModel
                for coupon in event_coupons:
                    # Do something with the coupon data, like sending an email, etc.
                    print(f"Fetched coupon: {coupon}")

                response_data = {
                    'message': 'Order created successfully',
                    'order': OrderSerializer(order).data
                }
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                order.delete()
                return JsonResponse({'error': 'Failed to create order in Cashfree'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error in CreateOrderView: {e}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def create_cashfree_order(order_data):
    headers = {
        'x-api-version': '2023-08-01',
        'x-client-id': CASHFREE_APP_ID,
        'x-client-secret': CASHFREE_APP_KEY
    }

    data = {
        "order_id": order_data['order_id'],
        "order_amount": str(order_data['order_amount']),
        "order_currency": order_data['order_currency'],
        "order_note": order_data.get('order_note', ''),
        "customer_details": {
            "customer_id": order_data['customer_details']['customer_id'],
            "customer_name": order_data['customer_details']['customer_name'],
            "customer_email": order_data['customer_details']['customer_email'],
            "customer_phone": order_data['customer_details']['customer_phone']
        },
        "order_meta": {
            "return_url": order_data.get('return_url', ''),
            "notify_url": order_data.get('notify_url', ''),
            "payment_methods": order_data.get('payment_methods', '')
        }
    }

    url = 'https://sandbox.cashfree.com/pg/orders'
    try:
        logging.debug(f"Sending request to Cashfree: {data}")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        logging.debug(f"Cashfree response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating Cashfree order: {e}")
        if response is not None:
            logging.error(f"Response content: {response.content}")
        return None

class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class OrderDetailView(APIView):
    def get(self, request, order_id):
        try:
            orders = Order.objects.filter(order_id=order_id).order_by('-created_at')
            if not orders.exists():
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
            order = orders.first()  # Get the most recent order
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class ProcessPaymentView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            payment_session_id = data['payment_session_id']
            payment_method = data['payment_method']

            # Construct the payment method object based on the type of payment
            payment_data = {
                "payment_method": payment_method,
                "payment_session_id": payment_session_id
            }

            headers = {
                'x-api-version': '2023-08-01',
                'x-client-id': CASHFREE_APP_ID,
                'x-client-secret': CASHFREE_APP_KEY,
                'accept': 'application/json',
                'content-type': 'application/json'
            }

            url = 'https://sandbox.cashfree.com/pg/orders/sessions'
            response = requests.post(url, json=payment_data, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            return JsonResponse(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error in ProcessPaymentView: {e}")
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentFormView(View):
    def get(self, request, order_id):
        try:
            # Fetch orders with the given order_id
            orders = Order.objects.filter(order_id=order_id)
            
            if not orders.exists():
                return JsonResponse({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if orders.count() > 2:
                # Handle the case where there are multiple orders
                # Select the most recent order or the one with a specific status
                order = orders.order_by('-created_at').first()
                # If you have a specific status to filter by, use it instead
                # order = orders.filter(order_status='PENDING').order_by('-created_at').first()
            else:
                order = orders.first()
            
            payment_session_id = order.payment_session_id
            
            return render(request, 'payment.html', {'payment_session_id': payment_session_id})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CashfreeCallbackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            order_status= data.get('order_status')
            
            # Log the received data for debugging
            logging.info(f"Received callback data: {data}")
            
            # Initialize transaction_details
            transaction_details = None

            if order_status == 'SUCCESS':
                #"order_status": "SUCCESS",
                # Retrieve the first EventTransactionModel entry
                event_transaction = EventTransactionModel.objects.first()
                logging.info(f"Event transaction retrieved: {event_transaction}")
                
                if not event_transaction:
                    logging.info("No transaction found in the database.")
                    return JsonResponse({'error': 'No transaction found'}, status=404)
                
                # Retrieve additional data from related models if needed
                event_coupon = event_transaction.coupon
                
                # Extract and structure the transaction details
                transaction_details = self.get_transaction_details(event_transaction, event_coupon)
                
                response_data = {
                    'message': 'Payment successful',
                    'transaction_details': transaction_details
                }
                return JsonResponse(response_data, status=200)
            
            elif order_status == 'PENDING':
                # Retrieve all EventTransactionModel entries
                transactions = EventTransactionModel.objects.all()
                
                if not transactions.exists():
                    logging.info("No transactions found in the database.")
                    return JsonResponse({'error': 'No transactions found'}, status=404)
                
                # Extract and structure the transaction details for all transactions
                all_transactions_details = [
                    self.get_transaction_details(transaction, transaction.coupon)
                    for transaction in transactions
                ]
                
                response_data = {
                    'message': 'Payment pending',
                    'all_transaction_details': all_transactions_details
                }
                return JsonResponse(response_data, status=200)
            
            return JsonResponse({'message': 'Payment status not recognized'}, status=400)
        
        except Exception as e:
            logging.error(f"Error in CashfreeCallbackView: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    def get_transaction_details(self, event_transaction, event_coupon):
        """Helper method to structure transaction details."""
        transaction_details = {
            "pk": event_transaction.pk,
            "event": {
                "pk": event_transaction.event.pk,
                "name": event_transaction.event.name,
                "start_date": event_transaction.event.start_date,
                "end_date": event_transaction.event.end_date,
                "city": event_transaction.event.city,
                "image": event_transaction.event.image
            },
            "skus": [
                {
                    "pk": sku.pk,
                    "sku": {
                        "pk": sku.sku.pk,
                        "name": sku.sku.name,
                        "description": sku.sku.description,
                        "price": sku.sku.price,
                        "image": sku.sku.image,
                        "pax_allowed": sku.sku.pax_allowed,
                        "total_sold": sku.sku.total_sold,
                        "max_tickets": sku.sku.max_tickets
                    },
                    "quantity": sku.quantity,
                    "qr_code": sku.qr_code
                } for sku in event_transaction.skus.all()
            ],
            "user": {
                "firebase_uid": event_transaction.user.firebase_uid,
                "username": event_transaction.user.username,
                "full_name": event_transaction.user.full_name,
                "first_name": event_transaction.user.first_name,
                "last_name": event_transaction.user.last_name,
                "avatar": event_transaction.user.avatar,
                "is_online": event_transaction.user.is_online,
                "user_type": event_transaction.user.user_type,
                "last_seen": event_transaction.user.last_seen,
                "date_joined": event_transaction.user.date_joined,
                "show_avatar": event_transaction.user.show_avatar,
                "connection_status": event_transaction.user.connection_status,
                "connect_request_id": event_transaction.user.connect_request_id,
                "is_blocked": event_transaction.user.is_blocked,
                "badge": event_transaction.user.badge
            },
            "coupon": {
                "pk": event_coupon.pk if event_coupon else None,
                "code": event_coupon.code if event_coupon else None,
                "discount": event_coupon.discount if event_coupon else None,
                "fixed_amount": event_coupon.fixed_amount if event_coupon else None,
                "percentage": event_coupon.percentage if event_coupon else None,
                "expiry_date": event_coupon.expiry_date if event_coupon else None,
                "maximum_discount": event_coupon.maximum_discount if event_coupon else None,
                "minimum_amount": event_coupon.minimum_amount if event_coupon else None
            } if event_coupon else None,
            "status": event_transaction.status,
            "created_at": event_transaction.created_at,
            "expire_at": event_transaction.expire_at,
            "initial_full_cost": event_transaction.initial_full_cost,
            "cost_after_tax": event_transaction.cost_after_tax,
            "cost_before_discount": event_transaction.cost_before_discount,
            "cost_after_discount": event_transaction.cost_after_discount,
            "final_cost": event_transaction.final_cost
        }

        # Log the structured transaction details for debugging
        logging.info(f"Retrieved transaction details: {transaction_details}")
        
        return transaction_details


