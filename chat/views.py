from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from pine.models import *
from pine.forms import *
from django.http import JsonResponse
from django.db.models import *
# Create your views here.
@login_required(login_url='login')
def rooms(request):
    rooms = Room.objects.filter(slug="supplier")

    return render(request, 'chat/rooms.html', {'rooms':rooms})
@login_required(login_url='login')
def room(request,slug):
    # rooms = Room.objects.all()
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)[0:25]

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'room': room,
        'messages': messages
    }
    return render(request, 'chat/room.html', context)

def room_delete(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return redirect('bidding')
    
    if request.method == 'POST':
        room.delete()
        return redirect('bidding')
  
    return render(request, 'chat/room_delete.html', {'room': room})

@login_required(login_url='login')
def bidding(request):
    # link = "http://127.0.0.1:8000/bidding/high-quality/1/"
    rooms = Room.objects.exclude(slug="employee").order_by('-date_added')
    emp_rooms = Room.objects.filter(slug="employee")
    bidding_processes = BiddingProcess.objects.all()
    if request.method == 'POST':
        roomform = RoomForm(request.POST)

        if roomform.is_valid():
            roomform.save()
            return redirect('bidding')
        
    else:
        roomform = RoomForm()

    if request.method == 'POST':
        biddingForm = BiddingForm(request.POST)

        if biddingForm.is_valid():
            biddingForm.save()
            return redirect('bidder_win_list')
        
    else:
        biddingForm = BiddingForm()

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'rooms':rooms, 'roomform': roomform,
        'bidding_processes': bidding_processes,
        'biddingForm': biddingForm,
        'emp_rooms': emp_rooms,
        # 'link': link
    }
    return render(request, 'chat/bidding.html', context)

@login_required(login_url='login')
def bidding_update(request, pk):
    bidding_processes = BiddingProcess.objects.get(id=pk)
    if request.method == 'POST':
        bid_form = BuyPineTotal(request.POST, instance=bidding_processes)
        if bid_form.is_valid():
            bid_form.save()
            return redirect('bidder_win_list')
    else:
        bid_form = BuyPineTotal(instance=bidding_processes)
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'bid_form': bid_form
    }
    return render(request, 'chat/bidding_update.html', context)

@login_required(login_url='login')
def bidder_win_list(request):
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

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'bidders_win_by_year': bidders_win_by_year,
    }

    return render (request, 'chat/bidders_win_list.html', context)

def leaderboard(request):
    leaderboard_data = (
        BiddingProcess.objects.values('user__username')
        .annotate(total_buy=Sum('total_buy_pine'))
        .order_by('-total_buy')
    )
    leaderboard_data_harvested_bad = (
        HarvestedBad.objects.values('user__username')
        .annotate(total_buy_harv=Sum('total_number'))
        .order_by('-total_buy_harv')
    )
    leaderboard_data_rejected = (
        RejectedPine.objects.values('user__username')
        .annotate(total_buy_harvrej=Sum('total_number'))
        .order_by('-total_buy_harvrej')
    )

    context = { 'room_name': "broadcast",
        'leaderboard_data': leaderboard_data,
        'leaderboard_data_harvested_bad': leaderboard_data_harvested_bad,
        'leaderboard_data_rejected': leaderboard_data_rejected,
    }

    return render(request, 'chat/leaderboard.html', context)

def leaderboard_b(request):
    leaderboard_data_harvested_bad = (
        HarvestedBad.objects.values('user__username')
        .annotate(total_buy_harv=Sum('total_number'))
        .order_by('-total_buy_harv')
    )

    context = { 'room_name': "broadcast",
        'leaderboard_data_harvested_bad': leaderboard_data_harvested_bad,
    }

    return render(request, 'chat/leaderboard_b.html', context)

def leaderboard_c(request):
    leaderboard_data_rejected = (
        RejectedPine.objects.values('user__username')
        .annotate(total_buy_harvrej=Sum('total_number'))
        .order_by('-total_buy_harvrej')
    )

    context = { 'room_name': "broadcast",
        'leaderboard_data_rejected': leaderboard_data_rejected,
    }

    return render(request, 'chat/leaderboard_c.html', context)

@login_required(login_url='login')
def bidder_win_list_delete(request, pk):
    try:
        bid_win = BiddingProcess.objects.get(id=pk)
        bid_win.delete()
        return JsonResponse({'success': True})
    except BiddingProcess.DoesNotExist:
        return JsonResponse({'success': False})
    

#------------------------------------------------- Low Quality-----------------------------------------------------------------#
@login_required(login_url='login')
def bidder_win_lis_low(request):
    harvested_bad = HarvestedBad.objects.all().order_by('date')

    harvested_bad_by_year = {}

    for harvested_bads in harvested_bad:
        year = harvested_bads.date.year

        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []

        harvested_bad_by_year[year].append(harvested_bads)

        harvested_bads.total = harvested_bads.calculate_total()

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'harvested_bad_by_year': harvested_bad_by_year,
    }

    return render (request, 'chat/low_quality/bidders_win_list_low.html', context)

@login_required(login_url='login')
def roomlow(request,slug):
    # rooms = Room.objects.all()
    room = RoomLowQuality.objects.get(slug=slug)
    messages = MessageLow.objects.filter(room=room)[0:25]

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'room': room,
        'messages': messages
    }
    return render(request, 'chat/low_quality/room_low.html', context)

