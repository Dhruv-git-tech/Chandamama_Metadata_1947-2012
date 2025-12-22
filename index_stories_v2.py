
import os
import json
import re
import sys
import difflib

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = r"C:\Users\Dhruv\Documents\chandamama 3.0"
JSON_METADATA_DIR = os.path.join(ROOT_DIR, "json_metadata")

def load_json(filepath):
    """Loads JSON data from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {filepath}")
        return None

def save_json(filepath, data):
    """Saves data to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def clean_text(text):
    """Cleans text by removing markdown symbols and excessive whitespace."""
    if not text:
        return ""
    text = re.sub(r'[#*]', '', text) 
    return text.strip()

def extract_author_from_content(content):
    """
    Attempts to find an author signature at the end of the content.
    Looks for lines starting with '—' or '-' in the last few lines.
    """
    if not content:
        return None
        
    lines = content.strip().split('\n')
    # Check last 3 lines
    for line in reversed(lines[-3:]):
        line = line.strip()
        # Regex for em-dash, en-dash, or hyphen followed by text
        match = re.match(r'^[—–-]\s*(.+)$', line)
        if match:
            return match.group(1).strip()
            
    return None

def get_data_from_md_folder(folder_path):
    """
    Parses all Markdown files.
    Returns: { 
        pdf_page_int: {
            'content': str,
            'headers': [list of str],
            'author_candidate': str,
            'has_double_hash': bool  # True if file contains '##'
        }
    }
    """
    data_map = {}
    if not os.path.exists(folder_path):
        return data_map

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            filepath = os.path.join(folder_path, filename)
            
            match = re.search(r'page_(\d+)', filename)
            if match:
                pdf_page = int(match.group(1))
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    lines = content.split('\n')
                    headers = []
                    has_double_hash = False
                    
                    # 1. Scan for '##' headers
                    for line in lines:
                        strip_line = line.strip()
                        if strip_line.startswith('##'):
                            has_double_hash = True
                            clean = clean_text(strip_line)
                            if clean:
                                headers.append(clean)
                                
                    # 2. Also grab Single '#' headers just in case
                    for line in lines:
                        strip_line = line.strip()
                        if strip_line.startswith('#') and not strip_line.startswith('##'):
                            clean = clean_text(strip_line)
                            if clean:
                                headers.append(clean)

                    author_cand = extract_author_from_content(content)
                    
                    data_map[pdf_page] = {
                        'content': content,
                        'headers': headers,
                        'author_candidate': author_cand,
                        'has_double_hash': has_double_hash
                    }
                    
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    
    return data_map

def find_best_md_page_match(json_title, md_map):
    """
    Finds the MD page that contains a header matching the json_title.
    Priority: '##' headers.
    Returns: matching_pdf_page_int OR None
    """
    best_page = None
    best_ratio = 0
    
    for pdf_page, data in md_map.items():
        headers = data['headers']
        # If '##' exists, only check those? Or check all but weight them?
        # User said "indicated as ##".
        # Let's filter for ## if possible, but our 'headers' list mixes them?
        # No, let's just check all extracted headers. 
        # But we strongly prefer pages that actually have headers.
        
        for header in headers:
            ratio = difflib.SequenceMatcher(None, json_title, header).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_page = pdf_page
                
    if best_ratio > 0.75: 
        return best_page
        
    return None

