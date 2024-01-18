import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"notification_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )

    # Receive message from WebSocket
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json["message"]

    #     # Send message to room group
    #     await self.channel_layer.group_send(
    #         self.room_group_name, {"type": "chat.message", "message": message}
    #     )

    # Receive message from room group
    async def send_notification(self, event):
        message = json.loads(event["message"])

        # message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))

class RealtimeUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("realtime_updates_group", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("realtime_updates_group", self.channel_name)

    async def notification(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))


# consumers.py

from django.http import JsonResponse
from pine.models import *
from django.db.models import Sum

def get_harvest_chart_data(request):
    # Fetch BiddingProcess data
    harvested_good_by_year = {}

    for bidding_process in BiddingProcess.objects.all().order_by('-date'):
        year = bidding_process.date.year
        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []
        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total_harvest()

    # Fetch HarvestedBad data
    harvested_bad_by_year = {}

    for harvested_bad in HarvestedBad.objects.all().order_by('-date'):
        year = harvested_bad.date.year
        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []
        harvested_bad_by_year[year].append(harvested_bad)
        harvested_bad.total = harvested_bad.calculate_total_harvest()

    # Fetch RejectedPine data
    harvested_rejected_by_year = {}

    for rejected_pine in RejectedPine.objects.all().order_by('-date'):
        year = rejected_pine.date.year
        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []
        harvested_rejected_by_year[year].append(rejected_pine)
        rejected_pine.total = rejected_pine.calculate_total_harvest()

    harv_all_years = set(harvested_good_by_year.keys()) | set(harvested_bad_by_year.keys()) | set(harvested_rejected_by_year.keys())
    
    data = {
        'years': list(harv_all_years),
        'harvested_good_data': [sum(b.total for b in harvested_good_by_year.get(year, [])) for year in harv_all_years],
        'harvested_bad_data': [sum(h.total for h in harvested_bad_by_year.get(year, [])) for year in harv_all_years],
        'harvested_rejected_data': [sum(i.total for i in harvested_rejected_by_year.get(year, [])) for year in harv_all_years],
    }

    return JsonResponse(data)

def get_crop_chart_data(request):
    hawaii_crop = (
        Crop.objects.filter(category__name='Hawaii')
        .values('plant_date')
        .annotate(total_planted=Sum('number_planted'))
        .order_by('-plant_date')
    )

    pormosa_crop = (
        Crop.objects.filter(category__name='Pormosa')
        .values('plant_date')
        .annotate(total_planted=Sum('number_planted'))
        .order_by('-plant_date')
    )

    data = {
        'labels': [crop_data['plant_date'].strftime('%Y') for crop_data in hawaii_crop],
        'hawaii_data': [crop_data['total_planted'] for crop_data in hawaii_crop],
        'pormosa_data': [crop_data['total_planted'] for crop_data in pormosa_crop],
    }

    return JsonResponse(data)



def get_revenue_chart_data(request):
    # Fetch BiddingProcess data
    harvested_good_by_year = {}

    for bidding_process in BiddingProcess.objects.all().order_by('-date'):
        year = bidding_process.date.year
        if year not in harvested_good_by_year:
            harvested_good_by_year[year] = []
        harvested_good_by_year[year].append(bidding_process)
        bidding_process.total = bidding_process.calculate_total()

    # Fetch HarvestedBad data
    harvested_bad_by_year = {}

    for harvested_bad in HarvestedBad.objects.all().order_by('-date'):
        year = harvested_bad.date.year
        if year not in harvested_bad_by_year:
            harvested_bad_by_year[year] = []
        harvested_bad_by_year[year].append(harvested_bad)
        harvested_bad.total = harvested_bad.calculate_total()

    # Fetch RejectedPine data
    harvested_rejected_by_year = {}

    for rejected_pine in RejectedPine.objects.all().order_by('-date'):
        year = rejected_pine.date.year
        if year not in harvested_rejected_by_year:
            harvested_rejected_by_year[year] = []
        harvested_rejected_by_year[year].append(rejected_pine)
        rejected_pine.total = rejected_pine.calculate_total()

    # Combine years from all datasets
    all_years = set(harvested_good_by_year.keys()) | set(harvested_bad_by_year.keys()) | set(harvested_rejected_by_year.keys())

    # Initialize totals_by_year
    totals_by_year = {}

    # Calculate totals_by_year
    for year in all_years:
        harvested_good_total = sum(b.total for b in harvested_good_by_year.get(year, []) if b.total is not None)
        harvested_bad_total = sum(h.total for h in harvested_bad_by_year.get(year, []) if h.total is not None)
        harvested_rejected_total = sum(i.total for i in harvested_rejected_by_year.get(year, []) if i.total is not None)

        # Ensure that the totals are integers, setting them to 0 if they are None
        harvested_good_total = harvested_good_total if harvested_good_total is not None else 0
        harvested_bad_total = harvested_bad_total if harvested_bad_total is not None else 0
        harvested_rejected_total = harvested_rejected_total if harvested_rejected_total is not None else 0

        grand_total = harvested_good_total + harvested_bad_total + harvested_rejected_total

        totals_by_year[year] = {
            'harvested_good_total': harvested_good_total,
            'harvested_bad_total': harvested_bad_total,
            'harvested_rejected_total': harvested_rejected_total,
            'grand_total': grand_total,
        }

    # Build the data dictionary
    data = {
        'years': list(all_years),
        'harvested_good_data': [totals_by_year[year]['harvested_good_total'] for year in all_years],
        'harvested_bad_data': [totals_by_year[year]['harvested_bad_total'] for year in all_years],
        'harvested_rejected_data': [totals_by_year[year]['harvested_rejected_total'] for year in all_years],
        'grand_total': [totals_by_year[year]['grand_total'] for year in all_years],  # Include totals_by_year in the data
    }

    return JsonResponse(data)
