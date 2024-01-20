from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.db.models import *
from django.http import JsonResponse
from chat.models import *
from django.db.models.functions import ExtractYear
from decimal import Decimal
from chat.models import *
from chat.forms import *
# from stockmgmt.models import *
from user.decorators import *

# Create your views here.
@login_required(login_url='login')
def category(request):
    category = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        cat_form = CategoryForm()

    context = { 'room_name': "broadcast",'cat_form': cat_form,'category': category }
    return render(request, 'crop_yield/category.html', context)

def cat_delete(request, pk):
	categorys = Category.objects.get(id=pk)
	if request.method == 'POST':
		categorys.delete()
		# messages.success(request, 'Deleted Succesfully')

		return redirect('category')
	return render(request, 'crop_yield/category_delete.html')

def calculate_total_price(queryset):
    total_value = 0
    for item in queryset:
        if item.value is not None:
            total_value += item.value
    return total_value

@login_required(login_url='login')
def crop(request):
    emp_rooms = Room.objects.filter(slug="employee")
    category_filter = request.GET.get('category')
    all_categories = Category.objects.all()
    # calculate the price per planting crop
    crops = Crop.objects.all()
    for crop in crops:
        crop.total_price = crop.calculate_total()
    # end

    if category_filter:
        crops = crops.filter(category__name=category_filter)
    # rooms = Room.objects.all()
    pine_price = PinePrice.objects.first()

    total_planted = Crop.objects.aggregate(total_planted=models.Sum('number_planted'))['total_planted']
    cost = None

    hawaii_crop = (
        Crop.objects.filter(category__name='Hawaii')
        .values('plant_date')
        .annotate(total_planted=Sum('number_planted'))
        .order_by('plant_date')
    )
    pormosa_crop = (
        Crop.objects.filter(category__name='Pormosa')
        .values('plant_date')
        .annotate(total_planted=Sum('number_planted'))
        .order_by('plant_date')
    )

    hawaii_pine_crop = PinePrice.objects.filter(category='2').first()
    pormosa_pine_crop = PinePrice.objects.filter(category='1').first()

    for item in hawaii_crop:
        item['price'] = float(item['total_planted']) * (float(hawaii_pine_crop.price) if hawaii_pine_crop else 0)

    for item in pormosa_crop:
        item['price'] = float(item['total_planted']) * (float(pormosa_pine_crop.price) if pormosa_pine_crop else 0)

    if total_planted is not None and pine_price is not None:
            cost = total_planted * pine_price.price

    if request.method == 'POST':
        form = CropForm(request.POST)  

        if form.is_valid():
            category = form.cleaned_data['category']
            number_planted = form.cleaned_data['number_planted']
            plant_date = form.cleaned_data.get('plant_date')  # Use get() to avoid KeyError

            existing_crop = Crop.objects.filter(category=category, plant_date=plant_date).first()

            if existing_crop:
                existing_crop.number_planted += number_planted
                existing_crop.price = pine_price
                existing_crop.product = existing_crop.number_planted * pine_price.price
                existing_crop.save()
            else:
                new_crop = form.save(commit=False)
                new_crop.price = pine_price
                new_crop.product = new_crop.number_planted * pine_price.price 
                new_crop.save()

            return redirect('crop')
    else:
        form = CropForm()


    context = { 'room_name': "broadcast",'crops': crops, 
               'form': form, 
               'pine_price': pine_price, 
               'hawaii_crop': hawaii_crop,
               'pormosa_crop': pormosa_crop,
               'all_categories': all_categories,
               'total_cost': cost, 
               'emp_rooms': emp_rooms,
            #    'rooms': rooms, 
               'room_name': "broadcast"}
    return render(request, 'crop_yield/crop.html', context)



@login_required(login_url='login')
def crop_update(request, pk):
    crop = Crop.objects.get(id=pk)
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            return redirect('emp_farm_planting')
    else:
        form = CropForm(instance=crop)
    context = { 'room_name': "broadcast",'form': form}
    return render(request, 'crop_yield/crop_update.html', context)

def crop_delete(request, pk):
    crop = Crop.objects.get(id=pk)
    crops = Crop.objects.all
    if request.method == 'POST':
        crop.delete()
        return redirect('crop')

    return render(request, 'crop_yield/crop_delete.html', {'crops':crops})
    

#--------------------------------------------MAIN-------------------------------------------------------------------------------------- 
# -------------crop list--------------------------------
@login_required(login_url='login')
@admin_only
def crop_list(request):
    crops = Crop.objects.all().order_by('-plant_date')

    crops_by_year = {}
    crops_by_category = {}

    for crop in crops:
        year = crop.plant_date.year
        if year not in crops_by_year:
            crops_by_year[year] = []
        if crop.category not in crops_by_category:
            crops_by_category[crop.category] = []

        crops_by_year[year].append(crop)
        crops_by_category[crop.category].append(crop)

    for year, crops_list in crops_by_year.items():
        for crop in crops_list:
            crop.total = crop.calculate_total()

    category_totals = {}
    for category, crops_list in crops_by_category.items():
        category_totals[category] = sum(c.calculate_total() for c in crops_list)

    yearly_totals = {}  

    for year, crops_list in crops_by_year.items():
        yearly_totals[year] = sum(c.number_planted for c in crops_list)

    if request.method == 'POST':
        crop_form = CropForm(request.POST)

        if crop_form.is_valid():
            crop_form.save()
            return redirect('crop_list')

    else:
        crop_form = CropForm()

    total_planted = Crop.objects.aggregate(total_planted=Sum('number_planted'))['total_planted']

    yearly_totals = {}  

    for year, crops_list in crops_by_year.items():
        yearly_totals[year] = sum(c.number_planted for c in crops_list)

    first_updated_data = None

    if yearly_totals:
        # Find the first updated data
        first_year, first_total_planted = next(iter(yearly_totals.items()))
        first_updated_data = {'year': first_year, 'total_planted': first_total_planted}

    pine_price = PinePrice.objects.first()
    cost = None

    if total_planted is not None and pine_price is not None:
        cost = total_planted * pine_price.price
    else:
        cost = 0
# end crop  
# --CROP--
    # crops = Crop.objects.all()
    # hawaii_crop = (
    # Crop.objects.filter(category__name='Hawaii')
    # .values('plant_date')
    # .annotate(total_planted=Sum('number_planted'))
    # .order_by('-plant_date')
    # )

    # pormosa_crop = (
    #     Crop.objects.filter(category__name='Pormosa')  # <-- This line should filter 'Pormosa' category, not 'Hawaii'
    #     .values('plant_date')
    #     .annotate(total_planted=Sum('number_planted'))
    #     .order_by('-plant_date')
    # )

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'yearly_totals': yearly_totals,
        'first_updated_data': first_updated_data,   

        'crop_form': crop_form,

        'cost': cost,
        # 'hawaii_crop': hawaii_crop,
        # 'pormosa_crop': pormosa_crop,
    }

    return render(request, 'crop_yield/crop_list.html', context)

# -------------------------------------------------------------------------------------------------------------------------------
@login_required(login_url='login')
@admin_only
def harvest_list(request):
    variety = Category.objects.all()
    harvested_good = BiddingProcess.objects.all().order_by('-date')
    total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
# Revenues for harvest///////////////////////////////////////////////////
    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year
        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []
        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total_harvest()

    total_buy_pine_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year
        if year not in total_buy_pine_by_year:
            total_buy_pine_by_year[year] = 0
        total_buy_pine_by_year[year] += bidding_process.total_buy_pine

    # --HARVESTED BAD-- #
    harvested_bad = HarvestedBad.objects.all().order_by('-date')

    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year
        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []
        harvested_bad_by_year[year].append(harvested_bads)
        harvested_bads.total = harvested_bads.calculate_total_harvest()
    
    # if request.method == 'POST':
    #     bad_quality_form = HarvestedBadForm(request.POST)

    #     if bad_quality_form.is_valid():
    #         bad_quality_form.save()
    #         return redirect('harvest_list')
        
    # else:
    #     bad_quality_form = HarvestedBadForm()
# ------------------------------------------------------------------------------------

    # --REJECTED PINE-- #
    rejected_pines = RejectedPine.objects.all().order_by('-date')

    harvested_rejected_by_year = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year
        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []
        harvested_rejected_by_year[year].append(rejected_pine)
        rejected_pine.total = rejected_pine.calculate_total_harvest()

    if request.method == 'POST':
        if 'harvested_bad_submit' in request.POST:
            bad_quality_form = HarvestedBadForm(request.POST)
            if bad_quality_form.is_valid():
                bad_quality_form.save()
                return redirect('harvest_list')

        if 'rejected_pine_submit' in request.POST:
            rejected_form = RejectedForm(request.POST)
            if rejected_form.is_valid():
                rejected_form.save()
                return redirect('harvest_list')

    else:
        bad_quality_form = HarvestedBadForm()
        rejected_form = RejectedForm()

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_good_by_year.keys() | harvested_bad_by_year.keys() | harvested_rejected_by_year.keys():
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []))
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []))
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
            'harvested_bad_total': harvested_bad_total,
            'harvested_rejected_total': harvested_rejected_total,
            'grand_total': harvested_good_total + harvested_bad_total + harvested_rejected_total,
        }
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
    
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_good_by_year': harvested_good_by_year,
        'harvested_bad_by_year': harvested_bad_by_year,
        'harvested_rejected_by_year': harvested_rejected_by_year,
      
        'totals_by_year': totals_by_year,  # Include the totals in the context
        'total_buy_pine_by_year': total_buy_pine_by_year,
        'total_harvest': total_harvest,
        'bad_quality_form': bad_quality_form,
        'variety': variety,
        'rejected_form': rejected_form
    }

    return render(request, 'crop_yield/harvest_list.html', context)

