import requests
from bs4 import BeautifulSoup
import re

def scrape_wikipedia(url: str):
    """
    Robust Wikipedia scraper that properly extracts article content
    """
    try:
        # Validate URL
        if 'wikipedia.org' not in url.lower():
            raise ValueError("Please provide a valid Wikipedia URL")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"Fetching Wikipedia URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title - multiple selectors for robustness
        title = None
        title_selectors = ['h1#firstHeading', 'h1.firstHeading', 'h1']
        for selector in title_selectors:
            title = soup.select_one(selector)
            if title:
                break
        
        title_text = title.get_text().strip() if title else "Unknown Title"
        print(f"Found title: {title_text}")
        
        # Find the main content area - multiple strategies
        content_area = None
        
        # Strategy 1: Look for the main content div
        content_selectors = [
            'div#mw-content-text',
            'div.mw-content-text', 
            'div.mw-parser-output',
            'div.content'
        ]
        
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                print(f"Found content using selector: {selector}")
                break
        
        # Strategy 2: If no specific content div, look for paragraphs in body
        if not content_area:
            print("No specific content div found, using body content")
            content_area = soup.find('body')
        
        if not content_area:
            raise ValueError("Could not find any content area on the page")
        
        # Remove unwanted elements - be more specific
        unwanted_elements = content_area.find_all([
            'script', 'style', 'table', 'sup', 'div.thumb', 'div.navbox',
            'div.infobox', 'div.hatnote', 'span.reference', 'div.reference',
            'ol.references', 'div.mw-references-wrap', 'link', 'meta',
            'img', 'figure', 'aside', 'nav', 'footer', 'header'
        ])
        
        for element in unwanted_elements:
            element.decompose()
        
        # Also remove elements by class that contain navigation or metadata
        unwanted_classes = [
            'navbox', 'infobox', 'hatnote', 'reference', 'citation',
            'external', 'mw-editsection', 'mw-redirect', 'geo',
            'coordinates', 'metadata', 'ambox', 'sidebar'
        ]
        
        for class_name in unwanted_classes:
            elements = content_area.find_all(class_=class_name)
            for element in elements:
                element.decompose()
        
        # Extract text from paragraphs
        paragraphs = content_area.find_all('p')
        text_content = []
        
        for p in paragraphs:
            text = p.get_text().strip()
            # Clean the text
            text = re.sub(r'\[\d+\]', '', text)  # Remove [1], [2], etc.
            text = re.sub(r'\[\w+\]', '', text)  # Remove [citation needed], etc.
            text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
            text = text.strip()
            
            # Only include substantial paragraphs (not navigation, disclaimers, etc.)
            if (len(text) > 50 and 
                not text.startswith('This article') and
                not text.startswith('For other uses') and
                not text.startswith('In other projects') and
                'disambiguation' not in text.lower()):
                text_content.append(text)
        
        # If we still don't have enough content, try a different approach
        if len(text_content) < 3:
            print("Not enough paragraphs found, trying alternative extraction...")
            # Get all text from the main content area
            all_text = content_area.get_text()
            # Split into sentences and take the first substantial ones
            sentences = re.split(r'[.!?]+', all_text)
            text_content = [s.strip() for s in sentences if len(s.strip()) > 30][:20]
        
        clean_text = ' '.join(text_content)
        
        # Final cleanup
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        print(f"Final content length: {len(clean_text)} characters")
        
        if len(clean_text) < 100:
            # If still too short, provide more diagnostic info
            print(f"Diagnostic - Number of paragraphs found: {len(paragraphs)}")
            print(f"Diagnostic - First paragraph preview: {paragraphs[0].get_text()[:100] if paragraphs else 'No paragraphs'}")
            raise ValueError(f"Not enough meaningful content found. Only extracted {len(clean_text)} characters.")
        
        print(f"Successfully scraped Wikipedia article: {title_text}")
        return {
            "title": title_text,
            "content": clean_text[:12000]  # Limit for LLM
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch the Wikipedia page: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing the page: {str(e)}")