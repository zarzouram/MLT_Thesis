from transphonator.phoneme.base_retriever import BasePhonemeRetriever
from transphonator.phoneme.cmu_retriever import CMURetriever
from transphonator.phoneme.g2p_retriever import G2pRetriever
from transphonator.pipeline.transliterator import TranslitPipeline
from transphonator.translit_maps.arabic_map import TranslitMapAra
from transphonator.translit_rules.arabic_rules import TranslitRuleAra
from transphonator.utils.paths import get_data_dir, process_args


def create_phoneme_retriever_ar(
    cmu_dict_path,
    fallback_dict_path=None,
) -> BasePhonemeRetriever:
    try:
        return G2pRetriever()
    except ImportError:
        return CMURetriever(
            cmu_dict_path, fallback_dict_path=fallback_dict_path
        )


if __name__ == "__main__":

    # Get data directory from arguments
    data_dir = process_args()
    cmu_dict_path, fallback_dict_path = get_data_dir(data_dir)

    # Step 1: Create Phoneme Retriever.
    phoneme_retriever_ar = create_phoneme_retriever_ar(
        cmu_dict_path, fallback_dict_path
    )

    # Step 2: Mapping list of phonemes to list of charachters.
    transliteration_map_ar = TranslitMapAra()

    # Step 3: Postprocessing the converted phonemes.
    transliteration_rules_ar = TranslitRuleAra()

    # Step 4: Create Pipeline.
    transliteration_pipline_ar = TranslitPipeline(
        phoneme_retriever_ar, transliteration_map_ar, transliteration_rules_ar
    )

    # Step 5: Run the pipeline.
    words = "Magdalena kristersson Naruhito Ulf this is".split()
    for word in words:
        print(word, transliteration_pipline_ar.transphonate(word))
