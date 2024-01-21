from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from pine.models import *
from django.db.models import *
from chat.models import *
from chat.forms import *
from notification_app.forms import *
from notification_app.models import *
from user.decorators import *
from django.contrib import messages
from user.models import UserProfile
from user.forms import *
from pine.forms import *
from django.db.models import Sum, F
from django.db.models.functions import ExtractYear
from decimal import Decimal
from collections import defaultdict
from django.http import HttpResponseForbidden
from django.views import View

from django.db.models import Count

class CustomCSRFFailureView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseForbidden("CSRF verification failed.")

def error_404(request,exception):
    return render(request, '404.html')

def custom_server_error(request):
    return render(request, '500.html', status=500)

@unauthenticated_user
def main(request):
    return render(request, 'home.html')

@login_required(login_url='login')
@admin_only
def index(request):
    variety = Category.objects.all()
    harvested_good = BiddingProcess.objects.all().order_by('date')

    # Create a dictionary to store total_buy_pine by year
    total_buy_pine_by_year = {}

    for bidding_process in harvested_good:
        year = bidding_process.date.year

        if year not in total_buy_pine_by_year:
            total_buy_pine_by_year[year] = 0

        total_buy_pine_by_year[year] += bidding_process.total_buy_pine

    hawaii = PineValue.objects.all()
    crops = Crop.objects.all()
    stock = Stock.objects.all()
# room chat
    emp_rooms = Room.objects.filter(slug="employee")
    if request.method == 'POST':
        roomform = RoomForm(request.POST)

        if roomform.is_valid():
            roomform.save()
            return redirect('index')
        
    else:
        roomform = RoomForm()
# -----------------------------------Crop Planting_______________________________________--_______
    # crops = Crop.objects.all()
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

    combined_crop = list(hawaii_crop) + list(pormosa_crop)

    # Calculate total planted for each year
    total_planted_by_year = {}
    for crop_data in combined_crop:
        year = crop_data['plant_date'].year
        total_planted_by_year[year] = total_planted_by_year.get(year, 0) + crop_data['total_planted']
        
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

    total_planted = Crop.objects.aggregate(total_planted=Sum('number_planted'))['total_planted']

    yearly_totals = {}  

    for year, crops_list in crops_by_year.items():
        yearly_totals[year] = sum(c.number_planted for c in crops_list)

    first_updated_data = None

    if yearly_totals:
        # Find the first updated data
        first_year, first_total_planted = next(iter(yearly_totals.items()))
        first_updated_data = {'year': first_year, 'total_planted': first_total_planted}
# -----------------------------------revenues HARVEST lIST----------------------------------------
    total_harvest = BiddingProcess.objects.aggregate(total_harvest=models.Sum('total_buy_pine'))['total_harvest']
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


    rejected_pines_by_year = {}
    rejected_pines_by_category = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in rejected_pines_by_year:
            rejected_pines_by_year[year] = []

   
        if rejected_pine.category not in rejected_pines_by_category:
            rejected_pines_by_category[rejected_pine.category] = []

   
        rejected_pines_by_year[year].append(rejected_pine)
        rejected_pines_by_category[rejected_pine.category].append(rejected_pine)

    # Sum the totals for each year
    totals_by_year = {}

    for year in harvested_good_by_year.keys() | harvested_bad_by_year.keys():
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []))
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []))
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []))

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
            'harvested_bad_total': harvested_bad_total,
            'harvested_rejected_total': harvested_rejected_total,
            'grand_total': harvested_good_total + harvested_bad_total + harvested_rejected_total,
        }
# ___________________________________________________________________________________________________________________________
# for crop_expense
    crops = Crop.objects.all().order_by('plant_date')

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


        for crop in crops_list:
            crop_total = crop.calculate_total()  
            if crop_total is not None:
                category_total += crop_total

        category_totals[category] = category_total 

    grand_total = sum(category_totals.values())
    
    crop_yearly_totals = Crop.objects.annotate(
    year=ExtractYear('plant_date')
    ).values('year').annotate(
        total=Sum(F('number_planted') * F('price_per_plant'), output_field=models.DecimalField(max_digits=10, decimal_places=2))
    ).order_by('year')
    # --end crop expense --
# -------------------------------------------------------------------------------------------------------------------------------------
# --WORK EXPENSE
    worker_expenses = WorkersExpense.objects.all().order_by('date')

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
        # print(f"Year {year}: Total Expenses = {total_expenses}")

