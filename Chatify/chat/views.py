import json

from asgiref.sync import sync_to_async, async_to_sync
from django.http import JsonResponse
from ninja import Router

from .models import Message
from accounts.models import CustomUser
from accounts.views import AuthBearer
from core.api import api

from .schemas import MessageIn

chat_router = Router()


@api.get("/is_authorized", auth=AuthBearer())
def is_authorized(request):
    return {"token": request.auth}


@chat_router.get('/get_user_chats/', auth=AuthBearer())
async def get_user_chats(request):
    username = request.auth['sub']
    user = await sync_to_async(CustomUser.objects.get)(username=username)
    sent_messages = await sync_to_async(list)(Message.objects.filter(sender=user))
    received_messages = await sync_to_async(list)(Message.objects.filter(recipient=user))
    chats = set()
    for message in sent_messages:
        chats.add(await sync_to_async(getattr)(message, 'recipient'))
    for message in received_messages:
        chats.add(await sync_to_async(getattr)(message, 'sender'))
    chat_list = [{'username': chat.username, 'id': chat.id} for chat in chats]
    return JsonResponse(chat_list, safe=False)


@chat_router.post('/send_message/{recipient_id}/', auth=AuthBearer())
async def send_message(request, recipient_id: int, data: MessageIn):
    username = request.auth['sub']
    sender = await sync_to_async(CustomUser.objects.get)(username=username)
    text = data.text
    recipient = await sync_to_async(CustomUser.objects.get)(id=recipient_id)
    message = await sync_to_async(Message.objects.create)(sender=sender, recipient=recipient, text=text)
    return JsonResponse({'status': 'success', 'message_id': message.id})


@chat_router.get('/get_messages/', auth=AuthBearer())
async def get_messages(request):
    username = request.auth['sub']
    user = await sync_to_async(CustomUser.objects.get)(username=username)
    sent_messages = await sync_to_async(list)(Message.objects.filter(sender=user))
    received_messages = await sync_to_async(list)(Message.objects.filter(recipient=user))
    messages = []
    for message in sent_messages:
        sender = await sync_to_async(CustomUser.objects.get)(id=message.sender_id)
        recipient = await sync_to_async(CustomUser.objects.get)(id=message.recipient_id)
        messages.append({'id': message.id, 'text': message.text, 'sender': sender.username, 'recipient': recipient.username, 'timestamp': message.timestamp})
    for message in received_messages:
        sender = await sync_to_async(CustomUser.objects.get)(id=message.sender_id)
        recipient = await sync_to_async(CustomUser.objects.get)(id=message.recipient_id)
        messages.append({'id': message.id, 'text': message.text, 'sender': sender.username, 'recipient': recipient.username, 'timestamp': message.timestamp})
    return JsonResponse(messages, safe=False)


@chat_router.get('/search_users/{query}/', auth=AuthBearer())
async def search_users(request, query: str):
    users = await sync_to_async(list)(CustomUser.objects.filter(username__icontains=query))
    user_list = [{'username': user.username, 'id': user.id} for user in users]
    return JsonResponse(user_list, safe=False)
