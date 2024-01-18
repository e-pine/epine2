from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	def __str__(self):
		return self.name
	
class Stock(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
	item_name = models.CharField(max_length=50, blank=True, null=True)
	quantity = models.IntegerField(default='0', blank=True, null=True)
	receive_quantity = models.IntegerField(default='0', blank=True, null=True)
	receive_by = models.CharField(max_length=50, blank=True, null=True)
	issue_quantity = models.IntegerField(default='0', blank=True, null=True)
	issue_by = models.CharField(max_length=50, blank=True, null=True)
	issue_to = models.CharField(max_length=50, blank=True, null=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	reorder_level = models.IntegerField(default='0', blank=True, null=True)
	last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	price = models.IntegerField(default='0', blank=True, null=True)
	expiration_date = models.DateField(blank=True, null=True)
	

	def __str__(self):
		return self.item_name + ' ' + str(self.quantity)
	
class StockHistory(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
	item_name = models.CharField(max_length=50, blank=True, null=True)
	quantity = models.IntegerField(default='0', blank=True, null=True)
	receive_quantity = models.IntegerField(default='0', blank=True, null=True)
	receive_by = models.CharField(max_length=50, blank=True, null=True)
	issue_quantity = models.IntegerField(default='0', blank=True, null=True)
	issue_by = models.CharField(max_length=50, blank=True, null=True)
	issue_to = models.CharField(max_length=50, blank=True, null=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	reorder_level = models.IntegerField(default='0', blank=True, null=True)
	last_updated = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
	timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
	price = models.IntegerField(default='0', blank=True, null=True)

class ItemHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    action = models.CharField(max_length=50, default='Unknown') 
    issued_by = models.CharField(max_length=50, blank=True, null=True)  # Added field for the issuing user
    received_by = models.CharField(max_length=50, blank=True, null=True)
	

    def __str__(self):
        return f"{self.user.username} - {self.item.item_name} - {self.quantity} - {self.timestamp}"