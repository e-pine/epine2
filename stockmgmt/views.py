from django.shortcuts import render, redirect
from django.http import HttpResponse
import csv
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required(login_url='login')
def list_item(request):
    header = 'List of Items'
    
    # Retrieve the category filter value from the request GET parameters
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
    
    
    user_item_history = ItemHistory.objects.filter(user=request.user).order_by('-timestamp')
    context = {
        "header": header,
        "queryset": queryset,
        "form_search": form_search,
        "form_create": form_create,
        "title": "Add Item",
        "all_categories": all_categories,  # Add all categories to the context
        "selected_category": category_filter,  # Add selected category to the context
        "user_item_history": user_item_history,
    }
    
    return render(request, "list_item.html", context)


@login_required(login_url='login')
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Successfully Saved')
		return redirect('list_item')


	context = {
		"form": form,
		"title": "Add Item",
	}
	return render(request, "add_items.html", context)

@login_required(login_url='login')
def update_items(request, pk):
    queryset = Stock.objects.get(id=pk)

    if not request.user.is_staff:
        # If the user is not staff, prevent them from editing the form
        form = StockUpdateForm(instance=queryset, user=request.user)
    else:
        form = StockUpdateForm(request.POST or None, instance=queryset, user=request.user)

    if request.method == 'POST':
        if request.user.is_staff:
            # Only allow staff to save changes
            form = StockUpdateForm(request.POST, instance=queryset, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Successfully Saved')
                return redirect('list_item')
        else:
            messages.error(request, 'You do not have permission to edit this form.')

    context = {
        'form': form
    }
    return render(request, 'add_items.html', context)

from django.http import JsonResponse
def delete_items(request, pk):
    try:
        stock = Stock.objects.get(id=pk)
        stock.delete()
        return JsonResponse({'success': True})
    except Stock.DoesNotExist:
        return JsonResponse({'success': False})

@login_required(login_url='login')
def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)

@login_required
def issue_items(request, pk):
    queryset = Stock.objects.get(id=pk)

    if request.method == 'POST':
        form = IssueForm(request.POST, instance=queryset)
        if form.is_valid():
            # Get the current user's username
            issue_by_username = request.user.username
            
            instance = form.save(commit=False)
            instance.issue_by = issue_by_username  # Assign the username to issue_by field
            instance.receive_quantity = 0
            instance.quantity -= instance.issue_quantity
            instance.save()

            messages.success(request, f"Issued SUCCESSFULLY. {instance.quantity} {instance.item_name}s now left in Stocks")

            return redirect('/')

    else:
        form = IssueForm(instance=queryset)

    context = {
        "title": f"Issue {queryset.item_name}",
        "queryset": queryset,
        "form": form,
        "username": f"Issue By: {request.user}",
    }

    return render(request, "add_items.html", context)


@login_required
def receive_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)
    
    if form.is_valid():
        instance = form.save(commit=False)
        instance.issue_quantity = 0
        instance.quantity += instance.receive_quantity
        instance.save()
        messages.success(request, "Add SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now in Stocks")

        # if request.user.userprofile.role == 'admin':
        #     return redirect('list_item') 
        # elif request.user.userprofile.role == 'employee':
        return redirect('/stock')

    context = {
        "title": 'Receive ' + str(queryset.item_name),
        "instance": queryset,
        "form": form,
        "username": 'Receive By: ' + str(request.user),
    }
    return render(request, "add_items.html", context)




@login_required(login_url='login')
def reorder_level(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReorderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))

		return redirect("list_item")
	context = {
			"instance": queryset,
			"form": form,
		}
	return render(request, "add_items.html", context)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='login')
def list_history(request):
    header = 'HISTORY DATA'
    queryset = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)

    if request.method == 'POST':
        category = form['category'].value()
        
        queryset = StockHistory.objects.filter(
            item_name__icontains=form['item_name'].value(),
            last_updated__range=[
                form['start_date'].value(),
                form['end_date'].value()
            ]
        )

        if (category != ''):
            queryset = queryset.filter(category_id=category)

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['CATEGORY',
                 'ITEM NAME',
                 'QUANTITY',
                 'ISSUE QUANTITY',
                 'RECEIVE QUANTITY',
                 'RECEIVE BY',
                 'ISSUE BY',
                 'LAST UPDATED'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                    [stock.category,
                     stock.item_name,
                     stock.quantity,
                     stock.issue_quantity,
                     stock.receive_quantity,
                     stock.receive_by,
                     stock.issue_by,
                     stock.last_updated])
            return response

    # Set the number of items per page
    items_per_page = 10  # Change this to your desired number

    paginator = Paginator(queryset, items_per_page)
    page = request.GET.get('page')

    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
    }

    return render(request, "list_history.html", context)

