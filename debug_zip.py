
import zipfile
import sys

# Force utf-8 for output if possible, though repr is safer
sys.stdout.reconfigure(encoding='utf-8')

zip_path = "extracted-text.zip"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    names = zip_ref.namelist()
    print("First 5 files (repr):")
    for n in names[:5]:
        print(repr(n))
        
    print("\nLooking for 1969...")
    found = False
    for n in names:
        if "1969" in n:
            print(f"Found match: {repr(n)}")
            found = True
            break
    if not found:
        print("No file with '1969' found.")
