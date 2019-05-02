from django.contrib import admin

from communication.models import Chat, Message, CallEntity, ChatEntity


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

@admin.register(CallEntity)
class CallEntityAdmin(admin.ModelAdmin):
    pass

@admin.register(ChatEntity)
class ChatEntityAdmin(admin.ModelAdmin):
    exclude = ['hours']