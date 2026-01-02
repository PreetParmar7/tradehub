# messaging/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from products.models import Product
from .models import Conversation, Message
from leads.models import Lead


@login_required
def start_conversation(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    seller = product.seller
    buyer = request.user

    # Guards
    if buyer == seller:
        return redirect('products:product_detail', product_id)

    if seller.profile.verification_status != 'approved':
        return redirect('products:product_detail', product_id)

    conversation, _ = Conversation.objects.get_or_create(
        buyer=buyer,
        seller=seller,
        product=product
    )

    return redirect('messaging:conversation', conversation.id)


@login_required
def inbox(request):
    user = request.user

    conversations = Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).order_by('-updated_at')

    return render(request, 'messaging/inbox.html', {
        'conversations': conversations
    })


@login_required
def conversation_detail(request, conv_id):
    conversation = get_object_or_404(Conversation, id=conv_id)

    # 🔐 Access control
    if request.user not in [conversation.buyer, conversation.seller]:
        return redirect('messaging:inbox')

    # ✅ Mark unread messages as read
    conversation.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    # 🔥 Update lead status when SELLER opens chat
    if request.user == conversation.seller:
        Lead.objects.filter(
            seller=conversation.seller,
            buyer=conversation.buyer,
            product=conversation.product,
            status='new'
        ).update(
            status='contacted'
        )

    # ✉️ Send message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )

            # 🔥 Seller response logic
            if request.user == conversation.seller:
                Lead.objects.filter(
                    seller=conversation.seller,
                    buyer=conversation.buyer,
                    product=conversation.product
                ).exclude(
                    status__in=['interested', 'not_interested']
                ).update(
                    status='interested',
                    reminder_at=timezone.now()
                )

            conversation.updated_at = timezone.now()
            conversation.save(update_fields=['updated_at'])

        return redirect('messaging:conversation', conversation.id)

    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': conversation.messages.order_by('created_at')
    })
