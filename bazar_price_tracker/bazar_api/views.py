import requests
from django.shortcuts import render

def home(request):

    prices_response = requests.get('https://bazar-price-tracker-api.onrender.com/api/prices/') 
    prices = prices_response.json() 
    
    items_response = requests.get('https://bazar-price-tracker-api.onrender.com/api/items/') 
    items = items_response.json() 
    
    markets_response = requests.get('https://bazar-price-tracker-api.onrender.com/api/markets/') 
    markets = markets_response.json() 
    
    
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
        if product not in products:
            products.append(product)      

    return render(request, 'home.html', {'products' : products})
