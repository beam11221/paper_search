import os
import json
import pandas as pd
from datetime import datetime

def extract_fields_from_json(json_file_path):
    """
    Extract specific fields from the JSON file and convert them into a flat columnar DataFrame.
    
    :param json_file_path: Path to the JSON file.
    :return: Pandas DataFrame with extracted fields.
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Extract root object for processing
    response = data.get('abstracts-retrieval-response', {})
    
    # 1. Extract date-sort (concatenate @day, @year, @month)
    date_sort = response.get('item', {}).get('ait:process-info', {}).get('ait:date-sort', {})
    date_sort_formatted = f"{date_sort.get('@year', '0000')}{date_sort.get('@month', '00')}{date_sort.get('@day', '00')}"
    
    # 2. Extract unique countries from author affiliations
    # author_groups = response.get('item', {}).get('bibrecord', {}).get('head', {}).get('author-group', [])
    # if isinstance(author_groups, dict):
    #     country_list = [author_groups['affiliation']['country']]
    # else:
    #     country_list = list(set(d['affiliation']['country'] for d in author_groups))

    # 3. Extract abstracts
    abstracts = response.get('item', {}).get('bibrecord', {}).get('head', {}).get('abstracts', '')
    
    # 4. Extract bibliography @refcount
    tail = response.get('item', {}).get('bibrecord', {}).get('tail', {})
    if tail is None:
        ref_count = None
    else:
        ref_count = tail.get('bibliography', {}).get('@refcount', 0)
    
    # 5. Extract unique affiliation organization names
    affiliations = response.get('affiliation', [])
    if isinstance(affiliations, dict):
        affiliation_names = [affiliations.get('affilname', '')]
    else:
        affiliation_names = list({affil.get('affilname', '') for affil in affiliations})
    
    # 6-9. Extract coredata fields
    coredata = response.get('coredata', {})
    prism_doi = coredata.get('prism:doi', '')
    publisher = coredata.get('dc:publisher', '')
    publication_name = coredata.get('prism:publicationName', '')
    title = coredata.get('dc:title', '')
    
    # 10. Extract subject-area abbreviations
    subject_areas = response.get('subject-areas', {}).get('subject-area', [])
    subject_abbrev = [area.get('@abbrev', '') for area in subject_areas]
    
    # 11. Extract author full names
    authors = response.get('authors', {}).get('author', [])
    author_names = [f"{author.get('ce:given-name', '')} {author.get('ce:surname', '')}" for author in authors]
    
    def clean_null_value(v):
        return v if v is not None else 'No Data'

    # Combine all extracted fields into a dictionary
    record = {
        'date_sort': clean_null_value(date_sort_formatted),
        # 'countries': country_list,
        'abstracts': clean_null_value(abstracts),
        'ref_count': clean_null_value(ref_count),
        'affiliation_names': affiliation_names,
        'prism_doi': clean_null_value(prism_doi),
        'publisher': clean_null_value(publisher),
        'publication_name': clean_null_value(publication_name),
        'title': clean_null_value(title),
        'subject_abbrev': subject_abbrev,
        'author_names': author_names,
    }
    
    return record

def json_files_to_dataframe(json_file_paths, directory):
    list_scopus_data = []    
    for json_file_path in json_file_paths:
        full_file_path = directory + "\\" + json_file_path
        print(full_file_path)
        list_scopus_data.append(extract_fields_from_json(full_file_path))

    return list_scopus_data


def get_all_file_paths(directory):
    """
    Crawls through a directory and its subdirectories to collect all file paths.
    
    :param directory: The directory to crawl.
    :return: A list of file paths relative to the given directory.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            # Construct the relative file path
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            file_paths.append(relative_path)
    return file_paths


# Collect file path and store into a list
target_directory = os.path.abspath("..\\Project")
file_paths = get_all_file_paths(target_directory)

# Transform json to df
list_scopus_data = json_files_to_dataframe(file_paths, target_directory)
df = pd.DataFrame(list_scopus_data)

# Save df to csv file
output_csv_path = 'output.csv'
df.to_csv(output_csv_path, index=False)