from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.http import JsonResponse
from django.utils import timezone
from .forms import *
from django.contrib.auth.decorators import login_required
from user.decorators import *
# Create your views here.


def event(request, event_id):
    notification = get_object_or_404(BroadcastNotification, id=event_id)
    event = get_object_or_404(BroadcastNotification, id=event_id)
    events = FarmEvent.objects.all()
    event_list = BroadcastNotification.objects.all()
    notification_with_details = get_object_or_404(BroadcastNotification, id=event_id)
    broadcast_notifications = BroadcastNotification.objects.prefetch_related('details').all()

    context = {
        'notification': notification, 
        'events': events, 
        'event_list': event_list,
        'event':event,
        'broadcast_notifications': broadcast_notifications,
        'notification_with_details': notification_with_details
    }
    
    return render(request, 'crop_yield/tracking/event.html', context)

def emp_event(request, event_id):
    notification = get_object_or_404(BroadcastNotification, id=event_id)
    event = get_object_or_404(BroadcastNotification, id=event_id)
    events = FarmEvent.objects.all()
    event_list = BroadcastNotification.objects.all()
    notification_with_details = get_object_or_404(BroadcastNotification, id=event_id)
    broadcast_notifications = BroadcastNotification.objects.prefetch_related('details').all()

    context = {
        'notification': notification, 'events': events, 
        'event_list': event_list,
        'event':event,
        'broadcast_notifications': broadcast_notifications,
        'notification_with_details': notification_with_details
    }
    
    return render(request, 'core/employee/emp_events.html', context)

