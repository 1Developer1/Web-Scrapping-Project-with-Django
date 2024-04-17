import requests
from bs4 import BeautifulSoup
import time
import random
from pymongo import MongoClient

def arama_yap(anahtar_kelime):
    url = f'https://scholar.google.com/scholar?q={anahtar_kelime}&hl=tr'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)
    wait_time = random.uniform(1, 3)  # Rastgele 2 ila 5 saniye bekleme
    time.sleep(wait_time)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Hata {response.status_code} - Sayfa alınamadı.')
        return None

def bilgileri_cikar(html):
    baslik=None
    detay_link=None
    soup = BeautifulSoup(html, 'html.parser')
    yayinlar = soup.find_all('div', class_='gs_r gs_or gs_scl')  
    for i, yayin in enumerate(yayinlar[:10], 1):
        baslik = yayin.find('h3', class_='gs_rt').find('a').text.strip()
        detay_link = yayin.find('h3', class_='gs_rt').find('a')['href']
        indirme_linki = yayin.find('div', class_='gs_or_ggsm').find('a')['href'] if yayin.find('div', class_='gs_or_ggsm') else ''
        alinti_sayisi_arama = yayin.find('div', class_="gs_fl gs_flb").find_all('a')[2]
        alinti_sayisi = alinti_sayisi_arama.text.strip() if alinti_sayisi_arama else ''
        # Anahtar kelimeleri ve diğer bilgileri al
        if 'dergipark.org.tr' in detay_link:  # Eğer dergipark sitesine aitse
            ozet, referanslar, alinti_sayisi = dergipark_bilgileri(detay_link,baslik,indirme_linki,alinti_sayisi)
        else:
            ozet, referanslar, alinti_sayisi = '', '', ''
        # Bekleme süresi ekleme
        wait_time = random.uniform(1, 3)  # Rastgele 2 ila 5 saniye bekleme
        time.sleep(wait_time)
    

def dergipark_bilgileri(detay_link,baslik2,indirme_linki,alinti_sayisi):
    wait_time = random.uniform(1, 3)  # Rastgele 2 ila 5 saniye bekleme
    time.sleep(wait_time)
    response = requests.get(detay_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        baslik=soup.find('div',class_="h3 d-flex align-items-baseline").find('h3').text.strip() if soup.find('div',class_="h3 d-flex align-items-baseline") else ''
        ozet = soup.find('div', class_='article-abstract data-section').find('p').text.strip() if soup.find('div', class_='article-abstract data-section') else ''
        referanslar = soup.find('div', class_='article-citations data-section').find('ul',class_='fa-ul').find_all('li') if soup.find('div', class_='article-citations data-section') else ''
        referans_listesi = []
        for numara, referans in enumerate(referanslar, 1):
            referans_listesi.append(f"{numara}. {referans.text.strip()}")
        anahtar_kelimeler = soup.find('div',class_="article-keywords data-section").find_all('a') if soup.find('div',class_="article-keywords data-section") else ''
        anahtar_kelime_liste=[]
        for anahtar_kelime in anahtar_kelimeler:
            anahtar_kelime_liste.append(anahtar_kelime.text.strip())
        tr_etiketleri = soup.find_all('tr')
        dil = None
        konular = None
        yayin_turu = None
        yazarlar = []
        yayinlanma_tarihi = None
        teslim_tarihi = None
        yayinlanma_yili = None

        for tr in tr_etiketleri:
            baslik = tr.find('th').text.strip() if tr.find('th') else None
            veri = tr.find('td').text.strip() if tr.find('td') else None
            if baslik and veri:
                if baslik == 'Primary Language':
                    dil = veri
                elif baslik == 'Subjects':
                    konular = veri
                elif baslik == 'Journal Section':
                    yayin_turu = veri
                elif baslik == 'Authors':
                    yazarlar = [yazar.strip() for yazar in veri.split('\n') if yazar.strip()]
                elif baslik == 'Publication Date':
                    yayinlanma_tarihi = veri
                elif baslik == 'Submission Date':
                    teslim_tarihi = veri
                elif baslik == 'Published in Issue':
                    yayinlanma_yili = veri
        
        print('Başlık:',baslik2)
        print("Dil:", dil)
        print("Konular:", konular)
        print("Yayın türü:", yayin_turu)
        print("Yazarlar:", yazarlar)
        print("Yayınlanma Tarihi:", yayinlanma_tarihi)
        print("Teslim Tarihi:", teslim_tarihi)
        print("Yayınlanma yılı:", yayinlanma_yili)
        print('Alıntı sayısı:',alinti_sayisi)
        for referans in referans_listesi:
            print(referans)
        print('Özet:',ozet)
        print('Anahtar Kelimeler:',anahtar_kelime_liste)
        print('URL:',detay_link)
        print('',alinti_sayisi)
        wait_time = random.uniform(1, 3)  # Rastgele 2 ila 5 saniye bekleme
        time.sleep(wait_time)

        veri_ekle({
            'yayinad': baslik2,
            'dil':dil,
            'konular':konular,     
            'yazarlar': yazarlar,
            'yayinturu': yayin_turu,
            'yayintarihi': yayinlanma_tarihi,
            'yayinlanma_yili':yayinlanma_yili,
            'Anahtar_Kelimeler':anahtar_kelime_liste,
            'ozet': ozet,
            'referanslar': referans_listesi,
            'alinti_sayisi': alinti_sayisi,
            'detay_link': detay_link,
            'indirme_linki':indirme_linki
        })

        return ozet, referans_listesi, alinti_sayisi
    else:
        print(f'Hata {response.status_code} - Sayfa alınamadı.')
        return '', '', '', ''

def veri_ekle(veri):
    # MongoDB'ye bağlan
    client = MongoClient('mongodb://localhost:27017/')  # MongoDB bağlantı URL'sini ayarlayın
    db = client['akademik_veritabani']  # Veritabanı adını belirleyin
    collection = db['yayinlar']  # Koleksiyon adını belirleyin

    try:
        # Veriyi ekleyin
        result = collection.insert_one(veri)
        print(f'ID: {result.inserted_id} ile veri eklendi.')
    except Exception as e:
        print(f'Veri eklerken hata oluştu: {e}')
    finally:
        # Bağlantıyı kapat
        client.close()


if __name__ == '__main__':
    anahtar_kelime = input('Arama yapmak istediğiniz anahtar kelimeyi girin: ')
    html = arama_yap(anahtar_kelime)

    if html:
        bilgileri_cikar(html)



        










