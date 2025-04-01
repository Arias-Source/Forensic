import requests
from bs4 import BeautifulSoup
import re
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cache to store metadata
metadata_cache = {}

def get_video_id(url):
    """Extract video ID from the YouTube URL."""
    video_id = None
    regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.*|(?:v|e(?:mbed)?)|.*[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        video_id = match.group(1)
    return video_id

def get_video_metadata(video_id):
    """Fetch metadata for the given YouTube video ID."""
    if video_id in metadata_cache:
        logging.info("Fetching metadata from cache.")
        return metadata_cache[video_id]

    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        logging.error(f"Error: Unable to access video page (Status code: {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else 'N/A'
    
    # Extract description
    description_tag = soup.find('meta', {'name': 'description'})
    description = description_tag['content'] if description_tag else 'N/A'
    
    # Extract published date
    published_at_tag = soup.find('meta', {'itemprop': 'datePublished'})
    published_at = published_at_tag['content'] if published_at_tag else 'N/A'
    
    # Extract view count and like count from the script tag
    scripts = soup.find_all('script')
    json_data = ''
    for script in scripts:
        if 'var ytInitialPlayerResponse' in script.text:
            json_data = script.string
            break
    
    # Extract view count and like count using regex
    view_count = re.search(r'"viewCount":"(\d+)"', json_data)
    like_count = re.search(r'"likeCount":"(\d+)"', json_data)
    dislike_count = re.search(r'"dislikeCount":"(\d+)"', json_data)  # Note: Dislike count may not be available
    comment_count = re.search(r'"commentCount":"(\d+)"', json_data)  # Note: Comment count may not be available
    
    metadata = {
        'Title': title,
        'Description': description,
        'Published At': published_at,
        'View Count': view_count.group(1) if view_count else 'N/A',
        'Like Count': like_count.group(1) if like_count else 'N/A',
        'Dislike Count': dislike_count.group(1) if dislike_count else 'N/A',
        'Comment Count': comment_count.group(1) if comment_count else 'N/A',
    }

    # Cache the metadata
    metadata_cache[video_id] = metadata
    return metadata

def print_metadata(metadata):
    """Print the metadata in a formatted way."""
    print("\nVideo Metadata:")
    print("=" * 50)
    for key, value in metadata.items():
        print(f"{key}: {value}")
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video metadata.")
    parser.add_argument('url', type=str, help='YouTube video URL')
    args = parser.parse_args()

    video_id = get_video_id(args.url)
    
    if video_id:
        metadata = get_video_metadata(video_id)
        if metadata:
            print_metadata(metadata)
        else:
            print("No metadata found for this video.")
    else:
        print("Invalid YouTube URL.")

if __name__ == "__main__":
    main()
