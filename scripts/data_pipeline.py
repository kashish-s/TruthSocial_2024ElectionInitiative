import pandas as pd
import os
from datetime import datetime
import json
import ast



persistent_folder = 'path_to_persistent_scrapes'
dynamic_folder = 'path_to_trending_scrapes'


def compile_data_for_keywords(folder):

    data = pd.DataFrame()
    files =  os.listdir(folder)
    for f in files:
        print('processing ',f)
        curr_date = f.split('_')[1][:-4]
        print(curr_date)
        cur_date = datetime.strptime(curr_date,'%Y-%m-%d')
        #then concantenate it
        keyword, date_str = f.split('_')
        date_str = date_str.split('.')[0]

        df = pd.read_csv(folder+'/'+f, sep='\t')

        df['Keyword'] = [keyword]*len(df)
        df['Scraping Date'] = [date_str]*len(df)
        data = pd.concat([data,df], ignore_index=True)

        data_unique = data.drop_duplicates(subset=['url', 'external_id', 'author_username', 'associated_tags',
            'tagged_accounts', 'status_links', 'media_urls', 'like_count',
            'reply_count', 'retruth_count', 'is_quote', 'is_retruth', 'is_reply',
            'replying_to', 'status', 'Keyword'])

    return data_unique


persistent_df = compile_data_for_keywords(persistent_folder)
dynamic_df = compile_data_for_keywords(dynamic_folder)

concatenated_data = pd.concat([persistent_df,dynamic_df],ignore_index=True)
concat_data_unique = concatenated_data.drop_duplicates(subset=['url', 'external_id', 'author_username', 'associated_tags',
                'tagged_accounts', 'status_links', 'media_urls', 'like_count',
                'reply_count', 'retruth_count', 'is_quote', 'is_retruth', 'is_reply',
                'replying_to', 'status', 'Keyword'])

#fix column data types, map keywords

concat_data_unique['associated_tags'] = concat_data_unique['associated_tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
concat_data_unique['tagged_accounts'] = concat_data_unique['tagged_accounts'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
concat_data_unique['replying_to'] = concat_data_unique['replying_to'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

with open('FINAL_MEMO/scripts.py/keyword_mappings.json', 'r') as json_file:
    mapping = json.load(json_file)

concat_data_unique['Keyword'] = concat_data_unique['Keyword'].apply(lambda x:mapping[x] if x in mapping else x)

concat_data_unique.to_csv('path_to_output_file.csv')