# ------------------------------------------------------------------------------------------------------------------------------
#  --APPLY FER AND PES
    fer_pes_expenses = ApplyFerPes.objects.all()

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
        # print(f"Year {year}: Total Expenses = {total_expenses}")
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    # Start expense
    start_expenses = StartExpense.objects.all()

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
# ------------------------------------------------------------------------------------------------------------------------------------------------------
    crop_yearly_totals_list = list(crop_yearly_totals)
    work_yearly_totals_list = list(work_yearly_totals)
    yearly_totals_list = list(yearly_totals)
    start_yearly_totals_list = list(start_yearly_totals)

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
# ___________________________________________________________________________________________________________________
#    for sales trends
    overall = {}

    for year, totals in totals_by_year.items():
        total_expense = next((entry['total'] for entry in total_expense_yearly if entry['year'] == year), 0)
        overall[year] = totals['grand_total'] - total_expense

    overall_sum = 0

    # for year, totals in totals_by_year.items():
    #     total_expense = next((entry['total'] for entry in total_expense_yearly if entry['year'] == year), 0)
    #     difference = totals['grand_total'] - total_expense
    #     overall_sum += difference

    roi_values = {}  # Dictionary to store ROI values for each year
    for year, totals in totals_by_year.items():
        total_expense = next((entry['total'] for entry in total_expense_yearly if entry['year'] == year), 0)
        # Calculate ROI for the current year
        roi_values[year] = ((totals['grand_total'] - total_expense) / total_expense * 100) if total_expense != 0 else 0


    leaderboard_data1 = (
        BiddingProcess.objects.values('user__username')
        .annotate(total_buy=Sum('total_buy_pine'))
        .order_by('-total_buy')
    )
    leaderboard_data = BiddingProcess.objects.values('user__username').annotate(total_buy=Sum('total_buy_pine')).order_by('-total_buy')[:3]
    leaderboard_data_harvested_bad = HarvestedBad.objects.values('user__username').annotate(total_buy_harv=Sum('total_number')).order_by('-total_buy_harv')[:3]
    leaderboard_data_rejected = RejectedPine.objects.values('user__username').annotate(total_buy_rej=Sum('total_number')).order_by('-total_buy_rej')[:3]
   


# -----------------------------------Harvested Totals----------------------------------------
    harvested_good_harv = BiddingProcess.objects.all().order_by('-date')
    overall_harvested_good_by_year_harv = {}

    for bidding_process_harv in harvested_good_harv:
        year = bidding_process_harv.date.year
        if year not in overall_harvested_good_by_year_harv:
            overall_harvested_good_by_year_harv[year] = []
        overall_harvested_good_by_year_harv[year].append(bidding_process_harv)
        bidding_process_harv.total = bidding_process_harv.calculate_total_harvest()

    # --HARVESTED BAD-- #
    harvested_bad_harv = HarvestedBad.objects.all().order_by('-date')
    overall_harvested_bad_by_year_harv = {}

    for harvested_bads_harv in harvested_bad_harv:
        year = harvested_bads_harv.date.year
        if year not in overall_harvested_bad_by_year_harv:
            overall_harvested_bad_by_year_harv[year] = []
        overall_harvested_bad_by_year_harv[year].append(harvested_bads_harv)
        harvested_bads_harv.total = harvested_bads_harv.calculate_total_harvest()

    # --REJECTED PINE-- #
    rejected_pines_harv = RejectedPine.objects.all().order_by('-date')
    overall_harvested_rejected_by_year_harv = {}
    
    for rejected_pine_harv in rejected_pines_harv:
        year = rejected_pine_harv.date.year
        if year not in overall_harvested_rejected_by_year_harv:
            overall_harvested_rejected_by_year_harv[year] = []
        overall_harvested_rejected_by_year_harv[year].append(rejected_pine_harv)
        rejected_pine_harv.total = rejected_pine_harv.calculate_total_harvest()

    # Create dictionaries to store rejected_pines by year and by category


    # Sum the totals for each year
    overall_totals_by_year_harv = {}

    for year in overall_harvested_good_by_year_harv.keys() | overall_harvested_bad_by_year_harv.keys():
        overall_harvested_good_total_harv = sum(b.total for b in overall_harvested_good_by_year_harv.get(year, []))
        overall_harvested_bad_total_harv = sum(h.total for h in overall_harvested_bad_by_year_harv.get(year, []))
        overall_harvested_rejected_total_harv = sum(i.total for i in overall_harvested_rejected_by_year_harv.get(year, []))

        overall_totals_by_year_harv[year] = {
            'overall_harvested_good_total_harv': overall_harvested_good_total_harv,
            'overall_harvested_bad_total_harv': overall_harvested_bad_total_harv,
            'overall_harvested_rejected_total_harv': overall_harvested_rejected_total_harv,
            'overall_grand_total': overall_harvested_good_total_harv + overall_harvested_bad_total_harv + overall_harvested_rejected_total_harv,
        }

    hgby = {}
    for bp in BiddingProcess.objects.all().order_by('-date'):
        year = bp.date.year
        if year not in hgby:
            hgby[year] = []
        hgby[year].append(bp)
        bp.total = bp.calculate_total_harvest()

    # Fetch HarvestedBad data
    hbby = {}
    for hb in HarvestedBad.objects.all().order_by('-date'):
        year = hb.date.year
        if year not in hbby:
            hbby[year] = []
        hbby[year].append(hb)
        hb.total = hb.calculate_total_harvest()

    # Fetch RejectedPine data
    hrby = {}
    for rp in RejectedPine.objects.all().order_by('-date'):
        year = rp.date.year
        if year not in hrby:
            hrby[year] = []
        hrby[year].append(rp)
        rp.total = rp.calculate_total_harvest()

    harv_all_years = set(hgby.keys()) | set(hbby.keys()) | set(hrby.keys())

    overall_harvest_by_year = {
        year: sum(
            b.total for b in hgby.get(year, [])
        ) + sum(
            h.total for h in hbby.get(year, [])
        ) + sum(
            i.total for i in hrby.get(year, [])
        ) for year in harv_all_years
    }

