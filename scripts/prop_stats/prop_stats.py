# %%
from IPython.display import display

import pandas as pd
import numpy as np

from pathlib import Path
from time import sleep
import requests
from tqdm.notebook import tqdm

from collections import Counter
import json
from wordcloud import WordCloud

from utills import get_prop_info, plot_hist

# %%
import matplotlib.pyplot as plt
# % matplotlib inline

# %%
prop_entity_api = 'https://www.wikidata.org/w/api.php?' \
    'action=wbgetclaims' \
    '&entity={}' \
    '&property={}' \
    '&format=json' \
    '&formatversion=2'

entity_labels_ar = 'https://www.wikidata.org/w/api.php?' \
    'action=wbgetentities' \
    '&format=json' \
    '&ids={}' \
    '&languages=ar|en' \
    '&props=labels' \
    '&formatversion=2'

USER_AGENT = {
    'User-Agent': 'A bot for get entities in Arabic. (guszarzmo@student.gu.se)'
}  # noqa:

# %%
prop_stats_dir = '../../outputs/prop_stats/wikibase-item_quantity_time/'
prop_stats_path = f'{prop_stats_dir}entities.parquet'
entities_info_path = f'{prop_stats_dir}entities_info.json'
conllu_dir = '../../outputs/conllu/wikibase-item_quantity_time/'
conllu_path = f'{conllu_dir}udp_en.conllu'

# %%
prop_dict = get_prop_info(conllu_path)
get_prop_label = lambda idx: prop_dict[idx]  # noqa: E731

# %%
prop_stats_df = pd.read_parquet(prop_stats_path)
prop_stats_df['prop_label'] = prop_stats_df['property_id'].apply(
    get_prop_label)

# %%
display(prop_stats_df)

# %%

no_entity = prop_stats_df['entity'].apply(lambda e: len(e)) == 0
no_entity_df = prop_stats_df[no_entity]

# %%
display(no_entity_df)

# %%
prop_stats_df = prop_stats_df[~no_entity]

# %%
prop_entity_df = prop_stats_df.explode('entity')

# %%
entities = prop_entity_df['entity'].unique()
print(len(entities))

# %%
if Path(entities_info_path).is_file():
    with open(entities_info_path, "r") as f:
        entities_info = json.load(f)
