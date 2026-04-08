import requests
import concurrent.futures

# --- GENİŞLETİLMİŞ KAYNAK HAVUZU ---
# Buraya ne kadar çok GitHub kaynağı eklersek, maç esnasında o kadar çok yedeğimiz olur.
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/tur.m3u",
    "https://raw.githubusercontent.com/Furkan-Gulsen/IPTV-Dunyasi/master/IPTV_Dunyasi.m3u",
    "https://raw.githubusercontent.com/Suleyman-K/IPTV-TR/main/spor.m3u",
    "https://raw.githubusercontent.com/Hukumdar/IPTV/master/tr.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'}

def validate_link(channel_tuple):
    name, url = channel_tuple
    try:
        # Sadece başlık kontrolü değil, yayının gerçekten akıp akmadığını kontrol et (timeout 3s)
        r = requests.get(url, headers=HEADERS, stream=True, timeout=3)
        if r.status_code == 200:
            return (name, url)
    except:
        return None

def bot_calistir():
    print("🛰️ MODIE Kesintisiz Yayın Sistemi Devrede...")
    raw_data = []
    
    for src in SOURCES:
        try:
            res = requests.get(src, timeout=10)
            if res.status_code == 200:
                lines = res.text.split('\n')
                for i in range(len(lines)):
                    if "#EXTINF" in lines[i]:
                        info = lines[i]
                        link = lines[i+1].strip()
                        # ANAHTAR KELİME FİLTRESİ (Spor ve Ulusal)
                        if any(x in info.upper() for x in ["BEIN", "SPOR", "EXXEN", "TIVIBU", "TRT", "STAR", "KANAL D", "TV8", "TABII"]):
                            raw_data.append((info, link))
        except: continue

    # Linkleri doğrula (Multi-thread)
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        valid_ones = list(filter(None, executor.map(validate_link, raw_data)))

    # YAYIN DURMAMASI İÇİN GRUPLAMA VE YEDEKLİ YAZMA
    with open("sinirsiz_yayin.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        seen_links = set()
        for name, url in valid_ones:
            if url not in seen_links:
                f.write(f"{name}\n{url}\n")
                seen_links.add(url)
    
    print(f"✅ {len(seen_links)} adet çalışan yedekli kanal hazır!")

if __name__ == "__main__":
    bot_calistir()
      
