from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def list_notifications(request):
    items = request.user.notification_set.order_by('-created_at')
    return render(request, 'notifications/list.html', {'items': items})
