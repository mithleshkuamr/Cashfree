# Cashfree/models.py
from django.db import models
from wagtail.models import ClusterableModel
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel
from wagtailautocomplete.edit_handlers import AutocompletePanel
from Events.tasks import task_expirePendingEventTransactions



class Order(models.Model):
    cf_order_id = models.CharField(max_length=50, primary_key=True)
    created_at = models.DateTimeField()
    customer_id = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    customer_uid = models.CharField(max_length=50, null=True, blank=True)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_currency = models.CharField(max_length=10, default='INR')
    order_expiry_time = models.DateTimeField()
    order_id = models.CharField(max_length=50)
    return_url = models.URLField(null=True, blank=True)
    notify_url = models.URLField(null=True, blank=True)
    payment_methods = models.CharField(max_length=255, null=True, blank=True)
    order_note = models.TextField(null=True, blank=True)
    order_status = models.CharField(max_length=50)
    payment_session_id = models.CharField(max_length=255)
    terminal_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.order_id

class Payment(models.Model):
    cf_payment_id = models.CharField(max_length=50, primary_key=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='payments')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_currency = models.CharField(max_length=10)
    payment_status = models.CharField(max_length=50)
    payment_time = models.DateTimeField()
    payment_message = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.JSONField(null=True, blank=True)
    payment_group = models.CharField(max_length=50)
    is_captured = models.BooleanField(default=False)
    payment_completion_time = models.DateTimeField(null=True, blank=True)
    bank_reference = models.CharField(max_length=50, null=True, blank=True)
    error_details = models.JSONField(null=True, blank=True)
    auth_id = models.CharField(max_length=50, null=True, blank=True)
    authorization = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.cf_payment_id
    
    
# class EventTransactionModel(ClusterableModel):
#     STATUS = (
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('cancelled', 'Cancelled'),
#         ('expired', 'Expired')
#     )
#     event = models.ForeignKey('EventPage', on_delete=models.CASCADE, null=True, blank=True)
#     show = models.ForeignKey('EventShowModel', on_delete=models.CASCADE, null=True, blank=True)
#     user = models.ForeignKey('CustomUser.CustomUser', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     status = models.CharField(max_length=10, choices=STATUS, default='pending')
#     initial_full_cost = models.FloatField(null=True, blank=True)
#     cost_after_tax = models.FloatField(null=True, blank=True)
#     cost_before_discount = models.FloatField(null=True, blank=True)
#     cost_after_discount = models.FloatField(null=True, blank=True)
#     final_cost = models.FloatField(null=True, blank=True)
#     coupon = models.ForeignKey('EventCouponModel', on_delete=models.SET_NULL, null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if self.id == None:
#             self.expires_at = timezone.now() + timedelta(minutes=10)
#             expire_at = make_aware(self.expires_at)
#             result = task_expirePendingEventTransactions.apply_async([self.id], eta=expire_at) 
#         super().save(*args, **kwargs)

#     panels = [
#         PageChooserPanel('event'),
#         AutocompletePanel('show'),
#         AutocompletePanel('user'),
#         FieldPanel('status'),
#         AutocompletePanel('coupon'),
#         InlinePanel('skus_purchased', label="SKUs Purchased"),
#     ]
