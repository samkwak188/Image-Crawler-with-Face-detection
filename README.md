# Google Image Crawler

A Python script that downloads portrait-oriented images from Google Images based on given keywords using Requests library. The script supports multiple languages including Korean. I wrote this simple image crawling code as my of my Machine Learning Project, and that is why i used pillow to convert all images to black and white by default, so that it would be more accurate when I train my ML model. 

## Features

- 🔍 Multi-keyword search support
- 🖼️ Portrait-oriented image filtering (aspect ratio 1:1 to 1:1.3)
- 🌐 Korean language support
- ⚫️ Automatic black and white conversion
- 📏 Minimum size requirements for quality control
- 🚫 Duplicate image detection
- ⏱️ Timeout handling for reliable downloads

## Usage
1. Import the required libraries.
2. Define your keywords, change the num_images value to the number of images you want to download per keyword, and run the script. Keywords can be in both English and Korean.

## How It Works

1. **Keyword Processing**
   - Creates a directory for each keyword
   - Properly encodes keywords for URL (especially important for Korean characters)

2. **Image Search**
   - Sends requests to Google Images
   - Uses custom headers to mimic browser behavior
   - Implements timeout handling (30s for search, 10s for downloads)

3. **Image Filtering**
   - Checks image dimensions
   - Ensures portrait orientation (height/width ratio between 1 and 1.3)
   - Requires minimum size (default: At least500x500 pixels)

4. **Image Processing**
   - Converts images to black and white
   - Saves in original format (typically JPEG)

## Error Handling

The script includes:
- Connection timeout handling
- Invalid image file detection
- Directory creation error handling
- Image processing error handling

## Notes

- Images are saved in separate folders named after each keyword
- Progress is displayed in the terminal (can be disabled)
- Respects Google's robots.txt through appropriate delays
- Uses a User-Agent string for compatibility

## Limitations

- Subject to Google's rate limiting
- Image quality depends on source
- Some images that looks better than othersmight be skipped due to size/ratio requirements
- Images scraped sometimes contains watermarks, or even not really related to the keyword.

"# Image-Crawler-" 
