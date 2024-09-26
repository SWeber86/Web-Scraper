import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm
import time  # Import the time module
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

def extract_tags(page, tag):
    tags = [element for element in page.find_all(tag)]
    return tags

def scrape_data(url):
    # Start measuring page load time
    start_time = time.time()
    response = requests.get(url, headers=headers)
    end_time = time.time()
    page_load_time = end_time - start_time
    # End measuring page load time

    if response.status_code != 200:
        return None, None

    page = BeautifulSoup(response.content, 'html.parser')
    canonical_url = page.find('link', {'rel': 'canonical'})
    canonical_url = canonical_url['href'] if canonical_url else None

    h1_tags = extract_tags(page, "h1")
    h2_tags = extract_tags(page, "h2")
    h3_tags = extract_tags(page, "h3")
    h4_tags = extract_tags(page, "h4")
    h5_tags = extract_tags(page, "h5")
    paragraphs = extract_tags(page, "p")

    data = {
        'URL': url,
        'Canonical URL': canonical_url,
        'Title': page.title.get_text().strip() if page.title else '',
        'Meta_Description': page.find('meta', attrs={'name': 'description'})['content'].strip() if page.find('meta', attrs={'name': 'description'}) else '',
        'Page_Speed': f"{page_load_time:.2f} seconds"  # Include page load time at the end
    }

    tag_counts = {'H1': len(h1_tags), 'H2': len(h2_tags), 'H3': len(h3_tags), 'H4': len(h4_tags), 'H5': len(h5_tags),
                  'Paragraph': len(paragraphs)}

    for i, tags in enumerate([h1_tags, h2_tags, h3_tags, h4_tags, h5_tags, paragraphs], start=1):
        tag_prefix = ['H1', 'H2', 'H3', 'H4', 'H5', 'Paragraph'][i - 1]
        for j, tag in enumerate(tags, start=1):
            tag_text = tag.get_text().strip()
            if tag_prefix == 'Paragraph':
                parent_tag = tag.find_previous(re.compile(r'^h[1-5]$'))
                parent_tag_text = f"{parent_tag.name}_{tags.index(tag) + 1}" if parent_tag else ""
                data[f"{tag_prefix}_{j}"] = f"({parent_tag_text}) {tag_text}"
            else:
                data[f"{tag_prefix}_{j}"] = tag_text

    return data, tag_counts

def fetch_and_process_urls(urls):
    all_links = []
    for url in tqdm(urls, desc="Processing Links"):  # Add progress update for processing links
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page = BeautifulSoup(response.content, 'html.parser')
            a_tags = page.find_all('a')
            for tag in a_tags:
                href = tag.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    span = tag.find('span')
                    link_text = span.get_text(strip=True) if span else tag.get_text(strip=True)
                    all_links.append({
                        'Page URL': url,
                        'Link Text': link_text,
                        'Destination URL': absolute_url  # Use the absolute URL
                    })
        else:
            print(f"Failed to fetch {url}")
    return pd.DataFrame(all_links, columns=['Page URL', 'Link Text', 'Destination URL'])

def get_alt_text(img):
    return img.get('alt', 'Missing Alt Attributes')

def scrape_images(urls):
    images_data = []  # Initialize an empty list for image data
    # Initialize a progress bar for the URLs
    with tqdm(total=len(urls), desc="Scraping Alt Attributes") as pbar:
        for url in urls:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            images = soup.find_all('img')
            for image in images:
                images_data.append({
                    'URL': url,
                    'Image Source': image['src'] if 'src' in image.attrs else 'No Source Attribute',
                    'Alt Text': get_alt_text(image)
                })
            pbar.update(1)  # Update the progress bar after each URL is processed
    return pd.DataFrame(images_data)

# Main function to scrape data from URLs and store in pandas DataFrames
def scrape_urls(urls):
    all_data = []
    tag_max_counts = {'H1': 0, 'H2': 0, 'H3': 0, 'H4': 0, 'H5': 0, 'Paragraph': 0}

    for url in tqdm(urls, desc="Scraping URLs"):
        data, tag_counts = scrape_data(url)
        if data is not None:
            all_data.append(data)
            for tag, count in tag_counts.items():
                if count > tag_max_counts[tag]:
                    tag_max_counts[tag] = count

    # Fill missing tag values with 'NA'
    for data in all_data:
        for tag, max_count in tag_max_counts.items():
            for i in range(1, max_count + 1):
                if f"{tag}_{i}" not in data:
                    data[f"{tag}_{i}"] = 'NA'

    # Create the final DataFrame
    columns_order = ['URL', 'Canonical URL', 'Title', 'Meta_Description']
    for tag, max_count in tag_max_counts.items():
        for i in range(1, max_count + 1):
            columns_order.append(f"{tag}_{i}")
    columns_order.append('Page_Speed')

    final_dataframe = pd.DataFrame(all_data, columns=columns_order)

    # Scrape links and images
    links_df = fetch_and_process_urls(urls)
    images_df = scrape_images(urls)

    return final_dataframe, links_df, images_df

# Example usage:
urls = ['https://example.com/']  # Replace with your URLs
indexed_pages_df, links_report_df, images_alt_report_df = scrape_urls(urls)

# Display the dataframes or work with them further
print(indexed_pages_df)
print(links_report_df)
print(images_alt_report_df)

indexed_pages_df