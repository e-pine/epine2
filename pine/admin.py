from django.contrib import admin
from .models import *

admin.site.register(Crop)
admin.site.register(Yield)
admin.site.register(Category)
admin.site.register(WorkersExpense)
admin.site.register(BadPine)
admin.site.register(BiddingProcess)
admin.site.register(HarvestedBad)
admin.site.register(RejectedPine)
admin.site.register(ApplyFerPes)
admin.site.register(StartExpense)

admin.site.register(Event)
admin.site.register(TypeFerPes)