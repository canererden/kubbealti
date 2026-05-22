import subprocess
import json
import os
from datetime import datetime

def update_feed():
    url = 'https://www.instagram.com/api/v1/users/web_profile_info/?username=kubbealtikahve'
    
    try:
        print("Instagram API'sinden gönderiler alınıyor (curl ile)...")
        res = subprocess.run([
            'curl', '-fsSL',
            url,
            '-H', 'x-ig-app-id: 936619743392459',
            '-H', 'user-agent: Mozilla/5.0'
        ], capture_output=True)
        
        if res.returncode != 0:
            raise Exception(f"curl command failed: {res.stderr.decode()}")
            
        data = json.loads(res.stdout.decode())
        edges = data['data']['user']['edge_owner_to_timeline_media']['edges'][:6]
        
        # instagram klasörünü oluştur
        os.makedirs('instagram', exist_ok=True)
        existing_files = os.listdir('instagram')
        
        posts = []
        downloaded_count = 0
        
        for edge in edges:
            node = edge['node']
            shortcode = node['shortcode']
            image_url = f"https://www.instagram.com/p/{shortcode}/media/?size=l"
            image_path = f"instagram/{shortcode}.jpg"
            
            print(f"Görsel indiriliyor: {shortcode}...")
            
            # Curl ile görseli indir
            img_res = subprocess.run([
                'curl', '-fsSL', '--retry', '2', '--retry-delay', '2',
                image_url,
                '-o', image_path,
                '-H', 'user-agent: Mozilla/5.0'
            ], capture_output=True)
            
            if img_res.returncode == 0:
                downloaded_count += 1
            else:
                print(f"Görsel indirilemedi ({shortcode}): {img_res.stderr.decode()}")
                if f"{shortcode}.jpg" in existing_files:
                    print("Eski görsel kullanılıyor.")
                else:
                    continue
                
            posts.append({
                'shortcode': shortcode,
                'image': image_path,
                'postUrl': f"https://www.instagram.com/p/{shortcode}/"
            })
            
        # feed dosyasını güncelle
        feed = {
            'updatedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'profile': 'kubbealtikahve',
            'posts': posts
        }
        
        with open('instagram-feed.json', 'w', encoding='utf-8') as f:
            json.dump(feed, f, indent=2, ensure_ascii=False)
            
        # Artık kullanılmayan eski görselleri sil
        active_images = {f"{p['shortcode']}.jpg" for p in posts}
        for file in existing_files:
            if file.endswith('.jpg') and file not in active_images:
                try:
                    os.remove(os.path.join('instagram', file))
                except:
                    pass
                    
        print(f"\nBaşarılı! {downloaded_count} yeni görsel indirildi ve instagram-feed.json güncellendi.")
        
    except Exception as e:
        print(f"\nInstagram feed güncellenirken hata oluştu: {e}")

if __name__ == '__main__':
    update_feed()
