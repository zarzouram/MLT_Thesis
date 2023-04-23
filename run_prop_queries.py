from scripts.prop_stats.property_queries import prop_blinks_query
from scripts.prop_stats.utills import get_prop_ids

CONLLU_PATH = './outputs/conllu/wikibase-item_quantity_time/udp_ar.conllu'
OUTPUT_DIR = './outputs/prop_stats/wikibase-item_quantity_time'
OUTPUT_FILE = f'{OUTPUT_DIR}/entities.parquet'

if __name__ == "__main__":
    prop_ids = get_prop_ids(CONLLU_PATH)
    prop_entities = prop_blinks_query(prop_ids, OUTPUT_FILE)