@login_required(login_url='login')
@admin_only
def harvest_bad_update(request, pk):
    harv_bad = HarvestedBad.objects.get(id=pk)
    if request.method == 'POST':
        harv_bad_form = HarvestedBadForm(request.POST, instance=harv_bad)
        if harv_bad_form.is_valid():
            harv_bad_form.save()
            return redirect('har_poor_quality')
    else:
        harv_bad_form = HarvestedBadForm(instance=harv_bad)

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harv_bad_form': harv_bad_form
        
        }
    return render(request, 'crop_yield/hav_bad_update.html', context)

def harvest_bad_delete(request, pk):
    try:
        bad_quality_del = HarvestedBad.objects.get(id=pk)
        bad_quality_del.delete()
        return JsonResponse({'success': True})
    except HarvestedBad.DoesNotExist:
        return JsonResponse({'success': False})

@login_required(login_url='login')
@admin_only
def rejected_pines_update(request, pk):
    rej = RejectedPine.objects.get(id=pk)
    if request.method == 'POST':
        rej_form = RejectedForm(request.POST, instance=rej)
        if rej_form.is_valid():
            rej_form.save()
            return redirect('hav_rejected')
    else:
        rej_form = RejectedForm(instance=rej)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'rej_form': rej_form
    }
    return render(request, 'crop_yield/rejected_pine_update.html', context)
    
def rejected_pines_delete(request, pk):
    try:
        rejected_pines_del = RejectedPine.objects.get(id=pk)
        rejected_pines_del.delete()
        return JsonResponse({'success': True})
    except RejectedPine.DoesNotExist:
        return JsonResponse({'success': False})

@login_required(login_url='login')
@admin_only
def harvest_revenues(request):
    harvested_good = BiddingProcess.objects.all().order_by('-date')

    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year
        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []
        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total()

    # --HARVESTED BAD-- #
    harvested_bad = HarvestedBad.objects.all().order_by('-date')
    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year
        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []
        harvested_bad_by_year[year].append(harvested_bads)
        harvested_bads.total = harvested_bads.calculate_total()

    # --REJECTED PINE-- #
    rejected_pines = RejectedPine.objects.all().order_by('date')
    harvested_rejected_by_year = {}
    
    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year
        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []
        harvested_rejected_by_year[year].append(rejected_pine)
        rejected_pine.total = rejected_pine.calculate_total()

    # Create dictionaries to store rejected_pines by year and by category
    rejected_pines_by_year = {}
    rejected_pines_by_category = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in rejected_pines_by_year:
            rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if rejected_pine.category not in rejected_pines_by_category:
            rejected_pines_by_category[rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        rejected_pines_by_year[year].append(rejected_pine)
        rejected_pines_by_category[rejected_pine.category].append(rejected_pine)

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_good_by_year.keys() | harvested_bad_by_year.keys():
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []) if b.total is not None)
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []) if h.total is not None)
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []) if i.total is not None)

        # Ensure that the totals are integers, setting them to 0 if they are None
        harvested_good_total = harvested_good_total if harvested_good_total is not None else 0
        harvested_bad_total = harvested_bad_total if harvested_bad_total is not None else 0
        harvested_rejected_total = harvested_rejected_total if harvested_rejected_total is not None else 0

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
            'harvested_bad_total': harvested_bad_total,
            'harvested_rejected_total': harvested_rejected_total,
            'grand_total': harvested_good_total + harvested_bad_total + harvested_rejected_total,
        }

        print("harvested_good_total:", harvested_good_total)
        print("harvested_bad_total:", harvested_bad_total)
        print("harvested_rejected_total:", harvested_rejected_total)



# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_good_by_year': harvested_good_by_year,
        'harvested_bad_by_year': harvested_bad_by_year,
        'rejected_pines_by_year': rejected_pines_by_year,
        'rejected_pines_by_category': rejected_pines_by_category,
        'totals_by_year': totals_by_year,  # Include the totals in the context
    }
    return render(request, 'revenues/harvest_revenues.html', context)

@login_required(login_url='login')
@admin_only
def revenues_goodquality(request):
    harvested_good = BiddingProcess.objects.all().order_by('date')

    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year
        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []
        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total()

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_good_by_year.keys():
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []) if b.total is not None)

        # Ensure that the totals are integers, setting them to 0 if they are None
        harvested_good_total = harvested_good_total if harvested_good_total is not None else 0

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
        }

        print("harvested_good_total:", harvested_good_total)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_good_by_year': harvested_good_by_year,
        'totals_by_year': totals_by_year,  # Include the totals in the context
    }
    return render(request, 'revenues/revenues_good_quality.html', context)

@login_required(login_url='login')
@admin_only
def revenues_badquality(request):
    # --HARVESTED BAD-- #
    harvested_bad = HarvestedBad.objects.all().order_by('-date')
    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year
        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []
        harvested_bad_by_year[year].append(harvested_bads)
        harvested_bads.total = harvested_bads.calculate_total()

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_bad_by_year.keys():
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []) if h.total is not None)

        harvested_bad_total = harvested_bad_total if harvested_bad_total is not None else 0

        totals_by_year[year] = {
            'harvested_bad_total': harvested_bad_total,
        }
        print("harvested_bad_total:", harvested_bad_total)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_bad_by_year': harvested_bad_by_year,
        'totals_by_year': totals_by_year,  # Include the totals in the context
    }
    return render(request, 'revenues/revenues_poor_quality.html', context)

@login_required(login_url='login')
@admin_only
def revenues_rejected(request):
    # --REJECTED PINE-- #
    rejected_pines = RejectedPine.objects.all().order_by('date')
    harvested_rejected_by_year = {}
    
    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year
        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []
        harvested_rejected_by_year[year].append(rejected_pine)
        rejected_pine.total = rejected_pine.calculate_total()

    # Create dictionaries to store rejected_pines by year and by category
    rejected_pines_by_year = {}
    rejected_pines_by_category = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in rejected_pines_by_year:
            rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if rejected_pine.category not in rejected_pines_by_category:
            rejected_pines_by_category[rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        rejected_pines_by_year[year].append(rejected_pine)
        rejected_pines_by_category[rejected_pine.category].append(rejected_pine)

    # Sum the totals for each year
    totals_by_year = {}

    for year in rejected_pines_by_year.keys():
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []) if i.total is not None)

        harvested_rejected_total = harvested_rejected_total if harvested_rejected_total is not None else 0

        totals_by_year[year] = {
            'harvested_rejected_total': harvested_rejected_total,
        }

        print("harvested_rejected_total:", harvested_rejected_total)



# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'rejected_pines_by_year': rejected_pines_by_year,
        'rejected_pines_by_category': rejected_pines_by_category,
        'totals_by_year': totals_by_year,  # Include the totals in the context
    }
    return render(request, 'revenues/revenues_rejected.html', context)


# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
from django.db.models import Sum, F
from django.db.models.functions import ExtractYear
@login_required(login_url='login')
@admin_only
def crop_expense(request):
# PLANTING EXPENSE
    crops = Crop.objects.all().order_by('-plant_date')

    crops_by_year = {}
    crops_by_category = {}

    for crop in crops:
        year = crop.plant_date.year

        if year not in crops_by_year:
            crops_by_year[year] = []

        if crop.category not in crops_by_category:
            crops_by_category[crop.category] = []

        crops_by_year[year].append(crop)
        crops_by_category[crop.category].append(crop)

    for year, crops_list in crops_by_year.items():
        for crop in crops_list:
            crop.total = crop.calculate_total()

    category_totals = {}

    for category, crops_list in crops_by_category.items():
        category_total = 0 

        # Calculate the total for each crop in the current category
        for crop in crops_list:
            crop_total = crop.calculate_total()  # Calculate the total for the current crop
            if crop_total is not None:
                category_total += crop_total  # Add the crop total to the category total

        category_totals[category] = category_total  # Store the category total in the dictionary

    # Calculate the grand total by summing up all category totals
    grand_total = sum(category_totals.values())
    
    crop_yearly_totals = Crop.objects.annotate(
    year=ExtractYear('plant_date')
    ).values('year').annotate(
        total=Sum(F('number_planted') * F('price_per_plant'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

# -------------------------------------------------------------------------------------------------------------------------------------
# --WORK EXPENSE
    worker_expenses = WorkersExpense.objects.all().order_by('-date')

# Create a dictionary to store worker expenses by year
    worker_expenses_by_year = {}
    grand_total_worker_expenses_by_year = {}  # Initialize a dictionary for grand totals by year

    for expense in worker_expenses:
        year = expense.date.year

        if year not in worker_expenses_by_year:
            worker_expenses_by_year[year] = []

        # Calculate the total for each expense
        expense.total = expense.calculate_total()

        worker_expenses_by_year[year].append(expense)

    for year, year_expenses in worker_expenses_by_year.items():
        # Calculate the grand total for each year
        grand_total_worker_expenses_by_year[year] = sum(expense.calculate_total() for expense in year_expenses if expense.total is not None)

    # Calculate the overall grand total for all years
    grand_total_worker_expenses = sum(grand_total_worker_expenses_by_year.values())

    # total by year
    work_yearly_totals = WorkersExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price_pay') * F('workers') * F('days'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in work_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        work_form = WorkerForm(request.POST)

        if work_form.is_valid():
            work_form.save()
            return redirect('crop_expense')
        
    else:
        work_form = WorkerForm()

# ------------------------------------------------------------------------------------------------------------------------------
#  FERTILIZER AND PESTICIDE EXPENSE
    fer_pes_expenses = ApplyFerPes.objects.all().order_by('-date')

    # Create a dictionary to store fer_pes_expenses by year
    fer_pes_expenses_by_year = {}

    for fer_expense in fer_pes_expenses:
        year = fer_expense.date.year

        if year not in fer_pes_expenses_by_year:
            fer_pes_expenses_by_year[year] = []

        # Calculate the total for each expense
        fer_expense.total = fer_expense.calculate_total()

        fer_pes_expenses_by_year[year].append(fer_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in fer_pes_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    ferpes_yearly_totals = ApplyFerPes.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('quantity_used'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in ferpes_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        ferpes_form = ApplyFerPesForm(request.POST)

        if ferpes_form.is_valid():
            ferpes_form.save()
            return redirect('crop_expense')
        
    else:
        ferpes_form = ApplyFerPesForm()
# -----------------------------------------------------------------------------------------------------------------------------------------------------
    # start_expense = StartExpense.objects.aggregate(start_expense=models.Sum('total_buy_pine'))['total_harvest']
    # total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
    
    # Start expense
    start_expenses = StartExpense.objects.all()

    # Create a dictionary to store start_expenses by year
    start_expenses_by_year = {}

    for start_expense in start_expenses:
        year = start_expense.date.year

        if year not in start_expenses_by_year:
            start_expenses_by_year[year] = []

        # Calculate the total for each expense
        start_expense.total = start_expense.calculate_total()

        start_expenses_by_year[year].append(start_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in start_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    start_yearly_totals = StartExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('total_number'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in start_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        start_form = StartExpenceForm(request.POST)

        if start_form.is_valid():
            start_form.save()
            return redirect('crop_expense')
        
    else:
        start_form = StartExpenceForm()
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    crop_yearly_totals_list = list(crop_yearly_totals)
    work_yearly_totals_list = list(work_yearly_totals)
    ferpesyearly_totals_list = list(ferpes_yearly_totals)
    start_yearly_totals_list = list(start_yearly_totals)
    
    # Combine the lists
    total_expense_yearly = crop_yearly_totals_list + work_yearly_totals_list + ferpesyearly_totals_list + start_yearly_totals_list
    
    yearly_totals_dict = {}

    for entry in total_expense_yearly:
        year = entry['year']
        total = entry['total']
        
        if year in yearly_totals_dict:
            yearly_totals_dict[year] += total
        else:
            yearly_totals_dict[year] = total

    # Convert the dictionary back to a list of dictionaries
    total_expense_yearly = [{'year': year, 'total': total} for year, total in yearly_totals_dict.items()]

    overall_total_expenses = 0  # Initialize the overall total expenses

    for entry in total_expense_yearly:
        total_expenses = entry['total']
        overall_total_expenses += total_expenses

    print(f"Overall Total Expenses: {overall_total_expenses}")

    currentYearIndex = 0

# ------------------------------------------------------------------------------------------------
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'grand_total': grand_total,  # Add the grand total to the context
        'worker_expenses_by_year': worker_expenses_by_year,
        'start_expenses_by_year': start_expenses_by_year,

        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,

        'crop_yearly_totals': crop_yearly_totals,
        'work_yearly_totals': work_yearly_totals,
        'ferpes_yearly_totals': ferpes_yearly_totals,
        'total_expense_yearly': total_expense_yearly,
        'work_form': work_form,
        'ferpes_form': ferpes_form,
        'start_form': start_form,

        'currentYearIndex': currentYearIndex
        
    }

    return render(request, 'crop_yield/crop_expense.html', context)

@login_required(login_url='login')
@admin_only
def work_expense_update(request, pk):
    workexpe = WorkersExpense.objects.get(id=pk)
    if request.method == 'POST':
        work_expense_form = WorkerForm(request.POST, instance=workexpe)
        if work_expense_form.is_valid():
            work_expense_form.save()
            return redirect('expe_labor')
    else:
        work_expense_form = WorkerForm(instance=workexpe)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'work_expense_form': work_expense_form}
    return render(request, 'crop_yield/work_expense_update.html', context)


allowed_users(allowed_roles=['employee'])
def work_expense_update_emp(request, pk):
    workexpe = WorkersExpense.objects.get(id=pk)
    if request.method == 'POST':
        work_expense_form = WorkerForm(request.POST, instance=workexpe)
        if work_expense_form.is_valid():
            work_expense_form.save()
            return redirect('emp_farm_labor')
    else:
        work_expense_form = WorkerForm(instance=workexpe)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'work_expense_form': work_expense_form}
    return render(request, 'crop_yield/work_expense_update_emp.html', context)

def work_expense_delete(request, pk):
    try:
        work_expense_del = WorkersExpense.objects.get(id=pk)
        work_expense_del.delete()
        return JsonResponse({'success': True})
    except WorkersExpense.DoesNotExist:
        return JsonResponse({'success': False})

@login_required(login_url='login')
@admin_only
def fer_expense_update(request, pk):
    ferpes = ApplyFerPes.objects.get(id=pk)
    if request.method == 'POST':
        fer_pes_form = ApplyFerPesForm(request.POST, instance=ferpes)
        if fer_pes_form.is_valid():
            fer_pes_form.save()
            return redirect('expe_fer_pes')
    else:
        fer_pes_form = ApplyFerPesForm(instance=ferpes)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'fer_pes_form': fer_pes_form}
    return render(request, 'crop_yield/fer_pes_update.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['employee'])
def fer_expense_update_emp(request, pk):
    ferpes = ApplyFerPes.objects.get(id=pk)
    if request.method == 'POST':
        fer_pes_form = ApplyFerPesForm(request.POST, instance=ferpes)
        if fer_pes_form.is_valid():
            fer_pes_form.save()
            return redirect('emp_farm_fer_pes')
    else:
        fer_pes_form = ApplyFerPesForm(instance=ferpes)
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'fer_pes_form': fer_pes_form}
    return render(request, 'crop_yield/fer_pes_update.html', context)

 
def fer_expense_delete(request, pk):
    try:
        fer_expense_del = ApplyFerPes.objects.get(id=pk)
        fer_expense_del.delete()
        return JsonResponse({'success': True})
    except ApplyFerPes.DoesNotExist:
        return JsonResponse({'success': False})

@login_required(login_url='login')
@admin_only
def sales_trends(request):
    # for revenues____________________________________
    revenues_harvested_good = BiddingProcess.objects.all().order_by('-date')

    revenues_harvested_good_by_year = {}

    for revenues_bidding_process in revenues_harvested_good:
        year = revenues_bidding_process.date.year
        if year not in revenues_harvested_good_by_year:
            revenues_harvested_good_by_year[year] = []
        revenues_harvested_good_by_year[year].append(revenues_bidding_process)
        revenues_bidding_process.total = revenues_bidding_process.calculate_total()

    # --HARVESTED BAD-- #
    revenues_harvested_bad = HarvestedBad.objects.all().order_by('-date')
    revenues_harvested_bad_by_year = {}

    for revenues_harvested_bads in revenues_harvested_bad:
        year = revenues_harvested_bads.date.year
        if year not in revenues_harvested_bad_by_year:
            revenues_harvested_bad_by_year[year] = []
        revenues_harvested_bad_by_year[year].append(revenues_harvested_bads)
        revenues_harvested_bads.total = revenues_harvested_bads.calculate_total()

    # --REJECTED PINE-- #
    revenues_rejected_pines = RejectedPine.objects.all().order_by('date')
    revenues_harvested_rejected_by_year = {}
    
    for revenues_rejected_pine in revenues_rejected_pines:
        year = revenues_rejected_pine.date.year
        if year not in revenues_harvested_rejected_by_year:
            revenues_harvested_rejected_by_year[year] = []
        revenues_harvested_rejected_by_year[year].append(revenues_rejected_pine)
        revenues_rejected_pine.total = revenues_rejected_pine.calculate_total()

    # Create dictionaries to store revenues_rejected_pines by year and by category
    revenues_rejected_pines_by_year = {}
    revenues_rejected_pines_by_category = {}

    for revenues_rejected_pine in revenues_rejected_pines:
        year = revenues_rejected_pine.date.year

        if year not in revenues_rejected_pines_by_year:
            revenues_rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if revenues_rejected_pine.category not in revenues_rejected_pines_by_category:
            revenues_rejected_pines_by_category[revenues_rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        revenues_rejected_pines_by_year[year].append(revenues_rejected_pine)
        revenues_rejected_pines_by_category[revenues_rejected_pine.category].append(revenues_rejected_pine)
    totals_by_year = {}

    for year in revenues_harvested_good_by_year.keys() | revenues_harvested_bad_by_year.keys() | revenues_harvested_rejected_by_year.keys():
        revenues_harvested_good_total = sum(b.total for b in revenues_harvested_good_by_year.get(year, []))
        revenues_harvested_bad_total = sum(h.total for h in revenues_harvested_bad_by_year.get(year, []))
        revenues_harvested_rejected_total = sum(i.total for i in revenues_harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'revenues_harvested_good_total': revenues_harvested_good_total,
            'revenues_harvested_bad_total': revenues_harvested_bad_total,
            'revenues_harvested_rejected_total': revenues_harvested_rejected_total,
            'revenues_grand_total': revenues_harvested_good_total + revenues_harvested_bad_total + revenues_harvested_rejected_total,
        }
# for crop revenues
    harvested_good = BiddingProcess.objects.all().order_by('-date')
    # total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []

        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total()

    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []

        harvested_good_by_year[year].append(bidding_process)

        bidding_process.total = bidding_process.calculate_total_harvest()

    total_buy_pine_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in total_buy_pine_by_year:
            total_buy_pine_by_year[year] = 0

        total_buy_pine_by_year[year] += bidding_process.total_buy_pine

    # --HARVESTED BAD-- #
    harvested_bad = HarvestedBad.objects.all().order_by('-date')

    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year

        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []

        harvested_bad_by_year[year].append(harvested_bads)

        harvested_bads.total = harvested_bads.calculate_total_harvest()
# ------------------------------------------------------------------------------------

    # --REJECTED PINE-- #
    rejected_pines = RejectedPine.objects.all().order_by('-date')

    harvested_rejected_by_year = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []

        harvested_rejected_by_year[year].append(rejected_pine)

        rejected_pine.total = rejected_pine.calculate_total_harvest()

    rejected_pines_by_year = {}
    rejected_pines_by_category = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in rejected_pines_by_year:
            rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if rejected_pine.category not in rejected_pines_by_category:
            rejected_pines_by_category[rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        rejected_pines_by_year[year].append(rejected_pine)
        rejected_pines_by_category[rejected_pine.category].append(rejected_pine)

    # Sum the totals for each year
    totals_by_year = {}

    if request.method == 'POST':
        if 'harvested_bad_submit' in request.POST:
            bad_quality_form = HarvestedBadForm(request.POST)
            if bad_quality_form.is_valid():
                bad_quality_form.save()
                return redirect('harvest_list')

        if 'rejected_pine_submit' in request.POST:
            rejected_form = RejectedForm(request.POST)
            if rejected_form.is_valid():
                rejected_form.save()
                return redirect('harvest_list')

    else:
        bad_quality_form = HarvestedBadForm()
        rejected_form = RejectedForm()

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_good_by_year.keys() | harvested_bad_by_year.keys() | harvested_rejected_by_year.keys():
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []))
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []))
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
            'harvested_bad_total': harvested_bad_total,
            'harvested_rejected_total': harvested_rejected_total,
            'grand_total': harvested_good_total + harvested_bad_total,
        }

    # ----------------------------------------------------------------------------------------------------------------
    harvested_good1 = BiddingProcess.objects.all().order_by('-date')
    harvested_good_by_year1 = {}

    for bidding_process1 in harvested_good1:
        year = bidding_process1.date.year

        if year not in harvested_good_by_year1:
            harvested_good_by_year1[year] = []

        harvested_good_by_year1[year].append(bidding_process1)
        bidding_process1.total = bidding_process1.calculate_total_harvest()

    harvested_good_by_year1 = {}

    for bidding_process1 in harvested_good:
        year = bidding_process1.date.year

        if year not in harvested_good_by_year1:
            harvested_good_by_year1[year] = []

        harvested_good_by_year1[year].append(bidding_process1)

        bidding_process1.total = bidding_process1.calculate_total_harvest()

    total_buy_pine_by_year1 = {}

    for bidding_process1 in harvested_good:
        year = bidding_process1.date.year

        if year not in total_buy_pine_by_year1:
            total_buy_pine_by_year1[year] = 0

        total_buy_pine_by_year1[year] += bidding_process1.total_buy_pine

    # --HARVESTED BAD-- #
    harvested_bad1 = HarvestedBad.objects.all().order_by('-date')

    harvested_bad_by_year1 = {}

    for harvested_bads1 in harvested_bad1:
        year = harvested_bads1.date.year

        if year not in harvested_bad_by_year1:
            harvested_bad_by_year1[year] = []

        harvested_bad_by_year1[year].append(harvested_bads1)

        harvested_bads1.total = harvested_bads1.calculate_total_harvest()
