# Building Arabic Lexical Database

- [1. Introduction](#1-introduction)
- [2. Step-1: Compiling Noun and Adjective Lists](#2-step-1-compiling-noun-and-adjective-lists)
  - [2.1. Datastructure](#21-datastructure)
    - [2.1.1. `ism_ar.IsmDict`](#211-ism_arismdict)
    - [2.1.2. `ism_ar.Ism`](#212-ism_arism)
  - [2.2. Extracting Nouns and Adjectives](#22-extracting-nouns-and-adjectives)
  - [2.3. Output](#23-output)
  - [2.4. Important note about the count](#24-important-note-about-the-count)
- [3. Step-2: Parsing Wiktionary](#3-step-2-parsing-wiktionary)
  - [3.1. Output](#31-output)
    - [3.1.1. Nouns](#311-nouns)
    - [3.1.2. Adjectives](#312-adjectives)
    - [3.1.3. X words](#313-x-words)
- [4. Step-4 Building the Lexical Database](#4-step-4-building-the-lexical-database)
  - [4.1. Output](#41-output)
    - [4.1.1. Nouns](#411-nouns)

---

## 1. Introduction

Here, I will build an Arabic Lexical Database for nouns and adjectives tokens
identified by UDPipe while parsing WikiData properties labels.  Each entry in
the database will have the broken plural forms, gender, and species properties.

The process of building this database involves the following:

 1. compiling a list of Arabic nouns and adjectives from the Conll-U file
 2. using Wiktionary, the respective broken plural form(s) are collected. Salem
    plurals are easily inflected so it will not saved.
    1. In addition, the lemma, POS, and gender for each entry will be collected
    from Wiktionary and compared with what is identified by the UDPipe.

    **Question: How to deal with Discrepancies? see section ##**

 3. It is expected that some entries will be missed from the Wiktionary.  Thus,
    another source may be used.

 4. Build the Lexical Database using data extracted above.

## 2. Step-1: Compiling Noun and Adjective Lists

**Nouns and adjectives are extracted from the Conll-U file in
[`extract_asmaa_ar.ipynb`](extract_asmaa_ar.ipynb) notebook** and saved in a
speciall data dictionary `IsmDict` that are keyed with `Ism` objects that
represent each entry. Both classes are implemented in `ism_ar.py`

### 2.1. Datastructure

#### 2.1.1. `ism_ar.IsmDict`

`IsmDict` is a subclass of a python dictionary used to save the extracted Nouns
and adjectives keys and the respective list tuple of label ids and label texts.

An Example of `Ism Dict` that has one object of `ism` may be:

    ```python
        {Ism(form='رئيس',lemma='رَئِيس'): [('P6', 'رئيس الحكومة'),
            ('P210', 'ممثل رئيس الحزب'),
            ('P2388', 'منصب رئيس هذه المنظمة'),
            ('P5440', 'معرف رئيس في رئاسة الجمهورية الفرنسية'),
            ('P5769', 'رئيس التحرير')]
        }
    ```

When a key is set in the dictionary, the class checks whether the key already
exists in the dictionary. If it does, it updates the existing key by merging
its plural with the new key's plural and adding value to the current value(s).
Otherwise, it adds the plural to the dictionary as is. Comparing two objects of
`Ism`s is implemented in =`Ism` Class.

#### 2.1.2. `ism_ar.Ism`

`Ism` represents an Arabic noun and adjective we need to extract. It has
attributes such as `form`, `lemma`, `upos`, `root`, `gender`, `species`, and
`plurals`. The attribute `has_salem_pl` identifies if the object of Ism has a
Salem plural form.

`Ism` also has methods for updating the plural and comparing two instances of
the class. The **eq** () method **compares two instances of Ism for equality
based on their form and lemma**, the **hash** () the method returns a hash
value for an instance of the class based on its form and lemma.

### 2.2. Extracting Nouns and Adjectives

`get_noun_adj_conllu` extracts information about nouns, adjectives, and X items
from a CoNLL-U formatted file.

The function creates three `IsmDict` objects to store information about nouns,
adjectives, and X items. **Unfortunately, some tokens generated by UDPipe are
not Arabic words. If such words are detected, the function skips them**.

If the token is a plural noun, the function uses the `process_plural` function
to get its singular form and gender. The function tries to detect if the word
is a Salem plural. If so, the single form is inferred, and the
`get_noun_adj_conllu` sets the attribute `has_salem_pl` in the respective `Ism`
object. If the word is not Salem plural, it is added to a dictionary of
suspected plural forms.

### 2.3. Output

There are:

- 2654 nouns
- 1545 adjectives
- 2940 tokens that cannot be assigned a real UPOS.

In addition, 626 broken plural words are found.

Moreover:

- 170 out of 2654 nouns are Salem plural
- 44 out of 1545 adjetives are Salem plural

The code writes the extracted nouns, adjectivess, X words, and plural words to
a binary file using the pickle.dump() function. The output file can be found
under the [lexicons_ar folder](../../outputs/lexicons_ar/) with name of
'asmaa.pkl'.

### 2.4. Important note about the count

Two Isms objects are considered the same if they have the same lemma and the
same form. Thus, some tokens may be actually repeated because:

  1. The UDPipe generates different lemma for the same word. For example, the
     word `معرف` but the UDPipe gives it four diffeent lemmas.
  2. Two similar word but one has the definite article prefix 'al-'

## 3. Step-2: Parsing Wiktionary

In this step, for each extracted word in step-1 the parsed wikitext data is
retrieved from the English Wiktionary API. **The respective code can be found in
[`parse_wikitionary_wikitext.ipynb`](.parse_wikitionary_wikitext.ipynb)**

The `get_parsed_data` function get the parsed wikitext from the English
Wiktionary API. It first tries to lookup the word by using the word form. If the
word is found, it returns the parsed wikitext data for the Arabic section. If
the word is not found, it tries to look up the word by using its lemma. If the
word is found, it returns the parsed wikitext data for the Arabic section. If
the word is not found, it returns a Status object indicating the reason why the
word could not be found.

### 3.1. Output

#### 3.1.1. Nouns

Out of 2654 nouns:

- 2107 words are found and have an Arabic section in the parsed wikitext.
- 44 words are found but does not have an Arabic section in the parsed wikitext.
- 503 words are not found

#### 3.1.2. Adjectives

Out of 1545 ajectives:

- 975 words are found and have an Arabic section in the parsed wikitext.
- 20 words are found but does not have an Arabic section in the parsed wikitext.
- 550 words are not found

#### 3.1.3. X words

For X words, out of 2940 tokens:

- 661 words are found and have an Arabic section in the parsed wikitext.
- 89 words are found but does not have an Arabic section in the parsed wikitext.
- 2190 words are found

The code writes the extracted wikitext for each nouns, adjectivess, and X words to
a binary file using the pickle.dump() function. 2e can be found
under the [wikitionary_ar](../../outputs/lexicons_ar/wikitionary_ar/) with the
following names:

- `nouns_wikitionary.pkl`
- `adjectives_wikitionary.pkl`
- `X_wikitionary.pkl`

## 4. Step-4 Building the Lexical Database

**In [`build_lexicon_ar.ipynb`](build_lexicon_ar.ipynb) notebook, I am goung to
build the datbase for the Nouns, adjectives and X words from the parsed
wikitext extracted from step-2**. In addition, I will check the discrepancies
between the features of the Arabic words extracted from the Wikitext and the
Conll-U files.

The code uses regular expression to:

  1. first extract the Noun or Adjective sections from the wikitext. The
     respective section should have a header of either `===Noun===` (with
     three equal signs) or `====Noun====` (with four equal signs).

  2. Then after extracting the required section, a set of regular expressions
     are used to extract the the template that has the information we looks
     for.Examples of these templates are:

       - {{ar-noun|نِقابة|head2=نَقابة|f|pl=نِقَابَات|pl2=نَقَابَات}}
       - {{ar-decl-noun|حُكُومَة|pl=حُكُومَات}}
       - {{ar-decl-coll-noun|سَحَاب|pl=سُحُب}}
       - {{ar-decl-gendered-noun|رَئِيس|pl=رُؤَسَاء}}
       - {{ar-decl-sing-noun|شَجَرَة|pl=أَشْجَار}}

  3. After extracting the required template, a set of regular expressions are
     used to extract the following features from the template:

       - **lemma**: the lemma extracted from the template are compared with what is
         found in the Conll-U file. Because the diacritics (short vowels /
         tashkeel) may be different for the same word, the `pyarabic` are used
         for this purpose.
       - **gender**: the lemma extracted from the template are compared with what is
         found in the Conll-U file.
       - **plural forms**

### 4.1. Output

#### 4.1.1. Nouns

As we can see from the table below, out of 2107 nouns found in Wiktionary, 1441
nouns are found in the Noun section. However, 38 words are identified as
adjectives in the Wiktionary and 628 are neithwe noun nor adjectives.

| POS extracted from Wikitext | count |
| ---                         | ---   |
| Noun                        | 1441  |
| Adjective                   | 38    |
| Neither noun nor Adjectives | 628   |

Also, 178 nouns has discrepancies in lemma, and 32 nouns has discrepancies in gender.