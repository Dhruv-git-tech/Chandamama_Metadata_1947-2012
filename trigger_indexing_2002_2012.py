import index_stories_v2
import os

ROOT_DIR = "c:\\Users\\Dhruv\\Documents\\chandamama 3.0"
TARGET_YEARS = [str(y) for y in range(2002, 2013)]

def main():
    print(f"Starting targeted indexing for years: {TARGET_YEARS}")
    folders = [f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f)) and f.startswith("చందమామ")]
    
    count = 0
    for folder in sorted(folders):
        # Check if folder name contains any of the target years
        if any(year in folder for year in TARGET_YEARS):
            index_stories_v2.process_folder(folder)
            count += 1
            
    print(f"Indexing Complete. Processed {count} folders.")

if __name__ == "__main__":
    main()