# ------------------------------------------------------------------------------------

    # --REJECTED PINE-- #
    rejected_pines1 = RejectedPine.objects.all().order_by('-date')

    harvested_rejected_by_year1 = {}

    for rejected_pine2 in rejected_pines1:
        year = rejected_pine2.date.year

        if year not in harvested_rejected_by_year1:
            harvested_rejected_by_year1[year] = []

        harvested_rejected_by_year1[year].append(rejected_pine2)

        rejected_pine2.total = rejected_pine2.calculate_total_harvest()

    rejected_pines_by_year1 = {}
    rejected_pines_by_category1 = {}

    for rejected_pine2 in rejected_pines1:
        year = rejected_pine2.date.year

        if year not in rejected_pines_by_year1:
            rejected_pines_by_year1[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if rejected_pine2.category not in rejected_pines_by_category1:
            rejected_pines_by_category1[rejected_pine2.category] = []

        # Append the rejected_pine to the lists for that year and category
        rejected_pines_by_year1[year].append(rejected_pine2)
        rejected_pines_by_category1[rejected_pine2.category].append(rejected_pine2)

    totals_by_year = {}

    for year in harvested_good_by_year1.keys() | harvested_bad_by_year1.keys() | harvested_rejected_by_year1.keys():
        harvested_good_total1 = sum(b.total for b in harvested_good_by_year1.get(year, []))
        harvested_bad_total1 = sum(h.total for h in harvested_bad_by_year1.get(year, []))
        harvested_rejected_total1 = sum(i.total for i in harvested_rejected_by_year1.get(year, []))

        totals_by_year[year] = {
            'harvested_good_total1': harvested_good_total1,
            'harvested_bad_total1': harvested_bad_total1,
            'harvested_rejected_total1': harvested_rejected_total1,
            'grand_total1': harvested_good_total1 + harvested_bad_total1,
        }
# ___________________________________________________________________________________________________________________________
# PLANTING EXPENSE
    crops = Crop.objects.all().order_by('-plant_date')

    crops_by_year = {}
    crops_by_category = {}

    for crop in crops:
        year = crop.plant_date.year

        if year not in crops_by_year:
            crops_by_year[year] = []

        if crop.category not in crops_by_category:
            crops_by_category[crop.category] = []

        crops_by_year[year].append(crop)
        crops_by_category[crop.category].append(crop)

    for year, crops_list in crops_by_year.items():
        for crop in crops_list:
            crop.total = crop.calculate_total()

    category_totals = {}

    for category, crops_list in crops_by_category.items():
        category_total = 0 

        # Calculate the total for each crop in the current category
        for crop in crops_list:
            crop_total = crop.calculate_total()  # Calculate the total for the current crop
            if crop_total is not None:
                category_total += crop_total  # Add the crop total to the category total

        category_totals[category] = category_total  # Store the category total in the dictionary

    # Calculate the grand total by summing up all category totals
    grand_total = sum(category_totals.values())
    
    crop_yearly_totals = Crop.objects.annotate(
    year=ExtractYear('plant_date')
    ).values('year').annotate(
        total=Sum(F('number_planted') * F('price_per_plant'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')
# -------------------------------------------------------------------------------------------------------------------------------------
# --WORK EXPENSE
    worker_expenses = WorkersExpense.objects.all().order_by('-date')

# Create a dictionary to store worker expenses by year
    worker_expenses_by_year = {}
    grand_total_worker_expenses_by_year = {}  # Initialize a dictionary for grand totals by year

    for expense in worker_expenses:
        year = expense.date.year

        if year not in worker_expenses_by_year:
            worker_expenses_by_year[year] = []

        # Calculate the total for each expense
        expense.total = expense.calculate_total()

        worker_expenses_by_year[year].append(expense)

    for year, year_expenses in worker_expenses_by_year.items():
        # Calculate the grand total for each year
        grand_total_worker_expenses_by_year[year] = sum(expense.calculate_total() for expense in year_expenses if expense.total is not None)

    # Calculate the overall grand total for all years
    grand_total_worker_expenses = sum(grand_total_worker_expenses_by_year.values())

    # total by year
    work_yearly_totals = WorkersExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price_pay') * F('workers') * F('days'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in work_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        work_form = WorkerForm(request.POST)

        if work_form.is_valid():
            work_form.save()
            return redirect('crop_expense')
        
    else:
        work_form = WorkerForm()
# ------------------------------------------------------------------------------------------------------------------------------
#  FERTILIZER AND PESTICIDE EXPENSE
    fer_pes_expenses = ApplyFerPes.objects.all().order_by('-date')

    # Create a dictionary to store fer_pes_expenses by year
    fer_pes_expenses_by_year = {}

    for fer_expense in fer_pes_expenses:
        year = fer_expense.date.year

        if year not in fer_pes_expenses_by_year:
            fer_pes_expenses_by_year[year] = []

        # Calculate the total for each expense
        fer_expense.total = fer_expense.calculate_total()

        fer_pes_expenses_by_year[year].append(fer_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in fer_pes_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    ferpes_yearly_totals = ApplyFerPes.objects.annotate(
        year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('quantity_used'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    # Check if ferpes_yearly_totals is not empty before entering the loop
    if ferpes_yearly_totals:
        for entry in ferpes_yearly_totals:
            year = entry['year']
            total_expenses = entry['total']
            print(f"Year {year}: Total Expenses = {total_expenses}")
    else:
        print("No expenses data available.")

    if request.method == 'POST':
        ferpes_form = ApplyFerPesForm(request.POST)

        if ferpes_form.is_valid():
            ferpes_form.save()
            return redirect('crop_expense')
    else:
        ferpes_form = ApplyFerPesForm()
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    crop_yearly_totals_list = list(crop_yearly_totals)
    work_yearly_totals_list = list(work_yearly_totals)
    yearly_totals_list = list(ferpes_yearly_totals)
    # Combine the lists
    total_expense_yearly = crop_yearly_totals_list + work_yearly_totals_list + yearly_totals_list
    yearly_totals_dict = {}

    for entry in total_expense_yearly:
        year = entry['year']
        total = entry['total']
        if year in yearly_totals_dict:
            yearly_totals_dict[year] += total
        else:
            yearly_totals_dict[year] = total
 
    total_expense_yearly = [{'year': year, 'total': total} for year, total in yearly_totals_dict.items()]
    overall_total_expenses = 0  

    for entry in total_expense_yearly:
        total_expenses = entry['total']
        overall_total_expenses += total_expenses

    print(f"Overall Total Expenses: {overall_total_expenses}")
    total_expense_yearly_percent = [{'year': entry['year'], 'total': entry['total'] / 100} for entry in total_expense_yearly]

        
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')

# for revenues____________________________________
    revenues_harvested_good = BiddingProcess.objects.all().order_by('-date')

    revenues_harvested_good_by_year = {}

    for revenues_bidding_process in revenues_harvested_good:
        year = revenues_bidding_process.date.year
        if year not in revenues_harvested_good_by_year:
            revenues_harvested_good_by_year[year] = []
        revenues_harvested_good_by_year[year].append(revenues_bidding_process)
        revenues_bidding_process.total = revenues_bidding_process.calculate_total()

    # --HARVESTED BAD-- #
    revenues_harvested_bad = HarvestedBad.objects.all().order_by('-date')
    revenues_harvested_bad_by_year = {}

    for revenues_harvested_bads in revenues_harvested_bad:
        year = revenues_harvested_bads.date.year
        if year not in revenues_harvested_bad_by_year:
            revenues_harvested_bad_by_year[year] = []
        revenues_harvested_bad_by_year[year].append(revenues_harvested_bads)
        revenues_harvested_bads.total = revenues_harvested_bads.calculate_total()

    # --REJECTED PINE-- #
    revenues_rejected_pines = RejectedPine.objects.all().order_by('date')
    revenues_harvested_rejected_by_year = {}
    
    for revenues_rejected_pine in revenues_rejected_pines:
        year = revenues_rejected_pine.date.year
        if year not in revenues_harvested_rejected_by_year:
            revenues_harvested_rejected_by_year[year] = []
        revenues_harvested_rejected_by_year[year].append(revenues_rejected_pine)
        revenues_rejected_pine.total = revenues_rejected_pine.calculate_total()

    # Create dictionaries to store revenues_rejected_pines by year and by category
    revenues_rejected_pines_by_year = {}
    revenues_rejected_pines_by_category = {}

    for revenues_rejected_pine in revenues_rejected_pines:
        year = revenues_rejected_pine.date.year

        if year not in revenues_rejected_pines_by_year:
            revenues_rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if revenues_rejected_pine.category not in revenues_rejected_pines_by_category:
            revenues_rejected_pines_by_category[revenues_rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        revenues_rejected_pines_by_year[year].append(revenues_rejected_pine)
        revenues_rejected_pines_by_category[revenues_rejected_pine.category].append(revenues_rejected_pine)
    totals_by_year = {}

    for year in revenues_harvested_good_by_year.keys() | revenues_harvested_bad_by_year.keys() | revenues_harvested_rejected_by_year.keys():
        revenues_harvested_good_total = sum(b.total for b in revenues_harvested_good_by_year.get(year, []))
        revenues_harvested_bad_total = sum(h.total for h in revenues_harvested_bad_by_year.get(year, []))
        revenues_harvested_rejected_total = sum(i.total for i in revenues_harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'revenues_harvested_good_total': revenues_harvested_good_total,
            'revenues_harvested_bad_total': revenues_harvested_bad_total,
            'revenues_harvested_rejected_total': revenues_harvested_rejected_total,
            'revenues_grand_total': revenues_harvested_good_total + revenues_harvested_bad_total + revenues_harvested_rejected_total,
        }

    # ___________________________________________________________________________________________________________________
    overall = {}
    for year, totals in totals_by_year.items():
        total_expense = next((entry['total'] for entry in total_expense_yearly if entry['year'] == year), 0)
        overall[year] = totals['revenues_grand_total'] - total_expense
    roi_values = {}  # Dictionary to store ROI values for each year
    for year, totals in totals_by_year.items():
        total_expense = next((entry['total'] for entry in total_expense_yearly if entry['year'] == year), 0)
        # Calculate ROI for the current year
        roi_values[year] = ((totals['revenues_grand_total'] - total_expense) / total_expense * 100) if total_expense != 0 else 0
    # 'roi_values' now contains the ROI values for each year

        # combined_data = [(year, overall.get(year, 'N/A'), roi_values.get(year, 'N/A')) for year in set(overall) | set(roi_values)]
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
# harvest revenues
        'harvested_good_by_year': harvested_good_by_year,
        'harvested_bad_by_year': harvested_bad_by_year,
        'rejected_pines_by_year': rejected_pines_by_year,
        'rejected_pines_by_category': rejected_pines_by_category,
        'totals_by_year': totals_by_year,  # Include the totals in the context

        'harvested_good_by_year1': harvested_good_by_year1,
        'harvested_bad_by_year1': harvested_bad_by_year1,
        'rejected_pines_by_year1': rejected_pines_by_year1,
        'rejected_pines_by_category1': rejected_pines_by_category1,

        'revenues_harvested_good_by_year': revenues_harvested_good_by_year,
        'revenues_harvested_bad_by_year': revenues_harvested_bad_by_year,
        'revenues_rejected_pines_by_year': revenues_rejected_pines_by_year,
        'revenues_rejected_pines_by_category': revenues_rejected_pines_by_category,
# __________________________________________________________________________________________
# crop expense
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'grand_total': grand_total, 
        # 'revenues_grand_total': revenues_grand_total, # Add the grand total to the context
        'worker_expenses_by_year': worker_expenses_by_year,
        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,

        'crop_yearly_totals': crop_yearly_totals,
        'work_yearly_totals': work_yearly_totals,
        'ferpes_yearly_totals': ferpes_yearly_totals,
        'total_expense_yearly': total_expense_yearly,
        'total_expense_yearly_percent': total_expense_yearly_percent,

        'overall': overall,
        'roi_values': roi_values,

        # 'combined_data': combined_data,
    }
    return render(request, 'crop_yield/sales_trend.html', context)


@login_required(login_url='login')
@admin_only
def har_high_quality(request):
    harvested_good = BiddingProcess.objects.all().order_by('-date')
    total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
# Revenues for harvest///////////////////////////////////////////////////
    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []

        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total()

    harvested_good_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []

        harvested_good_by_year[year].append(bidding_process)

        bidding_process.total = bidding_process.calculate_total_harvest()

    total_buy_pine_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in total_buy_pine_by_year:
            total_buy_pine_by_year[year] = 0

        total_buy_pine_by_year[year] += bidding_process.total_buy_pine

    # --HARVESTED BAD-- #
    harvested_bad = HarvestedBad.objects.all().order_by('-date')

    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year

        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []

        harvested_bad_by_year[year].append(harvested_bads)

        harvested_bads.total = harvested_bads.calculate_total_harvest()
    
    # if request.method == 'POST':
    #     bad_quality_form = HarvestedBadForm(request.POST)

    #     if bad_quality_form.is_valid():
    #         bad_quality_form.save()
    #         return redirect('harvest_list')
        
    # else:
    #     bad_quality_form = HarvestedBadForm()
# ------------------------------------------------------------------------------------

    # --REJECTED PINE-- #
    rejected_pines = RejectedPine.objects.all().order_by('-date')

    harvested_rejected_by_year = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []

        harvested_rejected_by_year[year].append(rejected_pine)

        rejected_pine.total = rejected_pine.calculate_total_harvest()

    rejected_pines_by_year = {}
    rejected_pines_by_category = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in rejected_pines_by_year:
            rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if rejected_pine.category not in rejected_pines_by_category:
            rejected_pines_by_category[rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        rejected_pines_by_year[year].append(rejected_pine)
        rejected_pines_by_category[rejected_pine.category].append(rejected_pine)

    # Sum the totals for each year
    totals_by_year = {}

    if request.method == 'POST':
        if 'harvested_bad_submit' in request.POST:
            bad_quality_form = HarvestedBadForm(request.POST)
            if bad_quality_form.is_valid():
                bad_quality_form.save()
                return redirect('harvest_list')

        if 'rejected_pine_submit' in request.POST:
            rejected_form = RejectedForm(request.POST)
            if rejected_form.is_valid():
                rejected_form.save()
                return redirect('harvest_list')

    else:
        bad_quality_form = HarvestedBadForm()
        rejected_form = RejectedForm()

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_good_by_year.keys() | harvested_bad_by_year.keys() | harvested_rejected_by_year.keys():
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []))
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []))
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
            'harvested_bad_total': harvested_bad_total,
            'harvested_rejected_total': harvested_rejected_total,
            'grand_total': harvested_good_total + harvested_bad_total,
        }

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_good_by_year': harvested_good_by_year,
        'harvested_bad_by_year': harvested_bad_by_year,
        'harvested_rejected_by_year': harvested_rejected_by_year,
        'rejected_pines_by_year': rejected_pines_by_year,
        'rejected_pines_by_category': rejected_pines_by_category,
        'totals_by_year': totals_by_year,  
        'total_buy_pine_by_year': total_buy_pine_by_year,
        'total_harvest': total_harvest,
        'bad_quality_form': bad_quality_form,
        'rejected_form': rejected_form
    }
    return render(request, 'crop_yield/harvest/harv_high_quality.html', context)

@login_required(login_url='login')
@admin_only
def har_poor_quality(request):

    # --HARVESTED BAD-- #
    harvested_bad = HarvestedBad.objects.all().order_by('-date')

    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year

        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []

        harvested_bad_by_year[year].append(harvested_bads)

        harvested_bads.total = harvested_bads.calculate_total_harvest()
    
    # if request.method == 'POST':
    #     bad_quality_form = HarvestedBadForm(request.POST)

    #     if bad_quality_form.is_valid():
    #         bad_quality_form.save()
    #         return redirect('harvest_list')
        
    # else:
    #     bad_quality_form = HarvestedBadForm()

    if request.method == 'POST':
        if 'harvested_bad_submit' in request.POST:
            bad_quality_form = HarvestedBadForm(request.POST)
            if bad_quality_form.is_valid():
                bad_quality_form.save()
                return redirect('harvest_list')

        if 'rejected_pine_submit' in request.POST:
            rejected_form = RejectedForm(request.POST)
            if rejected_form.is_valid():
                rejected_form.save()
                return redirect('harvest_list')

    else:
        bad_quality_form = HarvestedBadForm()
        rejected_form = RejectedForm()

    # Sum the totals for each year
    # totals_by_year = {}

    # for year in harvested_bad_by_year.keys():
    #     harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []))

    #     totals_by_year[year] = {
    #         'harvested_bad_total': harvested_bad_total,
    #     }
    harv_all_years = set(harvested_bad_by_year.keys())
    data = {
        'years': list(harv_all_years),
        'harvested_bad_data': [sum(h.total for h in harvested_bad_by_year.get(year, [])) for year in harv_all_years],
    }

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_bad_by_year': harvested_bad_by_year,
      
        'data': data,
        'bad_quality_form': bad_quality_form,
        'rejected_form': rejected_form
    }

    return render(request, 'crop_yield/harvest/harv_poor_quality.html', context)

@login_required(login_url='login')
@admin_only
def hav_rejected(request):
    total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
    # --REJECTED PINE-- #
    rejected_pines = RejectedPine.objects.all().order_by('-date')
    harvested_rejected_by_year = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year
        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []
        harvested_rejected_by_year[year].append(rejected_pine)
        rejected_pine.total = rejected_pine.calculate_total_harvest()

    rejected_pines_by_year = {}
    rejected_pines_by_category = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in rejected_pines_by_year:
            rejected_pines_by_year[year] = []

        # Check if the category is already a key in the category dictionary, if not, add it
        if rejected_pine.category not in rejected_pines_by_category:
            rejected_pines_by_category[rejected_pine.category] = []

        # Append the rejected_pine to the lists for that year and category
        rejected_pines_by_year[year].append(rejected_pine)
        rejected_pines_by_category[rejected_pine.category].append(rejected_pine)

    # Sum the totals for each year
    totals_by_year = {}

    if request.method == 'POST':
        if 'harvested_bad_submit' in request.POST:
            bad_quality_form = HarvestedBadForm(request.POST)
            if bad_quality_form.is_valid():
                bad_quality_form.save()
                return redirect('harvest_list')

        if 'rejected_pine_submit' in request.POST:
            rejected_form = RejectedForm(request.POST)
            if rejected_form.is_valid():
                rejected_form.save()
                return redirect('hav_rejected')

    else:
        bad_quality_form = HarvestedBadForm()
        rejected_form = RejectedForm()

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_rejected_by_year.keys():
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'harvested_rejected_total': harvested_rejected_total,
        }

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'harvested_rejected_by_year': harvested_rejected_by_year,
        'rejected_pines_by_year': rejected_pines_by_year,
        'rejected_pines_by_category': rejected_pines_by_category,
        'totals_by_year': totals_by_year,
        'total_harvest': total_harvest,
        'bad_quality_form': bad_quality_form,
        'rejected_form': rejected_form
    }
    return render(request, 'crop_yield/harvest/harv_rejected.html', context)