def roomlow_delete(request, pk):
    try:
        room = RoomLowQuality.objects.get(id=pk)
    except RoomLowQuality.DoesNotExist:
        return redirect('bidding_low_quality')
    
    if request.method == 'POST':
        room.delete()
        return redirect('bidding_low_quality')
  
    return render(request, 'chat/low_quality/room_low_delete.html', {'room': room})

@login_required(login_url='login')
def bidding_low_quality(request):
    room_low = RoomLowQuality.objects.exclude(slug="employee").order_by('-date_added')
    # emp_rooms = RoomLowQuality.objects.filter(slug="employee")
    # bidding_processes = BiddingProcess.objects.all()
    if request.method == 'POST':
        roomformlow = RoomFormLowQuality(request.POST)

        if roomformlow.is_valid():
            roomformlow.save()
            return redirect('bidding_low_quality')
        
    else:
        roomformlow = RoomFormLowQuality()
    
    if request.method == 'POST':
        bad_quality_form = HarvestedBadForm(request.POST)

        if bad_quality_form.is_valid():
            bad_quality_form.save()
            return redirect('bidder_win_lis_low')
        
    else:
        bad_quality_form = HarvestedBadForm()

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'room_low':room_low, 'roomformlow': roomformlow,
        # 'bidding_processes': bidding_processes,
        'bad_quality_form': bad_quality_form,
        # 'emp_rooms': emp_rooms
    }
    return render(request, 'chat/low_quality/bid_low.html', context)

#------------------------------------------------- rejected-----------------------------------------------------------------#
@login_required(login_url='login')
def bidder_win_lis_rejected(request):
    rejected_pines = RejectedPine.objects.all().order_by('-date')

    harvested_rejected_by_year = {}

    for rejected_pine in rejected_pines:
        year = rejected_pine.date.year

        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []

        harvested_rejected_by_year[year].append(rejected_pine)

        rejected_pine.total = rejected_pine.calculate_total_harvest()
    
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'harvested_rejected_by_year': harvested_rejected_by_year,
    }

    return render (request, 'chat/rejected/bidders_win_list_reject.html', context)

@login_required(login_url='login')
def roomrejected(request,slug):
    # rooms = Room.objects.all()
    room = RoomRejected.objects.get(slug=slug)
    messages = MessageRejected.objects.filter(room=room)[0:25]

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'room': room,
        'messages': messages
    }
    return render(request, 'chat/rejected/room_rejected.html', context)

def roomreject_delete(request, pk):
    try:
        room = RoomRejected.objects.get(id=pk)
    except RoomRejected.DoesNotExist:
        return redirect('bidding_rejected')
    
    if request.method == 'POST':
        room.delete()
        return redirect('bidding_rejected')
  
    return render(request, 'chat/rejected/room_reject_delete.html', {'room': room})

@login_required(login_url='login')
def bidding_rejected(request):
    room_rejected = RoomRejected.objects.exclude(slug="employee").order_by('-date_added')

    if request.method == 'POST':
        roomformrejected = RoomFormRejected(request.POST)

        if roomformrejected.is_valid():
            roomformrejected.save()
            return redirect('bidding_rejected')
        
    else:
        roomformrejected = RoomFormRejected()
    
    if request.method == 'POST':
        rejected_form = RejectedForm(request.POST)

        if rejected_form.is_valid():
            rejected_form.save()
            return redirect('bidder_win_lis_rejected')
        
    else:
        rejected_form = RejectedForm()

# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'room_rejected':room_rejected, 'roomformrejected': roomformrejected,
        'rejected_form': rejected_form,
       
    }
    return render(request, 'chat/rejected/bid_rejected.html', context)

# PERSONAL CHAT
from django.shortcuts import get_object_or_404
@login_required(login_url='login')
def pm(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'index.html', context={'users': users})

@login_required(login_url='login')
def chatPage(request, username):
    user_obj = get_object_or_404(User, username=username)
    users = User.objects.exclude(username=request.user.username)

    if request.user.id > user_obj.id:
        thread_name = f'chat_{request.user.id}-{user_obj.id}'
    else:
        thread_name = f'chat_{user_obj.id}-{request.user.id}'

    message_objs = ChatModel.objects.filter(thread_name=thread_name)

    # Include the 'link' attribute when rendering the template
    messages = [
        {
            'message': message.message,
            'timestamp': message.timestamp,
            'sender': message.sender,
            'link': message.link,
        }
        for message in message_objs
    ]
    
# -----------------PESONAL CHAT-----------------------
    current_user = request.user.username
    chat_messages = ChatModel.objects.exclude(sender=current_user).values('sender').annotate(
        message_count=Count('id'),
        latest_message=Max('message'),
        date=Max('timestamp')
    ).order_by('latest_message')
# -----------------PERSONAL CHAT----------------------
    context = { 'room_name': "broadcast",
# -----------------PERSONAL CHAT---------------------
        'chat_messages': chat_messages,
# -----------------PERSONAL CHAT------------------
        'user': user_obj,
        'users': users,
        'messages': messages,
    }

    return render(request, 'personal_chat.html', context)
