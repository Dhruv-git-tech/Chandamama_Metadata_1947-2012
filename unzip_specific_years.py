
import zipfile
import os
import shutil
import sys

# Set UTF-8 encoding for output to handle Telugu filenames
sys.stdout.reconfigure(encoding='utf-8')

zip_path = "extracted-text.zip"
years_to_extract = [str(y) for y in range(2002, 2013)]  # 2002 to 2012
root_prefix = "extracted-text/"

print("Starting extraction...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for file in zip_ref.namelist():
        # Check if file matches our years
        for year in years_to_extract:
            # Match strictly the year folders we want
            # e.g. extracted-text/చందమామ 1969 01/...
            year_folder_part = f"చందమామ {year}"
            
            if file.startswith(root_prefix + year_folder_part):
                # We want to extract it, but strip root_prefix
                # zipfile.extract extracts full path.
                # So we extract, then we will move it.
                # Optimization: check if target already exists to avoid re-work? 
                # Better just overwrite/update.
                
                # Check if it is a directory or file
                if file.endswith('/'):
                    continue
                
                # Extract to temp location or just extract and move
                zip_ref.extract(file)
                
                # Source path after extraction
                src_path = os.path.abspath(file)
                
                # Destination path (strip extracted-text/)
                # file is "extracted-text/folder/file"
                # dest is "folder/file"
                relative_path = file[len(root_prefix):] 
                dest_path = os.path.abspath(relative_path)
                
                # Create dest dir
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Move/Rename
                # Windows might have issues if file exists, execute move safely
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(src_path, dest_path)
                
                print(f"Extracted: {relative_path}")

# Cleanup the empty extracted-text folder if we made it
if os.path.exists("extracted-text"):
    # Only remove if empty or we want to clean up?
    # Better leave it or try rmdir which fails if not empty
    try:
        os.rmdir("extracted-text")
    except:
        pass

print("Extraction complete.")
