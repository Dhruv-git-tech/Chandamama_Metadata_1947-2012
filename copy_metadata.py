import shutil
import os

src = "json_metadata"
dst = "metadata_enriched"
# 2002 to 2012 inclusive
years = [str(y) for y in range(2002, 2013)]

for year in years:
    s = os.path.join(src, year)
    d = os.path.join(dst, year)
    if os.path.exists(s):
        if os.path.exists(d):
            shutil.rmtree(d) # Clean overwrite if exists
        shutil.copytree(s, d)
        print(f"Copied {year}")
    else:
        print(f"Skipping {year}, source not found")
