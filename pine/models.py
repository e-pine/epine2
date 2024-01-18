from django.db import models
from django.contrib.auth.models import User, Group

class Category(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True, unique=True)
	def __str__(self):
		return self.name
    
class PinePrice(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
     name = models.CharField(max_length=200, null=True)
     price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

     def __str__(self):
          return self.name
class PineValue(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
     value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
     date = models.DateField(auto_now_add=False, null=True)

class BadValuePine(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
     value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
     date = models.DateField(auto_now_add=False, null=True)

class Crop(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
     number_planted = models.PositiveIntegerField(null=True)
     plant_date = models.DateField(auto_now_add=True, null=True)
     price_per_plant = models.DecimalField(max_digits=10, decimal_places=2, null=True)

     def __str__(self):
         return f"{self.category}"

     def calculate_total(self):
        if self.number_planted is not None and self.price_per_plant is not None:
            return self.number_planted * self.price_per_plant
        else:
            return None

     
class Yield(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
     number_yield = models.PositiveIntegerField(null=True)
     harvest_date = models.DateField(auto_now_add=False, null=True)
     value = models.ForeignKey(PineValue, on_delete=models.SET_NULL, null=True)
     calculated_value = models.FloatField(null=True)

class BadPine(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
     number_yield = models.PositiveIntegerField(null=True)
     harvest_date = models.DateField(auto_now_add=False, null=True)
     value = models.ForeignKey(BadValuePine, on_delete=models.SET_NULL, null=True)
     calculated_value = models.FloatField(null=True)

class WorkersExpense(models.Model):
      name = models.CharField(max_length=200, null=True)
      price_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
      workers = models.DecimalField(max_digits=10, decimal_places=0, null=True)
      days = models.DecimalField(max_digits=10, decimal_places=0, null=True)
      date = models.DateField(auto_now_add=True, null=True)

      def calculate_total(self):
        if self.price_pay is not None and self.workers is not None and self.days is not None:
            return self.price_pay * self.workers * self.days
        else:
            return None

      def __str__(self):
            return self.name
    
class TypeFerPes(models.Model):
    type = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.type
      
class ApplyFerPes(models.Model):
     product_name = models.CharField(max_length=200, null=True)
     type = models.ForeignKey(TypeFerPes, on_delete=models.CASCADE, null=True)
     price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
     quantity_used = models.DecimalField(max_digits=10, decimal_places=0, null=True)
     date = models.DateField(auto_now_add=True, null=True)

     def calculate_total(self):
        if self.price is not None and self.quantity_used is not None:
            return self.price * self.quantity_used
        else:
            return None

     def __str__(self):
            return self.product_name

# ----------------------------------------------------FOR HIGH QUALITY PINEAPPLES----------------------------------------------------#   
class BiddingProcess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_buy_pine = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    date = models.DateField(auto_now=True, null=True)
    
    def calculate_total_harvest(self):
         if self.total_buy_pine is not None:
            return self.total_buy_pine
         else:
            return None
         
    def calculate_total(self):
        if self.bid_price is not None and self.total_buy_pine is not None:
            return self.bid_price * self.total_buy_pine
        else:
            return None

    @classmethod
    def assign_user_from_group(cls, buyer):
        try:
            group = Group.objects.get(name=buyer)  # Replace 'group_name' with the name of your group
            user_to_assign = group.user_set.first()  # Assign the first user in the group
            bidding_process = cls(user=user_to_assign)
            bidding_process.save()
            return bidding_process
        except Group.DoesNotExist:
            return None  # Handle the case where the group doesn't exist

    def __str__(self):
        return str(self.user)

# ----------------------------------------------------FOR LOW QUALITY PINEAPPLES----------------------------------------------------# 
class HarvestedBad(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=None)
      category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
      total_number = models.DecimalField(max_digits=10, decimal_places=2)
      price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
      date = models.DateField(auto_now_add=True, null=True)

      def calculate_total_harvest(self):
         if self.total_number is not None:
            return self.total_number
         else:
            return None

      def calculate_total(self):
        if self.price is not None and self.total_number is not None:
            return self.price * self.total_number
        else:
            return None
        
      @classmethod
      def assign_user_from_group(cls, buyer):
        try:
            group = Group.objects.get(name=buyer)  # Replace 'group_name' with the name of your group
            user_to_assign = group.user_set.first()  # Assign the first user in the group
            bidding_process = cls(user=user_to_assign)
            bidding_process.save()
            return bidding_process
        except Group.DoesNotExist:
            return None 

# ----------------------------------------------------FOR REJECTED PINEAPPLES----------------------------------------------------#      
class RejectedPine(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=None)
     category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
     total_number = models.DecimalField(max_digits=10, decimal_places=2)
     price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     date = models.DateField(auto_now_add=True, null=True)

     def calculate_total_harvest(self):
         if self.total_number is not None:
            return self.total_number
         else:
            return None

     def calculate_total(self):
         if self.total_number is not None:
            return self.price * self.total_number
         else:
            return None

         
class StartExpense(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_number = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField(auto_now_add=True, null=True)

    def calculate_total(self):
        if self.price is not None and self.total_number is not None:
            return self.price * self.total_number
        else:
            return None
        

class Event(models.Model):  
    STATUS_CHOICES = [
        ('start', 'Start'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='start')

    def __str__(self):
        return str(self.name)
