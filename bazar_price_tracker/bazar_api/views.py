from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bazar_api.forms import EditMarketManagerForm, LoginForm


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



@login_required
def profile_view(request):
    user = request.user  
    api_url = f'https://bazar-price-tracker-api.onrender.com/api/user/market_managers/{user}/'
    
    # Fetch profile data from API
    response = requests.get(api_url)
    manager_profile = response.json() if response.status_code == 200 else {}
    
    products = []
    
    for product in fetch_products():
        if manager_profile['market_name'] == product['market']:
            products.append(product)
    
    
    return render(request, 'profile.html', {'manager_profile': manager_profile, "products": products})



@login_required
def edit_profile(request):
    user = request.user  
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




ITEM_API_URL = "https://bazar-price-tracker-api.onrender.com/api/items/"
PRODUCT_API_URL = "https://bazar-price-tracker-api.onrender.com/api/prices/"


def get_or_create_item_from_api(item_name):
    
    response = requests.get(ITEM_API_URL, params={"name": item_name})
    
    items = response.json()
    for item in items:
        if item['name'] == item_name:
            return item['id']
    
    # If item does not exist, create a new one via POST request
    create_response = requests.post(ITEM_API_URL, json={"name": item_name})
    if create_response.status_code == 201:
        new_item = create_response.json()
        return new_item['id']
    else:
        raise Exception(f"Error creating item: {create_response.text}")


# View for adding a product
def add_product_to_api_view(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        price_per_kg = request.POST.get('price')
        market_id = 7
        try:
            item_id = get_or_create_item_from_api(item_name)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        product_data = {
            "price_per_kg": price_per_kg,
            "market": market_id,
            "item": item_id
        }
        
        response = requests.post(PRODUCT_API_URL, json=product_data)
        if response.status_code == 201:
            return redirect('profile') 
        else:
            return JsonResponse({'error': f"Error adding product: {response.text}"}, status=400)

    return redirect('profile') 



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # API call to the external login API
            api_url = 'https://bazar-price-tracker-api.onrender.com/api/user/login/'
            data = {
                'username': username,
                'password': password
            }

            try:
                response = requests.post(api_url, json=data)

                # Handle the response from the API
                if response.status_code == 200:
                    messages.success(request, 'Login successful!')
                    print("----------------------'Login successful!'---------------", request.user)
                    # You can redirect to a different page here if needed
                    return redirect('home')  # Assuming 'home' is a valid URL pattern
                else:
                    messages.error(request, 'Login failed. Please check your username and password.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        form = LoginForm()

    return render(request, 'user_forms.html', {'form': form})