# ___________________________________________________________________________________________________________________________
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
        'years': list(harv_all_years),
        'hgd': [sum(b.total for b in hgby.get(year, [])) for year in harv_all_years],
        'hbd': [sum(h.total for h in hbby.get(year, [])) for year in harv_all_years],
        'hrd': [sum(i.total for i in hrby.get(year, [])) for year in harv_all_years],
        'ohby': overall_harvest_by_year,
# -----------------PERSONAL CHAT------------------

        'variety': variety,
        'crops': crops,
        'combined_crop': combined_crop,
        'total_planted_by_year': total_planted_by_year,
        # 'total_expenses': total_expenses,
      
         
         'stock': stock,
         'emp_rooms': emp_rooms, 
         'room_name': "broadcast",
         'roomform': roomform,

      

         'hawaii': hawaii,

         # harvest
        'harvested_good_by_year': harvested_good_by_year,
        'harvested_bad_by_year': harvested_bad_by_year,
        'rejected_pines_by_year': rejected_pines_by_year,
        'rejected_pines_by_category': rejected_pines_by_category,
        'totals_by_year': totals_by_year, 
        'overall_totals_by_year_harv':overall_totals_by_year_harv,
        'total_buy_pine_by_year': total_buy_pine_by_year,
        'total_harvest': total_harvest,

        # crop expense
        'crops_by_year': crops_by_year,
        'crops_by_category': crops_by_category,
        'category_totals': category_totals,
        'grand_total': grand_total,  # Add the grand total to the context
        'worker_expenses_by_year': worker_expenses_by_year,
        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,

        'crop_yearly_totals': crop_yearly_totals,
        'work_yearly_totals': work_yearly_totals,
        'yearly_totals': yearly_totals,
        'total_expense_yearly': total_expense_yearly,
        'overall_total_expenses': overall_total_expenses,

        'overall': overall,
        'overall_sum': overall_sum,
        'roi_values': roi_values,

        # crop planting
        'hawaii_crop': hawaii_crop,
        'pormosa_crop': pormosa_crop,
        'yearly_totals': yearly_totals,
        'first_updated_data': first_updated_data,  

        'leaderboard_data': leaderboard_data,
        'leaderboard_data_harvested_bad': leaderboard_data_harvested_bad,
        'leaderboard_data_rejected': leaderboard_data_rejected,

        'total_expense_yearly_percent': total_expense_yearly_percent
        
    }
    return render(request, 'core/index.html', context)

