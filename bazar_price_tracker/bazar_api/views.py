import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bazar_api.forms import EditMarketManagerForm


def fetch_products():
    # Fetch data from the API
    prices_response = requests.get('https://bazar-price-tracker-api.onrender.com/api/prices/') 
    prices = prices_response.json() 
    
    items_response = requests.get('https://bazar-price-tracker-api.onrender.com/api/items/') 
    items = items_response.json() 
    
    markets_response = requests.get('https://bazar-price-tracker-api.onrender.com/api/markets/') 
    markets = markets_response.json() 
    
    # Combine the data into products
    products = []
    for price in prices:
        product = {}
        for item in items:
            if item['id'] == price['item']:  
                product['name'] = item['name']
                product['price'] = price['price_per_kg']
        for market in markets:
            if market['id'] == price['market']:  
                product['market'] = market['name']
        
        if not product in products:
            products.append(product)
    
    return products


def home(request):
    # Fetch fresh products data
    products = fetch_products()
    return render(request, 'home.html', {'products': products})


def Search_results(request):
    # Fetch fresh products data
    products = fetch_products()

    # Get search parameters
    market_name = request.GET.get('market_name', '').lower()
    item_name = request.GET.get('item_name', '').lower()
    
    results = []
     
    # Search in the products list
    for product in products:
        product_market_name = product['market'].lower()
        product_item_name = product['name'].lower()

        # Check if the search terms match
        if market_name and not item_name:
            if market_name in product_market_name:
                results.append(product)
        elif item_name and not market_name:
            if item_name in product_item_name:
                results.append(product)
        else:
            if market_name in product_market_name:
                if item_name in product_item_name:
                    results.append(product)
    
    return render(request, 'search_results.html', {'results': results})



# @login_required
def profile_view(request):
    user = request.user  
    user = "1"
    api_url = f'https://bazar-price-tracker-api.onrender.com/api/user/market_managers/{user}/'
    
    # Fetch profile data from API
    response = requests.get(api_url)
    manager_profile = response.json() if response.status_code == 200 else {}
    
    return render(request, 'profile.html', {'manager_profile': manager_profile})



# @login_required
def edit_profile(request):
    user = 1  # assuming the user is authenticated
    api_url = f'https://bazar-price-tracker-api.onrender.com/api/user/market_managers/{user}/'
    
    if request.method == 'POST':
        form = EditMarketManagerForm(request.POST, request.FILES)
        if form.is_valid():
            data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'market_name': form.cleaned_data['market_name'],
                'phone': form.cleaned_data['phone'],
            }
            
            # Handle profile picture if uploaded
            files = {'profile_picture': request.FILES['profile_picture']} if 'profile_picture' in request.FILES else None
            
            # Send PUT request to update profile
            response = requests.put(api_url, data=data, files=files)
            
            if response.status_code == 200:
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'Failed to update profile.')
    
    else:
        # Fetch current profile data to pre-fill the form
        response = requests.get(api_url)
        if response.status_code == 200:
            current_profile = response.json()
            form = EditMarketManagerForm(initial={
                'username': current_profile['username'],
                'email': current_profile['email'],
                'market_name': current_profile['market_name'],
                'phone': current_profile['phone'],
            })
        else:
            form = EditMarketManagerForm()

    return render(request, 'edit_profile.html', {'form': form})