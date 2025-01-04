import requests
import os
from PIL import Image
import re
import time
import urllib.parse
import cv2
import numpy as np

def scrape_images(keywords, num_images=20):
    # Load the face detection classifier with improved accuracy
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    for keyword in keywords:
        if not os.path.exists(keyword):
            os.makedirs(keyword)
            # Create a subfolder for cropped faces
            os.makedirs(os.path.join(keyword, 'faces'))

        # Properly encode Korean search terms
        encoded_keyword = urllib.parse.quote(f"{keyword}")
        
        # Simplified search URL that works better with Korean terms
        search_url = f"https://www.google.com/search?q={encoded_keyword}&tbm=isch&hl=ko&gl=kr"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',  # Added Korean language preference
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        print(f"Searching for: {keyword}")
        
        try:
            response = requests.get(search_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Modified pattern to catch more image URLs
            image_urls = []
            patterns = [
                r'\"(https?:\/\/[^\"]*?\.(?:jpg|jpeg|png))\"',
                r'(https?:\/\/[^\"]*?\.(?:jpg|jpeg|png))',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                for url in matches:
                    if isinstance(url, tuple):
                        url = url[0]
                    if (url.startswith('http') and 
                        not 'gstatic.com' in url and 
                        not 'google.com' in url and 
                        url not in image_urls):
                        image_urls.append(url)
            
            print(f"Found {len(image_urls)} image URLs")
            
            
            # Download images
            successful_downloads = 0
            for i, img_url in enumerate(image_urls):
                if successful_downloads >= num_images:
                    break

                try:
                    print(f"Attempting to download: {img_url}")
                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    img_response.raise_for_status()
                    
                    # Convert to numpy array for OpenCV processing
                    image_array = np.asarray(bytearray(img_response.content), dtype=np.uint8)
                    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    
                    if img is None:
                        print("Failed to load image")
                        continue
                    
                    # OpenCV gray scale is used to convert images to black and white for better face detection.
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # Apply histogram equalization to improve contrast
                    gray = cv2.equalizeHist(gray)
                    
                    # Detect faces with scaleFactor and minNeighbors parameters
                    faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.08,  # Reduce this value to improve accuracy, but if you decrease it too much, you might end up saving 0 images.
                        minNeighbors=6,    # Increased for fewer false positives
                        
                        #minimum and maximum size of the image to be saved
                        minSize=(100, 100),
                        maxSize=(2000, 2000)  
                    )
                    
                    if len(faces) > 0:
                        for i, (x, y, w, h) in enumerate(faces):
                            # Increase padding for better face context
                            padding = int(w * 0.3)
                            x1 = max(x - padding, 0)
                            y1 = max(y - padding, 0)
                            x2 = min(x + w + padding, img.shape[1])
                            y2 = min(y + h + padding, img.shape[0])
                            
                            # Crop the face
                            face_img = img[y1:y2, x1:x2]
                            
                            # Convert from BGR to RGB for PIL
                            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                            
                            # Convert to PIL Image
                            face_pil = Image.fromarray(face_rgb)
                            
                            # Convert to black and white using PIL
                            face_bw = face_pil.convert('L')  # 'L' mode = single channel grayscale
                            
                            # Enhance the image
                            from PIL import ImageEnhance
                            
                            # Enhance contrast
                            enhancer = ImageEnhance.Contrast(face_bw)
                            face_bw = enhancer.enhance(1.2)  # Increase contrast by 20%
                            
                            # Enhance sharpness
                            enhancer = ImageEnhance.Sharpness(face_bw)
                            face_bw = enhancer.enhance(1.1)  # Increase sharpness by 10%
                            
                            # Save the cropped face
                            save_path = os.path.join(keyword, 'faces', f"{keyword}_face_{successful_downloads + 1}_{i + 1}.jpg")
                            face_bw.save(save_path, 'JPEG', quality=95)
                            print(f"Successfully saved face: {save_path}")
                        
                        successful_downloads += 1
                    else:
                        print("No faces detected in the image")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue
                    
            print(f"Successfully downloaded {successful_downloads} images for '{keyword}'")
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            continue

# Example usage
keywords = ['your', 'keywords','here']
scrape_images(keywords, 20)