# users
from stockmgmt.forms import *
import csv
@login_required(login_url='login')
@allowed_users(allowed_roles=['employee'])
def employee(request):
    pine_prices = PinePrice.objects.all()
    c = Crop.objects.exclude() 
    y = Yield.objects.all()
    pine_value = PineValue.objects.all()
    rooms = Room.objects.filter(slug="employee")

    total_planted = Crop.objects.aggregate(total_planted=Sum('number_planted'))['total_planted']
    total_harvest = Yield.objects.aggregate(total_harvest=Sum('number_yield'))['total_harvest']

    # crop form
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

    if request.method == 'POST':
        crop_form = CropForm(request.POST)

        if crop_form.is_valid():
            crop_form.save()
            return redirect('empl-page')
        
    else:
        crop_form = CropForm()
    # end crop form----------------------------------------------------------------------------------------------------------

    # Harvest form
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
    
    if request.method == 'POST':
        bad_quality_form = HarvestedBadForm(request.POST)

        if bad_quality_form.is_valid():
            bad_quality_form.save()
            return redirect('empl-page')
        
    else:
        bad_quality_form = HarvestedBadForm()
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

    if request.method == 'POST':
        rejected_form = RejectedForm(request.POST)

        if rejected_form.is_valid():
            rejected_form.save()
            return redirect('empl-page')
        
    else:
        rejected_form = RejectedForm()

    # end harvested form-------------------------------------------------------------------

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
    # end work pay

    # stock items
    category_filter = request.GET.get('category')
    
    # Retrieve all categories to populate the category filter dropdown
    all_categories = Category.objects.all()
    
    # Retrieve the queryset based on the selected category filter
    queryset = Stock.objects.all()
    if category_filter:
        queryset = queryset.filter(category__name=category_filter)
    
    form_search = StockSearchForm(request.GET or None)
    
    if request.method == 'POST':
        form_search = StockSearchForm(request.POST)
        if form_search.is_valid():
            item_name = form_search.cleaned_data.get('item_name')
            queryset = queryset.filter(item_name__icontains=item_name)
            
            if form_search.cleaned_data.get('export_to_CSV'):
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="List_of_stock.csv"'
                writer = csv.writer(response)
                writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
                for stock in queryset:
                    writer.writerow([stock.category, stock.item_name, stock.quantity])
                return response
    
    form_create = StockCreateForm(request.POST or None)
    
    if form_create.is_valid() and request.method == 'POST':
        form_create.save()
        messages.success(request, 'Successfully Saved')
        return redirect('list_item')
    
    # ---------------------------------------------
    bidders_win = BiddingProcess.objects.all().order_by('-date')

    # Create a dictionary to store bidders_win by year
    bidders_win_by_year = {}

    for bidding_process in bidders_win:
        year = bidding_process.date.year

        # Check if the year is already a key in the dictionary, if not, add it
        if year not in bidders_win_by_year:
            bidders_win_by_year[year] = []

        # Append the bidding process to the list for that year
        bidders_win_by_year[year].append(bidding_process)

        # Calculate the total for each bidding process and add it to the object
        bidding_process.total = bidding_process.calculate_total()

    event = BroadcastNotification.objects.all() 
    
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
               'c': c, 'y': y,
               'pine_prices': pine_prices,
               'total_planted': total_planted,
               'total_harvest': total_harvest,
               'pine_value': pine_value,
               'rooms':rooms,

               'crops_by_year': crops_by_year,
                'crops_by_category': crops_by_category,
                'category_totals': category_totals,
                'worker_expenses_by_year': worker_expenses_by_year,

                'grand_total_worker_expenses': grand_total_worker_expenses,
                'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
                'work_yearly_totals': work_yearly_totals,
                'work_form': work_form,

            #    stock items
                "queryset": queryset,
                "form_search": form_search,
                "form_create": form_create,
                "title": "Add Item",
                "all_categories": all_categories,  
                "selected_category": category_filter, 
# planted
                'crops_by_year': crops_by_year,
                'crops_by_category': crops_by_category,
                'category_totals': category_totals,
