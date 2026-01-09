#!/usr/bin/env python3
"""
Download Pallett Creek seismite data from USGS ScienceBase
DOI: https://doi.org/10.5066/P917R4F9

Purpose: Check for lake sediment seismites around ~1285/1310 CE to validate
         potential SAF dark earthquake
"""

import sciencebasepy
import os
import json

# Initialize ScienceBase session
sb = sciencebasepy.SbSession()

# DOI for Pallett Creek dataset
doi = "10.5066/P917R4F9"

print(f"Searching for Pallett Creek dataset...")
print(f"DOI: {doi}\n")

# Try searching by title first (more reliable than DOI search)
items = sb.find_items_by_any_text("Pallett Creek")

if items and items.get('items'):
    print(f"Found {len(items['items'])} items matching 'Pallett Creek':\n")

    # Look for the item with our DOI
    target_item = None
    for item in items['items']:
        print(f"  - {item.get('title')}")
        if item.get('doi') == doi or doi in str(item.get('identifiers', [])):
            target_item = item
            print(f"    ✓ Matches DOI {doi}")

    if target_item:
        item_id = target_item['id']
        print(f"\n✓ Found target item ID: {item_id}")

        # Get full item details
        item = sb.get_item(item_id)

        print(f"\nTitle: {item.get('title')}")
        if 'summary' in item:
            print(f"Summary: {item['summary'][:300]}...")

        # Create download directory
        download_dir = "../data/pallett_creek"
        os.makedirs(download_dir, exist_ok=True)

        # Get file information
        file_info = sb.get_item_file_info(item)

        print(f"\n{len(file_info)} files available:")
        for i, f in enumerate(file_info):
            size_kb = f.get('size', 0) / 1024
            print(f"  {i+1}. {f['name']}")
            print(f"     Size: {size_kb:.1f} KB")
            print(f"     URL: {f['url'][:80]}...")

        # Download files
        if file_info:
            print(f"\nDownloading files to {download_dir}/...")

            # Download as zip (easier)
            zip_path = sb.get_item_files_zip(item, download_dir)
            print(f"\n✅ Downloaded as zip: {zip_path}")

            # Also save metadata
            metadata_path = os.path.join(download_dir, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(item, f, indent=2)
            print(f"✅ Metadata saved: {metadata_path}")

            print(f"\nNext step: Extract zip and analyze for 1285/1310 CE seismites")
        else:
            print("\n⚠️  No files found for this item")
    else:
        print(f"\n⚠️  Could not find item with DOI {doi}")
        print("Available items listed above - check manually on ScienceBase")
else:
    print("❌ No items found matching 'Pallett Creek'")
