import requests
import os
from PIL import Image
from io import BytesIO
import re
import time
import urllib.parse

def scrape_images(keywords, num_images=20):  #num_images is the number of images you want to download per keyword
    for keyword in keywords:
        if not os.path.exists(keyword):
            os.makedirs(keyword)

        # Properly encode Korean search terms
        encoded_keyword = urllib.parse.quote(f"{keyword}")
        
        # Simplified the search URL so that it works better with Korean terms
        search_url = f"https://www.google.com/search?q={encoded_keyword}&tbm=isch&hl=ko&gl=kr"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',  # Added Korean language preference for me to search in Korean, you can add your own preferred language
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        print(f"Searching for: {keyword}") #Remove the print statements if you want your terminal to be clean
        
        try:
            response = requests.get(search_url, headers=headers, timeout=30)  # 30 second timeout for search request
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
            
            # Modify image verification to prefer portrait orientation and face detection
            def is_portrait_ratio(width, height):
                ratio = height / width
                return 1 <= ratio <= 1.3  # Portrait aspect ratio range, I tried with multiple ranges and it seems 1 and 1.3 gives me the best portrait images
            
            # Download images
            successful_downloads = 0
            for img_url in image_urls:
                if successful_downloads >= num_images:
                    break

                try:
                    print(f"Attempting to download: {img_url}")
                    img_response = requests.get(img_url, headers=headers, timeout=10)  # 10 second timeout for image download
                    img_response.raise_for_status()
                    
                    # Verify it's an image and check its size
                    image = Image.open(BytesIO(img_response.content))
                    width, height = image.size
                    
                    # Check for minimum size and portrait orientation - increase the minimum size if you want bigger images
                    if (width >= 500 and height >= 500 and is_portrait_ratio(width, height)):

                        image = image.convert('L') #converts image to black and white. Remove this line for colored images

                        save_path = os.path.join(keyword, f"{keyword}_{successful_downloads + 1}.jpg")
                        image.save(save_path, 'JPEG', quality=95)
                        print(f"Successfully downloaded: {save_path} - Size: {width}x{height}")
                        successful_downloads += 1
                    else:
                        print(f"Skipping image - wrong size/ratio: {width}x{height}")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error downloading image: {str(e)}")
                    continue
                    
            print(f"Successfully downloaded {successful_downloads} images for '{keyword}'")
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            continue

# Example usage
keywords = ['your','keyword(s)','here'] #Keywords should be separated by quotation marks and commas. 
scrape_images(keywords, 1) #This is how you call the function. 

