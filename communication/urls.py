from django.urls import path

from communication.views import chat_retrieve, message_list, message_create_update, message_create_update, \
    message_delete, message_search, chat_create, call_request, call_end

urlpatterns = [
    path('chat/create/', chat_create, name='chat-create'),
    path('chat/<int:pk>/', chat_retrieve, name='chat-retrieve'),
    path('chat/<int:chat_id>/message-list/', message_list, name='message-list'),
    path('chat/<int:chat_id>/message/search/<str:text>/', message_search, name='chat-message-search'),

    path('message/create/', message_create_update, name='message-create'),
    path('message/update/<int:pk>/', message_create_update, name='message-update'),
    path('message/delete/<int:p>/', message_delete, name='message-delete'),
    path('message/search/<str:text>/', message_search, name='message-search'),

    path('call/request/<int:with_id>/', call_request, name='call-request'),
    path('call/end/<int:with_id>/<str:room_name>/', call_end, name='call-end'),
]