# harvested
                'harvested_good_by_year': harvested_good_by_year,
                'harvested_bad_by_year': harvested_bad_by_year,
                'harvested_rejected_by_year': harvested_rejected_by_year,
                'rejected_pines_by_year': rejected_pines_by_year,
                'rejected_pines_by_category': rejected_pines_by_category,
                'totals_by_year': totals_by_year,  # Include the totals in the context
                'total_buy_pine_by_year': total_buy_pine_by_year,
                'total_harvest': total_harvest,
                'bad_quality_form': bad_quality_form,
                'rejected_form': rejected_form,

                'bidders_win_by_year': bidders_win_by_year,

                'event': event,
            }
    return render(request, 'core/employee/employee.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['employee'])
def emp_farm_events(request):

    event = BroadcastNotification.objects.all().order_by('-broadcast_on')[:10]

    context = {'room_name': "broadcast",
        'event': event
    }

    return render (request, 'core/employee/emp_farm_events.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['employee'])
def emp_farm_planting(request):
    crops = Crop.objects.all().order_by('-plant_date')[:10]

    if request.method == 'POST':
        crop_form = CropForm(request.POST)

        if crop_form.is_valid():
            crop_form.save()
            return redirect('emp_farm_planting')

    else:
        crop_form = CropForm()
 
# end crop  

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------  
        'crop_form': crop_form,
        'crops': crops
    }

    return render (request, 'core/employee/emp_farm_planting.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['employee'])
def emp_farm_labor(request):

    worker_expenses = WorkersExpense.objects.all().order_by('-date')[:10]

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
            return redirect('emp_farm_labor')
        
    else:
        work_form = WorkerForm()

     # -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'worker_expenses_by_year': worker_expenses_by_year,

        'grand_total_worker_expenses': grand_total_worker_expenses,
        'grand_total_worker_expenses_by_year': grand_total_worker_expenses_by_year,
        'work_yearly_totals': work_yearly_totals,
        'work_form': work_form,
        'worker_expenses': worker_expenses
        
        
    }

    return render (request, 'core/employee/emp_farm_labor.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['employee'])
def emp_farm_fer_pes(request):

    fer_pes_expenses = ApplyFerPes.objects.all().order_by('-date')[:10]

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

# -----------------PERSONAL CHAT----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT----------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT----------------------
        'fer_pes_expenses_by_year': fer_pes_expenses_by_year,
        'grand_total_ferpes_expenses': grand_total_ferpes_expenses,
        'yearly_totals': yearly_totals,
        'ferpes_form': ferpes_form,
        'fer_pes_expenses': fer_pes_expenses
        
    }
    return render (request, 'core/employee/emp_farm_fer_pes.html', context)



# user apge --------------------------------------------------------------------
@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def buyer(request):
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'rooms': rooms,}

    return render(request, 'core/buyer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def buy_pm(request):
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'rooms': rooms,}

    return render(request, 'core/buyer/buy_pm.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def about(request):
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
    context = {'room_name': "broadcast",'rooms': rooms,}

    return render(request, 'core/buyer/about.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def bidding_rooms(request):
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
    room_low = RoomLowQuality.objects.exclude(slug="employee").order_by('-date_added')
    room_rejected = RoomRejected.objects.exclude(slug="employee").order_by('-date_added')

    context = {'room_name': "broadcast",'rooms': rooms,
               'room_low': room_low,
               'room_rejected': room_rejected,
               }

    return render(request, 'core/buyer/bidding_rooms.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def bidding_rooms_low(request):
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
    room_low = RoomLowQuality.objects.exclude(slug="employee").order_by('-date_added')
    room_rejected = RoomRejected.objects.exclude(slug="employee").order_by('-date_added')

    context = {'room_name': "broadcast",'rooms': rooms,
               'room_low': room_low,
               'room_rejected': room_rejected,
               }

    return render(request, 'core/buyer/bidding_rooms_poor.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['buyer'])
def bidding_rooms_rej(request):
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
    room_low = RoomLowQuality.objects.exclude(slug="employee").order_by('-date_added')
    room_rejected = RoomRejected.objects.exclude(slug="employee").order_by('-date_added')

    context = {'room_name': "broadcast",'rooms': rooms,
               'room_low': room_low,
               'room_rejected': room_rejected,
               }

    return render(request, 'core/buyer/bidding_rooms_rej.html', context)

# -------------------------------------------------------------------------------------

# 'end users'

@login_required(login_url='login')
def user_list(request):
    role_filter = request.GET.get('role', None)  # Get the 'role' query parameter from the URL
    users = User.objects.exclude(groups__name='admin', )
    emp_rooms = Room.objects.filter(slug="employee")

    # Filter users based on the 'role' query parameter
    if role_filter:
        users = users.filter(userprofile__role=role_filter)

    add_user = AddUserForm()

    if request.method == 'POST':
        add_user = AddUserForm(request.POST, request.FILES)
        if add_user.is_valid():
            user = add_user.save()
            username = add_user.cleaned_data.get('username')
            role = add_user.cleaned_data.get('role')
            UserProfile.objects.create(user=user, role=role)
            return redirect('list-user')
        else:
            for error in add_user.errors.values():
                messages.error(request, error)

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = {'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'users': users, 
               'add_user': add_user, 
               'selected_role': role_filter,
               'emp_rooms': emp_rooms,
            }
    return render(request, 'core/list_user.html', context)

from django.http import JsonResponse
def user_delete(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.delete()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False})


from django.contrib.auth import authenticate, login, logout
@unauthenticated_user
def user_login(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('index')
        else:
            if user is None:
                messages.error(request, 'Username does not exist.')
            else:
                messages.error(request, 'Incorrect password.')

    return render(request, 'home.html', {'page': page})

@login_required(login_url='login')
def all_notifications(request):
    all_notifications = BroadcastNotification.objects.all()
    return render(request, 'all_notifications.html', {'notifications': all_notifications})