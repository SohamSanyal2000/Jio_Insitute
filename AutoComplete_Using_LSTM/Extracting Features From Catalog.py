# Script for Extracting Features from Fynd Catalog

import json
import urllib.parse
import os
import re

# File names and paths setup
input_file_name = "Original Fynd Catalog.json"
output_file_name = "Extracted Features.json"
unique_words_file_name = "List Of Unique Words.json"

# Get the current script directory
script_directory = os.path.dirname(os.path.realpath(__file__))
input_file_path = os.path.join(script_directory, input_file_name)
output_file_path = os.path.join(script_directory, output_file_name)
unique_words_file_path = os.path.join(script_directory, unique_words_file_name)

#Create a URL for a given category. Function returns category_url
def create_category_url(category):

    base_url = "https://www.gofynd.com/products/?q="
    encoded_category = urllib.parse.quote_plus(category)
    category_url = f"{base_url}{encoded_category}"
    return category_url

# Read the input JSON file
with open(input_file_path, 'r') as infile:
    data = json.load(infile)

# Process each dictionary in the list
result_list = []
for item in data:
    # Extract values
    name = item.get("name", "")
    slug = item.get("slug", "")
    
    # Append the specified string to the slug
    slug_with_prefix = f"https://www.gofynd.com/product/{slug}"

    # Extract the first "url" from "medias" list, if available
    media_url = item.get("medias", [{}])[0].get("url", "")
    categories = item.get("categories", [{}])[0].get("name", "")
    category_url = create_category_url(categories)
    description = item.get("attributes", {}).get("description", "")


    # Create a dictionary with extracted values
    result_dict = {
        "title": name,
        "url": slug_with_prefix,
        "media": media_url,
        "category": categories,
        "category_url": category_url,  
        "description": description                        
    }

    # Add the dictionary to the result list
    result_list.append(result_dict)

# Write the result list to a new JSON file
with open(output_file_path, 'w') as outfile:
    json.dump(result_list, outfile, indent=2)

#========================================================================================================================
# Creating the cleaned unique list of words from the catalog. 

# Extract all the names
names = [item['name'] for item in data]

# Separate names into one large list of separated words and Step 4: Remove special characters and repeated words
separated_words = []
for name in names:
    # Using regex to remove special characters and split into words
    words = re.findall(r'\b\w+\b', name.lower())
    separated_words.extend(words)

# Step 4: Remove repeated words
unique_words = list(set(separated_words))

filtered_words = [word for word in unique_words if not word.isdigit() and not any(char.isdigit() for char in word)]
filtered_words2 = [word for word in filtered_words if len(word) > 2]


# Step 5: Store the final unique_words list into a new JSON file

with open(unique_words_file_path, 'w') as output_file:
    json.dump(filtered_words2, output_file)

