from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def contact(request):
    return render(request, 'core/contact.html')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def select_location(request):
    if request.method == 'POST':
        location = request.POST.get('location')

        if request.user.is_authenticated:
            request.user.profile.location = location
            request.user.profile.save()
        else:
            request.session['location'] = location

        return redirect('core:home')

    return render(request, 'core/select_location.html')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import json
from django.http import JsonResponse

def save_location(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        profile = request.user.profile
        profile.city = data['city']
        profile.state = data['state']
        profile.pincode = data['pincode']
        profile.save()
    else:
        request.session['city'] = data['city']
        request.session['state'] = data['state']
        request.session['pincode'] = data['pincode']

    return JsonResponse({'status': 'ok'})
from django.shortcuts import render
from django.contrib.auth.models import User
from products.models import Category
from accounts.utils import seller_rank_score

from .models import Industry

from .models import Industry

def home(request):
    industries = Industry.objects.filter(is_active=True)

    popular_cities = [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Ahmedabad",
    ]

    return render(request, 'core/home.html', {
        'industries': industries,
        'popular_cities': popular_cities,
    })
