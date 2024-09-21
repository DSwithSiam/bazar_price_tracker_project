from django.shortcuts import render
import requests

def home(request):
   
    response = requests.get('https://api.example.com/bazar-prices') 
    data = response.json()

    return render(request, 'home.html', {'prices': data['prices']})
