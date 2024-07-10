# # Cashfree/urls.py
# from django.urls import path
# from .views import CreateOrderView, OrderListView,ProcessPaymentView,PaymentFormView,OrderDetailView,CashfreeCallbackView
# urlpatterns = [
#     path('create-order/', CreateOrderView.as_view(), name='create-order'),
#     path('orders/', OrderListView.as_view(), name='order-list'),  # Add this line if needed
#     path('orders/<str:order_id>/', OrderDetailView.as_view(), name='order-detail'), 
#     path('process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
#     #path('payment-form/<str:payment_session_id>/', PaymentFormView.as_view(), name='payment_form'),
#     # path('PaymentFormView/', PaymentFormView.as_view(), name='process-payment'),
#     # path('payment_view/', payment_view, name='payment'),
#     # path('payment-form/<str:payment_session_id>/', PaymentFormView.as_view(), name='payment_form'),
#     path('payment-form/<str:order_id>/', PaymentFormView.as_view(), name='payment_form'),
#     path('cashfree-callback/', CashfreeCallbackView.as_view(), name='cashfree_callback'),  # Add this line
    
# ]


# # from django.urls import path
# # from .views import CreateOrderView, OrderListView, ProcessPaymentView

# # urlpatterns = [
# #     path('create-order/', CreateOrderView.as_view(), name='create-order'),
# #     path('orders/', OrderListView.as_view(), name='order-list'),
# #     path('process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
# # ]

# from django.urls import path
# from .views import CreateOrderView, OrderListView, ProcessPaymentView, PaymentFormView, OrderDetailView, CashfreeCallbackView,FetchEventTransactionView

# urlpatterns = [
#     path('create-order/', CreateOrderView.as_view(), name='create-order'),
#     path('orders/', OrderListView.as_view(), name='order-list'),
#     path('orders/<str:order_id>/', OrderDetailView.as_view(), name='order-detail'),
#     path('process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
#     path('payment-form/<str:order_id>/', PaymentFormView.as_view(), name='payment-form'),
#     path('cashfree-callback/', CashfreeCallbackView.as_view(), name='cashfree-callback'),
#     path('fetch-transaction/<str:order_id>/', FetchEventTransactionView.as_view(), name='fetch_transaction'),
# ]
from django.urls import path
from .views import CreateOrderView, OrderListView, OrderDetailView, ProcessPaymentView, PaymentFormView, CashfreeCallbackView

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<str:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
    path('payment-form/<str:order_id>/', PaymentFormView.as_view(), name='payment-form'),
    path('cashfree-callback/', CashfreeCallbackView.as_view(), name='cashfree-callback'),
    
]
