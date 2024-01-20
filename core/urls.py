from django.urls import path
from .import views
from user import views as user_view 
from pine import views as pine_view 
from chat import views as chat_view
from stats import views as stats_view
from notification_app import views as not_view
from django.contrib.auth import views as auth_views
from user.forms import *
from notification_app.consumers import *


urlpatterns = [
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="user/password_reset.html",form_class=CustomPasswordResetForm), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="user/password_reset_set.html",form_class=CustomSetPasswordForm), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_done.html"), name="password_reset_complete"),
# tracking
    path('event_detail/<int:event_id>/', not_view.event_detail, name='event_detail'),
    path('farm_event_update/<int:event_id>/', not_view.farm_event_update, name="farm_event_update"),
    path('update_farm_event/<int:pk>/', not_view.update_farm_event, name="update_farm_event"),
    
    path('customize_farm_event/', not_view.customize_farm_event, name="customize_farm_event"),
    path('customize_farm_event_update/<int:pk>/', not_view.customize_farm_event_update, name='customize_farm_event_update'),
    path('customize_farm_event_delete/<int:pk>/', not_view.customize_farm_event_delete, name="customize_farm_event_delete"),

    path('farm-activities/running/', not_view.farm_event_list, name="farm_event_list"),
    path('farm-activities/completed/', not_view.farm_event_list_completed, name="farm_event_list_completed"),
    path('farm-activities/calendar/', not_view.farm_event, name="farm_event"),

    path('farm-activity/<int:event_id>/', not_view.event, name='event'),
    path('farm-activity/<int:event_id>/', not_view.event2, name='event2'),
    path('all_broadcast_notifications/', not_view.all_broadcast_notifications, name='all_broadcast_notifications'),
    # path('add_broadcast_notification/', not_view.add_broadcast_notification, name='add_broadcast_notification'), 

    path('cal_event/', not_view.cal_event, name='cal_event'),
    path('all_events/', not_view.all_events, name='all_events'),
    path('add_event/', not_view.add_event, name='add_event'), 
    path('update/', not_view.update, name='update'),
    path('remove/', not_view.remove, name='remove'),
    path('complete_event/<int:event_id>/', not_view.complete_event, name='complete_event'),

    path('farmevents/', not_view.FarmEventListView.as_view(), name='farmevent_list'),
    path('farmevents/create/', not_view.FarmEventCreateView.as_view(), name='farmevent_create'),
    path('farmevents/<int:pk>/update/', not_view.FarmEventUpdateView.as_view(), name='farmevent_update'),
    path('farmevents/<int:pk>/delete/', not_view.FarmEventDeleteView.as_view(), name='farmevent_delete'),

    path('broadcastnotifications/', not_view.BroadcastNotificationListView.as_view(), name='broadcastnotification_list'),
    path('broadcastnotifications/<int:pk>/delete/', not_view.BroadcastNotificationDeleteView.as_view(), name='broadcastnotification_delete'),

    

    path('', views.main, name="home"),
    path('index/', views.index, name="index"),

    path('register/', user_view.user_register, name="register"),
    path('login/', user_view.user_login, name="login"),
    path('logout/', user_view.user_logout, name="logout"),
    path('activate/<uidb64>/<token>', user_view.activate, name="activate"),


    path('user-list/', views.user_list, name="list-user"),
    path('user_delete/<int:pk>/', views.user_delete, name="user_delete"),

    path('employee/', views.employee, name="empl-page"),
    path('farm-activities/', views.emp_farm_events, name="emp_farm_events"),
    path('planting/', views.emp_farm_planting, name="emp_farm_planting"),
    path('works/', views.emp_farm_labor, name="emp_farm_labor"),
    path('fertilizer&pesticide/', views.emp_farm_fer_pes, name="emp_farm_fer_pes"),
    path('emp_event/<int:event_id>/', not_view.emp_event, name="emp_event"),
    path('edit_emp_event/<int:event_id>/', not_view.edit_emp_event, name='edit_emp_event'),

    path('buyer/', views.buyer, name="buy-page"),
    path('messages/', views.buy_pm, name="buy_pm"),
    path('about/', views.about, name="about"),
    path('bidding_rooms/', views.bidding_rooms, name="bidding_rooms"),
    path('bidding_rooms_low/', views.bidding_rooms_low, name="bidding_rooms_low"),
    path('bidding_rooms_rej/', views.bidding_rooms_rej, name="bidding_rooms_rej"),

    path('crop/', pine_view.crop, name="crop"),
    path('pineapple-variety/', pine_view.category, name="category"),

    path('planted-crop/', pine_view.crop_list, name="crop_list"),

    path('crop_expense/', pine_view.crop_expense, name="crop_expense"),
    path('expenses/planting', pine_view.expe_planting, name="expe_planting"),
    path('expenses/labor', pine_view.expe_labor, name="expe_labor"),
    path('expenses/fertilizer&pesticides', pine_view.expe_fer_pes, name="expe_fer_pes"),

    path('work_expense_update/<int:pk>/', pine_view.work_expense_update, name='work_expense_update'),
    path('work_expense_update_emp/<int:pk>/', pine_view.work_expense_update_emp, name='work_expense_update_emp'),
    path('work_expense_delete/<int:pk>/', pine_view.work_expense_delete, name='work_expense_delete'),
    path('fer_expense_update/<int:pk>/', pine_view.fer_expense_update, name='fer_expense_update'),
    path('fer_expense_update_emp/<int:pk>/', pine_view.fer_expense_update_emp, name='fer_expense_update_emp'),
    path('fer_expense_delete/<int:pk>/', pine_view.fer_expense_delete, name='fer_expense_delete'),

    path('harvest_list/', pine_view.harvest_list, name="harvest_list"),
    path('harvested/high-quality/', pine_view.har_high_quality, name="har_high_quality"),
    path('harvested/poor-quality/', pine_view.har_poor_quality, name="har_poor_quality"),
    path('harvested/rejected/', pine_view.hav_rejected, name="hav_rejected"),


    path('harvest_bad_update/<int:pk>/', pine_view.harvest_bad_update, name='harvest_bad_update'),
    path('harvest_bad_delete/<int:pk>/', pine_view.harvest_bad_delete, name="harvest_bad_delete"),
    path('rejected_pines_update/<int:pk>/', pine_view.rejected_pines_update, name='rejected_pines_update'),
    path('rejected_pines_delete/<int:pk>/', pine_view.rejected_pines_delete, name="rejected_pines_delete"),
    path('data-analysis/', pine_view.sales_trends, name="sales_trend"),

    path('harvested-revenues/', pine_view.harvest_revenues, name="harvest_revenues"),
    path('harvested-revenues/good-quality/', pine_view.revenues_goodquality, name="revenues_goodquality"),
    path('harvested-revenues/bad-quality/', pine_view.revenues_badquality, name="revenues_badquality"),
    path('harvested-revenues/rejected/', pine_view.revenues_rejected, name="revenues_rejected"),
    

    path('cat_delete/<int:pk>/', pine_view.cat_delete, name="cat_delete"),
    path('crop_delete/<int:pk>/', pine_view.crop_delete, name="crop_delete"),
    path('crop_update/<int:pk>/', pine_view.crop_update, name='crop_update'),

    path('events/', pine_view.event_list, name='event_list'),
    path('events/create/', pine_view.create_event, name='create_event'),
    path('events/set_end_date/<int:event_id>/', pine_view.set_end_date, name='set_end_date'),

    path('rooms/', chat_view.rooms, name="rooms"),
    path('bidding/high-quality', chat_view.bidding, name="bidding"),
    path('bidding_update/<int:pk>/', chat_view.bidding_update, name='bidding_update'),
    path('bidder-winners-list/high-quality/', chat_view.bidder_win_list, name="bidder_win_list"),
    path('top-bidders/set/A', chat_view.leaderboard, name='leaderboard'),
    path('top-bidders/set/B', chat_view.leaderboard_b, name='leaderboard_b'),
    path('top-bidders/rejected', chat_view.leaderboard_c, name='leaderboard_c'),
    
    path('bidder_win_list_delete/<int:pk>/', chat_view.bidder_win_list_delete, name="bidder_win_list_delete"),
    path('bidding/high-quality/<slug:slug>/', chat_view.room, name="room"),
    path('bidding/high-quality/delete/<int:pk>/', chat_view.room_delete, name='room_delete'),

    path('bidding/low-quality/', chat_view.bidding_low_quality, name="bidding_low_quality"),
    path('bidding/low-quality/<slug:slug>/', chat_view.roomlow, name="roomlow"),
    path('roomlow_delete/<int:pk>/', chat_view.roomlow_delete, name='roomlow_delete'),
    path('bidder-winners-list/low-quality/', chat_view.bidder_win_lis_low, name="bidder_win_lis_low"),

    path('bidding/rejected/', chat_view.bidding_rejected, name="bidding_rejected"),
    path('bidding/rejected/<slug:slug>/', chat_view.roomrejected, name="roomrej"),
    path('roomreject_delete/<int:pk>/', chat_view.roomreject_delete, name='roomreject_delete'),
    path('bidder-winners-list/rejected/', chat_view.bidder_win_lis_rejected, name="bidder_win_lis_rejected"),

    path('chat/', chat_view.pm, name='home'),
    path('messages/<str:username>/', chat_view.chatPage, name='chat'),

    path('notifications/', views.all_notifications, name='all_notifications'),

# ----------------sample it will be deleted after--------------------------

    path('get_crop_chart_data/', get_crop_chart_data, name='get_crop_chart_data'),
    path('get_harvest_chart_data/', get_harvest_chart_data, name='get_harvest_chart_data'),
    path('get_revenue_chart_data/', get_revenue_chart_data, name='get_revenue_chart_data'),
]