from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from stats.models import DataItem, Statistic
from django.http import JsonResponse
from django.db.models import Sum

def main(request):
    qs = Statistic.objects.all()
    if request.method == 'POST':
        new_stat = request.POST.get('new-statistic')
        obj, _ =Statistic.objects.get_or_create(name=new_stat)
        return redirect("dashboard", obj.slug)
    return render(request, 'data_stats.html', {'qs': qs})

def dashboard(request, slug):
    obj = get_object_or_404(Statistic, slug=slug)
    
    return render(request, 'data.html', {
        'name': obj.name,
        'slug': obj.slug,
        'data': obj.data,
        'user': request.user.username
    })

def chart_data(request, slug):
    obj = get_object_or_404(Statistic, slug=slug)
    qs = obj.data.values('owner').annotate(value_sum=Sum('value'))
    
    chart_data = [x.get("value_sum", 0) for x in qs]
    chart_labels = [x["owner"] for x in qs]
    
    return JsonResponse({
        "chartData": chart_data,
        "chartLabels": chart_labels
    })