import requests
from django.shortcuts import render

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

def profile_view(request):
    
    return render(request, 'profile.html',)