# expenses--------------------------
@login_required(login_url='login')
@admin_only
def expe_planting(request):
    # --crop expense --
    crops = Crop.objects.all().order_by('-plant_date')
    crops_by_year = {}
    crops_by_category = {}

    for crop in crops:
        year = crop.plant_date.year
        if year not in crops_by_year:
            crops_by_year[year] = []
        if crop.category not in crops_by_category:
            crops_by_category[crop.category] = []
        crops_by_year[year].append(crop)
        crops_by_category[crop.category].append(crop)

    for year, crops_list in crops_by_year.items():
        for crop in crops_list:
            crop.total = crop.calculate_total()
    # Initialize a dictionary to store the total for each category
    category_totals = {}
    # Loop through the categories in crops_by_category
    for category, crops_list in crops_by_category.items():
        category_total = 0  # Initialize the total for the current category
        # Calculate the total for each crop in the current category
        for crop in crops_list:
            crop_total = crop.calculate_total()  # Calculate the total for the current crop
            if crop_total is not None:
                category_total += crop_total  # Add the crop total to the category total
        category_totals[category] = category_total  # Store the category total in the dictionary

    # Calculate the grand total by summing up all category totals
    grand_total = sum(category_totals.values())
    crop_yearly_totals = Crop.objects.annotate(
    year=ExtractYear('plant_date')
    ).values('year').annotate(
        total=Sum(F('number_planted') * F('price_per_plant'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('-year')

# -------------------------------------------------------------------------------------------------------------------------------------
# --WORK EXPENSE
    worker_expenses = WorkersExpense.objects.all().order_by('-date')
# Create a dictionary to store worker expenses by year
    worker_expenses_by_year = {}
    grand_total_worker_expenses_by_year = {}  # Initialize a dictionary for grand totals by year

    for expense in worker_expenses:
        year = expense.date.year
        if year not in worker_expenses_by_year:
            worker_expenses_by_year[year] = []
        # Calculate the total for each expense
        expense.total = expense.calculate_total()
        worker_expenses_by_year[year].append(expense)

    for year, year_expenses in worker_expenses_by_year.items():
        # Calculate the grand total for each year
        grand_total_worker_expenses_by_year[year] = sum(expense.calculate_total() for expense in year_expenses if expense.total is not None)
    # Calculate the overall grand total for all years
    grand_total_worker_expenses = sum(grand_total_worker_expenses_by_year.values())
    # total by year
    work_yearly_totals = WorkersExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price_pay') * F('workers') * F('days'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in work_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        work_form = WorkerForm(request.POST)

        if work_form.is_valid():
            work_form.save()
            return redirect('crop_expense')
        
    else:
        work_form = WorkerForm()

# ------------------------------------------------------------------------------------------------------------------------------
#  --APPLY FER AND PES
    fer_pes_expenses = ApplyFerPes.objects.all().order_by('-date')
    # Create a dictionary to store fer_pes_expenses by year
    fer_pes_expenses_by_year = {}

    for fer_expense in fer_pes_expenses:
        year = fer_expense.date.year
        if year not in fer_pes_expenses_by_year:
            fer_pes_expenses_by_year[year] = []
        # Calculate the total for each expense
        fer_expense.total = fer_expense.calculate_total()
        fer_pes_expenses_by_year[year].append(fer_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in fer_pes_expenses_by_year.values() for expense in year_expenses)
    # Group the data by year and calculate the sum of total expenses for each year
    yearly_totals = ApplyFerPes.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('quantity_used'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')
    for entry in yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        ferpes_form = ApplyFerPesForm(request.POST)

        if ferpes_form.is_valid():
            ferpes_form.save()
            return redirect('crop_expense')
        
    else:
        ferpes_form = ApplyFerPesForm()
# ---------------------------------------------------------------------------------
    # start_expenses = StartExpense.objects.all()

    # start_expenses_by_year = {}

    # for start_expense in start_expenses:
    #     year = start_expense.date.year

    #     if year not in start_expenses_by_year:
    #         start_expenses_by_year[year] = []

    #     start_expense.total = start_expense.calculate_total()

    #     start_expenses_by_year[year].append(start_expense)
    # grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in start_expenses_by_year.values() for expense in year_expenses)
    
    # start_yearly_totals = StartExpense.objects.annotate(
    # year=ExtractYear('date')
    # ).values('year').annotate(
    #     total=Sum(F('price') * F('total_number'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    # ).order_by('year')

    # for entry in start_yearly_totals:
    #     year = entry['year']
    #     total_expenses = entry['total']
    #     print(f"Year {year}: Total Expenses = {total_expenses}")

    # if request.method == 'POST':
    #     start_form = StartExpenceForm(request.POST)

    #     if start_form.is_valid():
    #         start_form.save()
    #         return redirect('crop_expense')
        
    # else:
    #     start_form = StartExpenceForm()
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    crop_yearly_totals_list = list(crop_yearly_totals)
    work_yearly_totals_list = list(work_yearly_totals)
    yearly_totals_list = list(yearly_totals)
    # start_yearly_totals_list = list(start_yearly_totals)
    
    # Combine the lists
    total_expense_yearly = crop_yearly_totals_list + work_yearly_totals_list + yearly_totals_list #+ start_yearly_totals_list
    yearly_totals_dict = {}

    for entry in total_expense_yearly:
        year = entry['year']
        total = entry['total']
        if year in yearly_totals_dict:
            yearly_totals_dict[year] += total
        else:
            yearly_totals_dict[year] = total

    # Convert the dictionary back to a list of dictionaries
    total_expense_yearly = [{'year': year, 'total': total} for year, total in yearly_totals_dict.items()]
    overall_total_expenses = 0  # Initialize the overall total expenses

    for entry in total_expense_yearly:
        total_expenses = entry['total']
        overall_total_expenses += total_expenses

    print(f"Overall Total Expenses: {overall_total_expenses}")

    

# ------------------------------------------------------------------------------------------------
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'grand_total': grand_total,  # Add the grand total to the context
        'worker_expenses_by_year': worker_expenses_by_year,
        # 'start_expenses_by_year': start_expenses_by_year,

        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,

        'crop_yearly_totals': crop_yearly_totals,
        'work_yearly_totals': work_yearly_totals,
        'yearly_totals': yearly_totals,
        'total_expense_yearly': total_expense_yearly,
        'work_form': work_form,
        'ferpes_form': ferpes_form,
        # 'start_form': start_form
        
    }

    return render(request, 'rev_expe/expense/expe_planting.html', context)

@login_required(login_url='login')
@admin_only
def expe_labor(request):
    crops = Crop.objects.all().order_by('-plant_date')

    crops_by_year = {}
    crops_by_category = {}

    for crop in crops:
        year = crop.plant_date.year

        if year not in crops_by_year:
            crops_by_year[year] = []

        if crop.category not in crops_by_category:
            crops_by_category[crop.category] = []

        crops_by_year[year].append(crop)
        crops_by_category[crop.category].append(crop)

    for year, crops_list in crops_by_year.items():
        for crop in crops_list:
            crop.total = crop.calculate_total()

    # Initialize a dictionary to store the total for each category
    category_totals = {}

    # Loop through the categories in crops_by_category
    for category, crops_list in crops_by_category.items():
        category_total = 0  # Initialize the total for the current category

        # Calculate the total for each crop in the current category
        for crop in crops_list:
            crop_total = crop.calculate_total()  # Calculate the total for the current crop
            if crop_total is not None:
                category_total += crop_total  # Add the crop total to the category total

        category_totals[category] = category_total  # Store the category total in the dictionary

    # Calculate the grand total by summing up all category totals
    grand_total = sum(category_totals.values())
    
    crop_yearly_totals = Crop.objects.annotate(
    year=ExtractYear('plant_date')
    ).values('year').annotate(
        total=Sum(F('number_planted') * F('price_per_plant'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

# -------------------------------------------------------------------------------------------------------------------------------------
# --WORK EXPENSE
    worker_expenses = WorkersExpense.objects.all().order_by('-date')

# Create a dictionary to store worker expenses by year
    worker_expenses_by_year = {}
    grand_total_worker_expenses_by_year = {}  # Initialize a dictionary for grand totals by year

    for expense in worker_expenses:
        year = expense.date.year

        if year not in worker_expenses_by_year:
            worker_expenses_by_year[year] = []

        # Calculate the total for each expense
        expense.total = expense.calculate_total()

        worker_expenses_by_year[year].append(expense)

    for year, year_expenses in worker_expenses_by_year.items():
        # Calculate the grand total for each year
        grand_total_worker_expenses_by_year[year] = sum(expense.calculate_total() for expense in year_expenses if expense.total is not None)

    # Calculate the overall grand total for all years
    grand_total_worker_expenses = sum(grand_total_worker_expenses_by_year.values())

    # total by year
    work_yearly_totals = WorkersExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price_pay') * F('workers') * F('days'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in work_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        work_form = WorkerForm(request.POST)

        if work_form.is_valid():
            work_form.save()
            return redirect('expe_labor')
        
    else:
        work_form = WorkerForm()

# ------------------------------------------------------------------------------------------------------------------------------
#  --APPLY FER AND PES
    fer_pes_expenses = ApplyFerPes.objects.all().order_by('-date')

    # Create a dictionary to store fer_pes_expenses by year
    fer_pes_expenses_by_year = {}

    for fer_expense in fer_pes_expenses:
        year = fer_expense.date.year

        if year not in fer_pes_expenses_by_year:
            fer_pes_expenses_by_year[year] = []

        # Calculate the total for each expense
        fer_expense.total = fer_expense.calculate_total()

        fer_pes_expenses_by_year[year].append(fer_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in fer_pes_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    yearly_totals = ApplyFerPes.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('quantity_used'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        ferpes_form = ApplyFerPesForm(request.POST)

        if ferpes_form.is_valid():
            ferpes_form.save()
            return redirect('crop_expense')
        
    else:
        ferpes_form = ApplyFerPesForm()
    
    # Start expense
    start_expenses = StartExpense.objects.all()

    # Create a dictionary to store start_expenses by year
    start_expenses_by_year = {}

    for start_expense in start_expenses:
        year = start_expense.date.year

        if year not in start_expenses_by_year:
            start_expenses_by_year[year] = []

        # Calculate the total for each expense
        start_expense.total = start_expense.calculate_total()

        start_expenses_by_year[year].append(start_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in start_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    start_yearly_totals = StartExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('total_number'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in start_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        start_form = StartExpenceForm(request.POST)

        if start_form.is_valid():
            start_form.save()
            return redirect('expe_labor')
        
    else:
        start_form = StartExpenceForm()
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    crop_yearly_totals_list = list(crop_yearly_totals)
    work_yearly_totals_list = list(work_yearly_totals)
    yearly_totals_list = list(yearly_totals)
    start_yearly_totals_list = list(start_yearly_totals)
    
    # Combine the lists
    total_expense_yearly = crop_yearly_totals_list + work_yearly_totals_list + yearly_totals_list + start_yearly_totals_list
    
    yearly_totals_dict = {}

    for entry in total_expense_yearly:
        year = entry['year']
        total = entry['total']
        
        if year in yearly_totals_dict:
            yearly_totals_dict[year] += total
        else:
            yearly_totals_dict[year] = total

    # Convert the dictionary back to a list of dictionaries
    total_expense_yearly = [{'year': year, 'total': total} for year, total in yearly_totals_dict.items()]

    overall_total_expenses = 0  # Initialize the overall total expenses

    for entry in total_expense_yearly:
        total_expenses = entry['total']
        overall_total_expenses += total_expenses

    print(f"Overall Total Expenses: {overall_total_expenses}")

    

# ------------------------------------------------------------------------------------------------
 # -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'grand_total': grand_total,  # Add the grand total to the context
        'worker_expenses_by_year': worker_expenses_by_year,
        'start_expenses_by_year': start_expenses_by_year,

        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,

        'crop_yearly_totals': crop_yearly_totals,
        'work_yearly_totals': work_yearly_totals,
        'yearly_totals': yearly_totals,
        'total_expense_yearly': total_expense_yearly,
        'work_form': work_form,
        'ferpes_form': ferpes_form,
        'start_form': start_form
        
    }

    return render(request, 'rev_expe/expense/expe_labor.html', context)

@login_required(login_url='login')
@admin_only
def expe_fer_pes (request):
    crops = Crop.objects.all().order_by('-plant_date')

    crops_by_year = {}
    crops_by_category = {}

    for crop in crops:
        year = crop.plant_date.year

        if year not in crops_by_year:
            crops_by_year[year] = []

        if crop.category not in crops_by_category:
            crops_by_category[crop.category] = []

        crops_by_year[year].append(crop)
        crops_by_category[crop.category].append(crop)

    for year, crops_list in crops_by_year.items():
        for crop in crops_list:
            crop.total = crop.calculate_total()

    # Initialize a dictionary to store the total for each category
    category_totals = {}

    # Loop through the categories in crops_by_category
    for category, crops_list in crops_by_category.items():
        category_total = 0  # Initialize the total for the current category

        # Calculate the total for each crop in the current category
        for crop in crops_list:
            crop_total = crop.calculate_total()  # Calculate the total for the current crop
            if crop_total is not None:
                category_total += crop_total  # Add the crop total to the category total

        category_totals[category] = category_total  # Store the category total in the dictionary

    # Calculate the grand total by summing up all category totals
    grand_total = sum(category_totals.values())
    
    crop_yearly_totals = Crop.objects.annotate(
    year=ExtractYear('plant_date')
    ).values('year').annotate(
        total=Sum(F('number_planted') * F('price_per_plant'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

# -------------------------------------------------------------------------------------------------------------------------------------
# --WORK EXPENSE
    worker_expenses = WorkersExpense.objects.all().order_by('-date')

# Create a dictionary to store worker expenses by year
    worker_expenses_by_year = {}
    grand_total_worker_expenses_by_year = {}  # Initialize a dictionary for grand totals by year

    for expense in worker_expenses:
        year = expense.date.year

        if year not in worker_expenses_by_year:
            worker_expenses_by_year[year] = []

        # Calculate the total for each expense
        expense.total = expense.calculate_total()

        worker_expenses_by_year[year].append(expense)

    for year, year_expenses in worker_expenses_by_year.items():
        # Calculate the grand total for each year
        grand_total_worker_expenses_by_year[year] = sum(expense.calculate_total() for expense in year_expenses if expense.total is not None)

    # Calculate the overall grand total for all years
    grand_total_worker_expenses = sum(grand_total_worker_expenses_by_year.values())

    # total by year
    work_yearly_totals = WorkersExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price_pay') * F('workers') * F('days'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in work_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        work_form = WorkerForm(request.POST)

        if work_form.is_valid():
            work_form.save()
            return redirect('crop_expense')
        
    else:
        work_form = WorkerForm()

# ------------------------------------------------------------------------------------------------------------------------------
#  --APPLY FER AND PES
    fer_pes_expenses = ApplyFerPes.objects.all().order_by('-date')

    # Create a dictionary to store fer_pes_expenses by year
    fer_pes_expenses_by_year = {}

    for fer_expense in fer_pes_expenses:
        year = fer_expense.date.year

        if year not in fer_pes_expenses_by_year:
            fer_pes_expenses_by_year[year] = []

        # Calculate the total for each expense
        fer_expense.total = fer_expense.calculate_total()

        fer_pes_expenses_by_year[year].append(fer_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in fer_pes_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    yearly_totals = ApplyFerPes.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('quantity_used'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        ferpes_form = ApplyFerPesForm(request.POST)

        if ferpes_form.is_valid():
            ferpes_form.save()
            return redirect('expe_fer_pes')
        
    else:
        ferpes_form = ApplyFerPesForm()
# -----------------------------------------------------------------------------------------------------------------------------------------------------
    # start_expense = StartExpense.objects.aggregate(start_expense=models.Sum('total_buy_pine'))['total_harvest']
    # total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
    
    # Start expense
    start_expenses = StartExpense.objects.all()

    # Create a dictionary to store start_expenses by year
    start_expenses_by_year = {}

    for start_expense in start_expenses:
        year = start_expense.date.year

        if year not in start_expenses_by_year:
            start_expenses_by_year[year] = []

        # Calculate the total for each expense
        start_expense.total = start_expense.calculate_total()

        start_expenses_by_year[year].append(start_expense)
    grand_total_ferpes_expenses = sum(expense.calculate_total() for year_expenses in start_expenses_by_year.values() for expense in year_expenses)
    
    # Group the data by year and calculate the sum of total expenses for each year
    start_yearly_totals = StartExpense.objects.annotate(
    year=ExtractYear('date')
    ).values('year').annotate(
        total=Sum(F('price') * F('total_number'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')

    for entry in start_yearly_totals:
        year = entry['year']
        total_expenses = entry['total']
        print(f"Year {year}: Total Expenses = {total_expenses}")

    if request.method == 'POST':
        start_form = StartExpenceForm(request.POST)

        if start_form.is_valid():
            start_form.save()
            return redirect('crop_expense')
        
    else:
        start_form = StartExpenceForm()
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    crop_yearly_totals_list = list(crop_yearly_totals)
    work_yearly_totals_list = list(work_yearly_totals)
    yearly_totals_list = list(yearly_totals)
    start_yearly_totals_list = list(start_yearly_totals)
    
    # Combine the lists
    total_expense_yearly = crop_yearly_totals_list + work_yearly_totals_list + yearly_totals_list + start_yearly_totals_list
    
    yearly_totals_dict = {}

    for entry in total_expense_yearly:
        year = entry['year']
        total = entry['total']
        
        if year in yearly_totals_dict:
            yearly_totals_dict[year] += total
        else:
            yearly_totals_dict[year] = total

    # Convert the dictionary back to a list of dictionaries
    total_expense_yearly = [{'year': year, 'total': total} for year, total in yearly_totals_dict.items()]

    overall_total_expenses = 0  # Initialize the overall total expenses

    for entry in total_expense_yearly:
        total_expenses = entry['total']
        overall_total_expenses += total_expenses

    print(f"Overall Total Expenses: {overall_total_expenses}")

    

# ------------------------------------------------------------------------------------------------
# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'grand_total': grand_total,  # Add the grand total to the context
        'worker_expenses_by_year': worker_expenses_by_year,
        'start_expenses_by_year': start_expenses_by_year,

        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,

        'crop_yearly_totals': crop_yearly_totals,
        'work_yearly_totals': work_yearly_totals,
        'yearly_totals': yearly_totals,
        'total_expense_yearly': total_expense_yearly,
        'work_form': work_form,
        'ferpes_form': ferpes_form,
        'start_form': start_form
        
    }

    return render(request, 'rev_expe/expense/expe_fer_pes.html', context)


@login_required(login_url='login')
@admin_only
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            
            # Set start date
            event.start_date = timezone.now()

            # Set end date, modify this part based on your logic
            # For example, setting it to the start date + 7 days
            event.end_date = event.start_date + timezone.timedelta()
            
            event.status = 'start'  # Set the status to 'start'
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'create_event.html', {'form': form})

@login_required(login_url='login')
@admin_only
def event_list(request):
    events = Event.objects.all()
    return render(request, 'event_list.html', {'events': events})

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

def set_end_date(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        event.end_date = timezone.now()
        event.status = 'completed'  # Set the status to 'completed'
        event.save()
        return redirect('event_list')

    return render(request, 'event_list.html', {'events': [event]})
