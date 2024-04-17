from django.shortcuts import render
from django.http import HttpResponse
from .models import yayinlar_collections
from .utils import get_search_keyword
from .webScrapping import arama_yap, bilgileri_cikar  
import requests  
import os
import uuid


   
def list_yayinlar(request):
    yayinlar = yayinlar_collections.find()
    data = {'yayinlar': yayinlar}
    return render(request, 'yayinlar_listesi.html', data)

def search_and_scrape(request):
    if request.method == 'GET':
        anahtar_kelime = get_search_keyword(request)
        print(anahtar_kelime)
        if anahtar_kelime:
            html = arama_yap(anahtar_kelime)
            if html:
                bilgileri_cikar(html)
    return render(request, 'yayinlar_listesi.html')

def search_and_fetch(request):
    yayinlar = yayinlar_collections.find()  
    data = {'yayinlar': yayinlar}
    return render(request, 'yayinlar_listesi.html', data)

def search_view(request):
    keyword = get_search_keyword(request)
    print("Aranan Kelime:", keyword)
    return render(request, 'yayinlar_listesi.html') 

def download_pdf(request, pdf_url):
    try:
        print(pdf_url)
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_content = response.content
            response = HttpResponse(pdf_content, content_type='application/pdf')
            
            unique_filename = str(uuid.uuid4()) + ".pdf"
            file_path = os.path.join(os.path.dirname(__file__), unique_filename)
            
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(unique_filename)
            
            return response
        else:
            return HttpResponse("Failed to download PDF", status=response.status_code)
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

def filter_yayinlar(request):
    yayin_ad = request.GET.get('yayin_ad')
    yayin_turu = request.GET.get('yayin_turu')

    filtered_yayinlar = yayinlar_collections.find() 

    if yayin_ad:
        filtered_yayinlar = yayinlar_collections.find({"yayinad": {"$regex": f".*{yayin_ad}.*", "$options": "i"}})

    if yayin_turu:
        filtered_yayinlar = yayinlar_collections.find({"yayinturu": yayin_turu})


    context = {
        'yayinlar': filtered_yayinlar
    }
    return render(request, 'yayinlar_listesi.html', context)


def list_yayinlar(request):
    sort_by = request.GET.get('sort-by', 'date-desc') 

    if sort_by == 'date-desc':
        yayinlar = yayinlar_collections.find().sort('yayintarihi', -1) 
    elif sort_by == 'date-asc':
        yayinlar = yayinlar_collections.find().sort('yayintarihi', 1)  
    elif sort_by == 'citation-desc':
        yayinlar = yayinlar_collections.find().sort('alinti_sayisi', -1)  
    elif sort_by == 'citation-asc':
        yayinlar = yayinlar_collections.find().sort('alinti_sayisi', 1)  

    data = {'yayinlar': yayinlar}
    return render(request, 'yayinlar_listesi.html', data)