def process_folder(folder_name):
    md_folder_path = os.path.join(ROOT_DIR, folder_name)
    json_filename = folder_name.replace(" ", "_") + ".json"
    
    # Locate JSON - if not found, we will generate it.
    parts = folder_name.split()
    year = "Unknown"
    old_json_path = None
    if len(parts) >= 2 and parts[1].isdigit():
        year = parts[1]
        path_year = os.path.join(JSON_METADATA_DIR, year, json_filename)
        path_root = os.path.join(JSON_METADATA_DIR, json_filename)
        if os.path.exists(path_year): old_json_path = path_year
        elif os.path.exists(path_root): old_json_path = path_root
    
    md_map = get_data_from_md_folder(md_folder_path)
    if not md_map:
        return

    stories = []
    
    if old_json_path:
        # EXISTING JSON LOGIC
        old_data = load_json(old_json_path)
        if old_data:
            stories = old_data.get('stories', [])
            
        # 1. Map Stories to Start Pages
        assigned_stories = []
        story_start_pages = set()

        for story in stories:
            title = story.get('title', '')
            match_page = find_best_md_page_match(title, md_map)
            if match_page is None:
                 p_start = story.get('page_start', 0)
                 if p_start in md_map:
                     match_page = p_start
            
            if match_page is not None and match_page in md_map:
                story['pdf_page'] = match_page
                story_start_pages.add(match_page)
                assigned_stories.append({'story': story, 'start_page': match_page})
            else:
                assigned_stories.append({'story': story, 'start_page': 999999})

        assigned_stories.sort(key=lambda x: x['start_page'])
        
    else:
        # MISSING JSON LOGIC - GENERATE FROM SCRATCH
        # Create stories from '##' headers in MD files
        print(f"Generating metadata for {folder_name} (No existing JSON found)")
        sorted_pages = sorted(md_map.keys())
        assigned_stories = []
        
        for page in sorted_pages:
            p_data = md_map[page]
            # Fix for duplication: Only take the FIRST header as the story title.
            # This avoids creating separate stories for "Title" and "Subtitle" on the same page.
            if p_data['headers']:
                header = p_data['headers'][0]
                story = {
                    "title": header,
                    "page_start": page, 
                    "pdf_page": page,
                    "content": "" 
                }
                assigned_stories.append({'story': story, 'start_page': page})
        
        # Determine Book ID if possible
        old_data = {"book_id": folder_name}

    # 2. Build Content (Continuation Logic) - Shared for both paths
    for i, item in enumerate(assigned_stories):
        story = item['story']
        start_page = item['start_page']
        
        if start_page == 999999 or start_page not in md_map:
            continue
            
        full_content = []
        author_from_md = None
        
        next_story_start = 999999
        if i + 1 < len(assigned_stories):
            next_story_start = assigned_stories[i+1]['start_page']
            
        current_page = start_page
        while current_page in md_map:
            if current_page >= next_story_start and current_page != start_page:
                break
                
            # If generating from scratch, we rely on assigned_stories which came from headers,
            # so the 'break on ##' check is redundant but safe.
            # If using existing JSON, we still want to break on new unindexed headers.
            if current_page != start_page and md_map[current_page]['has_double_hash']:
                # However, if we generated stories from ALL headers, this condition is naturally covered
                # by 'next_story_start' logic unless we missed a header.
                pass 
                
            # Check for double hash strict break only if we are enriching (old_json_path exists)
            # OR if we are generating, next_story_start handles it.
            # Let's keep the safety break but maybe relax it? 
            # Actually, standard behavior: if we hit a new ##, it's likely a new story.
            if current_page != start_page and md_map[current_page]['has_double_hash']:
                 break
            
            page_data = md_map[current_page]
            full_content.append(page_data['content'])
            if page_data['author_candidate']:
                author_from_md = page_data['author_candidate']
                
            current_page += 1
            
        story['content'] = "\n\n".join(full_content)
        if author_from_md and 'author' not in story:
            story['author'] = author_from_md

    # Save
    new_data = {
        "book_id": old_data.get('book_id', folder_name),
        "stories": [item['story'] for item in assigned_stories]
    }
    
    if year != "Unknown":
        save_path = os.path.join(JSON_METADATA_DIR, year, json_filename)
        save_json(save_path, new_data)
        print(f"Processed {folder_name} -> {year}/{json_filename}")

def main():
    folders = [f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f)) and f.startswith("చందమామ")]
    for folder in sorted(folders):
        process_folder(folder)
    print("Indexing Complete.")

if __name__ == "__main__":
    main()