def edit_emp_event(request, event_id):
    notification = get_object_or_404(BroadcastNotification, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            return redirect('emp_event', event_id=event_id)
    else:
        form = EventForm(instance=notification)

    context = {
        'form': form, 
        'notification': notification
    }

    return render(request, 'core/employee/edit_emp_event.html', context)


@login_required(login_url='login')
@admin_only    
def farm_event(request):
    event = BroadcastNotification.objects.all()
    events = FarmEvent.objects.all()

    if request.method == 'POST':
        event_form = EventForm(request.POST)
        
        if event_form.is_valid():
            event_form.save()
            return redirect('farm_event')
        
    else:
        event_form = EventForm()

    farm_events = FarmEvent.objects.all()

    # Get all BroadcastNotifications
    broadcast_notifications = BroadcastNotification.objects.prefetch_related('details').all()

    context = {
        'event': event,
        'events': events,
        'event_form': event_form,
        'farm_events': farm_events,
        'broadcast_notifications': broadcast_notifications,
    }

    return render(request, 'crop_yield/tracking/farm_event.html', context)

from itertools import groupby

@login_required(login_url='login')
@admin_only
def farm_event_list(request):
    event = BroadcastNotification.objects.all()
    grouped_events = {}
    for key, group in groupby(event, key=lambda x: x.variety):
        grouped_events[key] = list(group)
    context ={
        'event': event,
        'grouped_events': grouped_events
    }
    return render(request, 'crop_yield/tracking/event_list.html', context)

def farm_event_list_completed(request):
    event = BroadcastNotification.objects.all()
    context ={
        'event': event
    }
    return render(request, 'crop_yield/tracking/event_list_completed.html', context)

def update_farm_event(request, pk):
    event = BroadcastNotification.objects.get(id=pk) 
    if request.method == 'POST':
        update_farm_form = RescheduleForm(request.POST, instance=event)
        if update_farm_form.is_valid():
            update_farm_form.save()
            return redirect('farm_event_list')
    else:
        update_farm_form = RescheduleForm(instance=event)

    context = {
        'update_farm_form': update_farm_form
    }
    return render (request, 'crop_yield/tracking/update_farm_event.html',context)

    
@login_required(login_url='login')
@admin_only
def event_detail(request, event_id):
    farm_event = get_object_or_404(FarmEvent, id=event_id)
    # You can pass additional context or retrieve related data here

    return render(request, 'event_detail.html', {'farm_event': farm_event})

# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# def farm_event_update(request, pk):
#     notification = BroadcastNotification.objects.get(pk=pk)
#     event_update = BroadcastNotification.objects.get(id=pk)

#     if request.method == 'POST':
#         update_event_form = EventForm(request.POST, instance=event_update)
#         if update_event_form.is_valid():
#             update_event_form.save()

            # Notify clients using WebSocket when data is updated
            # channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(
            #     "realtime_updates_group",
            #     {
            #         "type": "notification",
            #         "message": f"Data for {notification.name} updated",
            #     }
            # )

    #         return redirect('empl-page')
    # else:
    #     update_event_form = EventForm(instance=event_update)

    # context = {
    #     'update_event_form': update_event_form,
    #     'notification': notification
    # }

    # return render(request, 'crop_yield/tracking/farm_event_update.html', context)


def farm_event_update(request, event_id):
    # Fetch the specific BroadcastNotification or return a 404 if not found
    notification = get_object_or_404(BroadcastNotification, id=event_id)

    if request.method == 'POST':
        form = FarmEventDetailsForm(request.POST)
        if form.is_valid():
            # Save the form with the associated BroadcastNotification
            farm_event_details = form.save(commit=False)
            farm_event_details.broadcast_notification = notification
            farm_event_details.save()
            return redirect('emp_farm_events')
    else:
        form = FarmEventDetailsForm()

    context = {
        'notification': notification,
        'form': form,
    }

    return render(request, 'crop_yield/tracking/farm_event_update.html', context)

def customize_farm_event(request):
    customize_event = FarmEvent.objects.all()

    if request.method == 'POST':
        customize_event_form = CustomizeEventForm(request.POST)
        
        if customize_event_form.is_valid():
            customize_event_form.save()
            return redirect('customize_farm_event')
        
    else:
        customize_event_form = CustomizeEventForm()

    context = {
        'customize_event': customize_event,
        'customize_event_form': customize_event_form
    }
    return render(request, 'crop_yield/tracking/farm_event_customize.html', context)

def customize_farm_event_update(request, pk):
    customize_event = FarmEvent.objects.get(id=pk)

    if request.method == 'POST':
        customize_event_form = CustomizeEventForm(request.POST, instance=customize_event)
        
        if customize_event_form.is_valid():
            customize_event_form.save()
            return redirect('customize_farm_event')
        
    else:
        customize_event_form = CustomizeEventForm(instance=customize_event)

    context = {
        'customize_event': customize_event,
        'customize_event_form': customize_event_form
    }
    return render(request, 'crop_yield/tracking/farm_event_customize_update.html', context)

def customize_farm_event_delete(request, pk):
    try:
        customize_event = FarmEvent.objects.get(id=pk)
    except FarmEvent.DoesNotExist:
        return redirect('customize_farm_event')
    
    if request.method == 'POST':
        customize_event.delete()
        return redirect('customize_farm_event')
    
    context = {
        'customize_event': customize_event
    }
  
    return render(request, 'crop_yield/tracking/farm_event_customize_delete.html', context)

def complete_event(request, event_id):
    event = get_object_or_404(BroadcastNotification, pk=event_id)
    
    if not event.sent:
        event.sent = True
        event.status = 'Completed'
        event.end_on = timezone.now()
        event.save()
        return JsonResponse({'message': 'Event marked as completed'})
    else:
        return JsonResponse({'message': 'Event is already completed'})

from django.utils import timezone as django_timezone

def all_broadcast_notifications(request):
    all_notifications = BroadcastNotification.objects.all()
    out = []
    for notification in all_notifications:
        event_name = notification.name.event if notification.name else ""
        out.append({
            'title': event_name,
            'id': notification.id,
            'start': django_timezone.localtime(notification.broadcast_on).strftime("%Y-%m-%d %H:%M:%S"),
            'end': django_timezone.localtime(notification.end_on).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return JsonResponse(out, safe=False)


def cal_event(request):
    all_events = Events.objects.all()
    context = {
        "events":all_events,
    }
    return render(request,'crop_yield/tracking/calevent.html', context )

def all_events(request):                                                                                                 
    all_events = Events.objects.all()                                                                                    
    out = []                                                                                                             
    for event in all_events:                                                                                             
        out.append({                                                                                                     
            'title': event.name,                                                                                         
            'id': event.id,                                                                                              
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),                                                         
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),                                                             
        })                                                                                                               
                                                                                                                      
    return JsonResponse(out, safe=False) 

def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name=str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)

def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)
 
def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.delete()
    data = {}
    return JsonResponse(data)


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class FarmEventListView(ListView):
    model = FarmEvent
    template_name = 'farmevent_list.html'

    def get_queryset(self):
        # Use select_related to fetch related FarmEventDetails in a single query
        return FarmEvent.objects.select_related('details').all()

class FarmEventCreateView(CreateView):
    model = FarmEvent
    template_name = 'farmevent_form.html'
    fields = ['event']
    success_url = reverse_lazy('farmevent_list')

class FarmEventUpdateView(UpdateView):
    model = FarmEvent
    template_name = 'farmevent_form.html'
    fields = ['event']
    success_url = reverse_lazy('farmevent_list')

class FarmEventDeleteView(DeleteView):
    model = FarmEvent
    template_name = 'farmevent_confirm_delete.html'
    success_url = reverse_lazy('farmevent_list')

class BroadcastNotificationListView(ListView):
    model = BroadcastNotification
    template_name = 'broadcastnotification_list.html'

class BroadcastNotificationDeleteView(DeleteView):
    model = BroadcastNotification
    template_name = 'broadcastnotification_confirm_delete.html'
    success_url = reverse_lazy('broadcastnotification_list')


# --------------------JUST SAMPLE__________________