else:

    entities_chunks = np.array_split(entities, len(entities) // 49)
    entities_info = {}
    pbar = tqdm(total=len(entities_chunks))
    for i, entities_chunk in enumerate(entities_chunks):
        entities_str = '|'.join(entities_chunk)
        retry = True
        retries_num = 0
        failed_chunks = []
        while retry:
            try:
                response = requests.get(entity_labels_ar.format(entities_str),
                                        headers=USER_AGENT)
                if response.status_code == 200:
                    results = response.json()
                    if results.get('success', 0) == 1:
                        ents_dict = results['entities']
                        for ent_id, ent_dict in ents_dict.items():
                            labels_dict = ent_dict.get('labels', {})
                            if 'ar' in labels_dict and 'en' in labels_dict:
                                label_ar = labels_dict['ar']['value']
                                label_en = labels_dict['en']['value']
                            else:
                                label_ar = None
                                label_en = None
                            entities_info[ent_id] = {
                                'ar': label_ar,
                                'en': label_en
                            }
                        retry = False
                        retries_num = 0
                        pbar.update(1)
                        sleep(1)
                    else:
                        retries_num += 1
                        pbar.set_description(
                            f'API Call retuns No Sucess in chunk: {i}')
                        print(f'+ API Call retuns No Sucess in chunk: {i}')
                        sleep(120)
                else:
                    retries_num += 1
                    status = response.status_code
                    pbar.set_description(
                        f'API Call status is {status} in chunck: {i}')
                    print(f'- API Call status is {status} in chunck: {i}')
                    print(f'  {response.content}')
                    sleep(120)
            except ConnectionError:
                retries_num += 1
                pbar.set_description(f'Exception in chunck: {i}')
                print(f'(* Exception in chunck: {i}')
                with open(entities_info_path, "w") as f:
                    json.dump(entities_info, f)
                sleep(180)

                if retries_num >= 3:
                    retry = False
                    retries_num = 0
                    failed_chunks.append(i)

    with open(entities_info_path, "w") as f:
        json.dump(entities_info, f, indent=2)

# %%
entity_isar = lambda e: bool(entities_info[e]['ar'])  # noqa: E731
entity_label = lambda e: entities_info[e]['en']  # noqa: E731

# %%
prop_entity_df['ent_label'] = prop_entity_df['entity'].apply(entity_label)
prop_entity_df['isar'] = prop_entity_df['entity'].apply(entity_isar)

# %%
entities_count = prop_entity_df[['entity',
                                 'isar']].set_index('entity').value_counts()

# %%
display(entities_count)

# %%
entities_ar_count = entities_count[True]
entities_ar_percent = entities_ar_count / entities_count.sum()
print(f'Percentage of Arabic Entitirs: {entities_ar_percent:.2%}')

# %%
prop_entity_ar_df = prop_entity_df[prop_entity_df['isar']]
display(prop_entity_ar_df)

# %%
entities_ar_counter = Counter(prop_entity_ar_df['entity']).most_common()
entities_ar_count = np.array([count for _, count in entities_ar_counter])
print(f'Number of unique entities: {len(entities_ar_count)}')
print(f'Min count: {entities_ar_count.min()}')
print(f'Max count: {entities_ar_count.max()}')
print(f'Average Count: {entities_ar_count.mean().round(2)}')
print(f'Median Count: {np.median(entities_ar_count).round(2)}')
print(f'Count that >= 25% of counts: {np.percentile(entities_ar_count, 25)}')
print(f'Count that >= 75% of counts: {np.percentile(entities_ar_count, 75)}')
print(f'Count that >= 90% of counts: {np.percentile(entities_ar_count, 90)}')

# %%
entities_count = prop_entity_ar_df.groupby('property_id', as_index=False).agg(
    {'entity': list})
entities_count['entity_count'] = entities_count['entity'].apply(len)

display(entities_count)

# %%
title = 'Histogram of entity count per Wikidata property'
label_x = 'Entity Counts'
label_y = 'frequency'
label_hist = ["Entity Count"]
fig_data = {
    "label_h": label_hist,
    "xlabel": label_x,
    "ylabel": label_y,
    "title": title
}

bins = np.histogram_bin_edges(entities_count['entity_count'],
                              bins='auto').round()
_ = plot_hist([entities_count['entity_count'].to_numpy()],
              fig_data=fig_data,
              bins=[bins],
              count=True)

# %%
relevent_props_df = entities_count.copy()[
    entities_count['entity_count'] < bins[1]]
relevent_props_df['prop_label'] = relevent_props_df['property_id'].apply(
    get_prop_label)
display(relevent_props_df)

# %%
entities_ar_counter = Counter(
    relevent_props_df.explode('entity')['entity']).most_common()
entities_ar_count = np.array([count for _, count in entities_ar_counter])
print(f'Number of unique entities: {len(entities_ar_count)}')
print(f'Min count: {entities_ar_count.min()}')
print(f'Max count: {entities_ar_count.max()}')
print(f'Average Count: {entities_ar_count.mean().round(2)}')
print(f'Median Count: {np.median(entities_ar_count).round(2)}')
print(f'Count that >= 25% of counts: {np.percentile(entities_ar_count, 25)}')
print(f'Count that >= 75% of counts: {np.percentile(entities_ar_count, 75)}')
print(f'Count that >= 90% of counts: {np.percentile(entities_ar_count, 90)}')

# %%
title = 'Histogram of entity count in relevent Properties'
label_x = 'Entity Counts'
label_y = 'frequency'
label_hist = ["Entity Count"]
fig_data = {
    "label_h": label_hist,
    "xlabel": label_x,
    "ylabel": label_y,
    "title": title
}

_ = plot_hist([entities_ar_count],
              fig_data=fig_data,
              bins=[list(range(entities_ar_count.max() + 1))],
              count=True)

# %%
relevent_props_df['entity_count'].describe()
title = 'Histogram of entity count per relevent Properties'
label_x = 'Entity Counts'
label_y = 'frequency'
label_hist = ["Entity Count"]
fig_data = {
    "label_h": label_hist,
    "xlabel": label_x,
    "ylabel": label_y,
    "title": title
}

bins = np.histogram_bin_edges(relevent_props_df['entity_count'],
                              bins='auto').round()
_ = plot_hist([relevent_props_df['entity_count']],
              fig_data=fig_data,
              bins=[bins],
              count=True)

# %%
relevent_props_df[relevent_props_df['entity_count'] >= 169][[
    'property_id', 'prop_label'
]]

# %%
relevent_props_entity_df = relevent_props_df.explode('entity')
relevent_props_entity_df['ent_label'] = relevent_props_entity_df[
    'entity'].apply(entity_label)

# %%
labels_list = [
    '~'.join(label.strip().split())
    for label in relevent_props_entity_df['ent_label']
]

wordcloud = WordCloud(max_font_size=50, stopwords=[],
                      background_color="white").generate_from_frequencies(
                          Counter(labels_list))
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

# %%
labels_list = [
    '~'.join(label.strip().split())
    for label in relevent_props_entity_df['prop_label']
]

wordcloud = WordCloud(max_font_size=50, stopwords=[],
                      background_color="white").generate_from_frequencies(
                          Counter(labels_list))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# %%
labels_list = [
    '~'.join(label.strip().split()) for label in prop_entity_ar_df['ent_label']
]

wordcloud = WordCloud(max_font_size=50, stopwords=[],
                      background_color="white").generate_from_frequencies(
                          Counter(labels_list))
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

# %%
labels_list = [
    '~'.join(label.split()) for label in prop_entity_ar_df['prop_label']
]

wordcloud = WordCloud(max_font_size=50, stopwords=[],
                      background_color="white").generate_from_frequencies(
                          Counter(labels_list))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
# %%
