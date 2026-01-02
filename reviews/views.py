from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Review

@login_required
def add_review(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)

    if request.method == 'POST':
        Review.objects.update_or_create(
            seller=seller,
            buyer=request.user,
            defaults={
                'rating': request.POST.get('rating'),
                'comment': request.POST.get('comment', '')
            }
        )
        return redirect('products:dealer_profile', seller.username)

    return render(request, 'reviews/add_review.html', {'seller': seller})
