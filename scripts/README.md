# WikiData Labels Universal Dependency Parsering Code Documentation

## 1. Intorduction

This project aims to parse Wikidata labels using different Universal Dependency
(UD) parsers. The project is divided into three modules:

  1. `scripts.parsers_m` defines classes responsible for parsing Wikidata
     labels using Universal Dependency parsers.

  2. `scripts.data_manipulation` defines classes that handle the conversion of
     parser output into the CoNLL-U format.

  3. Finally, `scripts.wiki_data` reads the Wikidata labels, then uses the
     parsers to parse the labels, and then uses the converters to convert the
     parser outputs to the CoNLL-U format. The output is then saved to a file.

Overall, the three modules work together to provide a complete pipeline for
parsing Wikidata labels.

## 2. The `scripts.parsers_m` Module

### 2.1. Introduction

The `scripts.parsers_m` module provides a flexible and extensible way to parse
Wikidata labels using Universal Dependency parsers. This module aims to
abstract the parsing implementation details, making it easy to add new parser
types in the future.

You can implement concrete classes for each parser type you want to use and
then easily switch between them by passing the appropriate object to the
WikiData class. There are two interface classes:
`scripts.parsers_m.interfaces.LibraryParser` and
`scripts.parsers_m.interfaces.RestAPIParser`. `RestAPIParser` is an interface
class for UD parsers with a REST API-based, while `LibraryParser` is an
interface class for UD parsers using a library. Both interface classes inherit
from the abstract base class `AbstractUDParser`.

If the parser's implementation is a library, the new implementation should
inherit from `LibraryParser.` On the other hand, if the parser's implementation
is a REST API, the new implementation should inherit from `RestAPIParser`. The
figure below shows the class relationships discussed above where there are two
concrete classes; one uses the `Stanza` library for UD parsing, and the other
use the `UDPipe` Rest API UD parser.

<img
src="https://github.com/zarzouram/MLT_Thesis/blob/main/imgs/scripts_classes/classes_parsers.svg"
width="70%">

### 2.2. `AbstractUDParser`

An abstract class serves as an interface for all UD Parser classes. It defines
two abstract methods: `parse` and `get_model_mapping`.

  1. `parse(self, texts: List[str], lang: str, params: Optional[dict]) -> Any`:
     This method takes a list of strings as input, along with a language code
     and an optional dictionary of the parser's parameters. It returns the
     output of the parsing process, which will vary based on the implementation
     in the concrete class.

  2. `get_model_mapping(self, lang: str) -> str`: This method takes a language
     code as input and returns the corresponding model name for the parser.

Two optional arguments are neede to initiate the respective class: `langs` and
`params`. `langs` is a list of language codes that the parser supports. The
`params` is a dictionary of parameters used to initiate the the corresponding
UD parser. The project configuration file defines the `langs` and the `params`
dictionary.

### 2.3. `RestAPIParser` and `LibraryParser`

Those are interface classes for UD parsers that are REST API-based and
library-based, inheriting from `AbstractUDParser`.  The `RestAPIParser` class
defines the URL property.

### 2.4. `UDPipeRestParser`

This concrete class implements the REST API for the `UDPipe` parser. It
inherits from the `RestAPIParser` class and implements the `parse` method.
`parse(self, texts: List[str], lang: str) -> str` method splits the list
of strings to avoid long request errors, then implements the parsing process
using the UDPipe REST API and returns the output in the CoNLL-U format as a
string.

There is no need to use the abstract method `get_model_mapping` as the
UDPipe accepts the language code as a model name.  The parameters of the UDPipe
are defined in the project's configuration file.

### 2.5. `StanzaParser`

This concrete class implements the UD parsing requirements using the `Stanza`
library. It inherits from LibraryParser and defines the `parse(self, texts:
List[str], lang: str) -> DoctDict` method. This method splits the list of
strings to avoid long request errors, then implements the parsing process using
the Stanza library and returns the output as a list of dictionary objects.

Two optional arguments initiate the class: `langs` and `params`. `langs` is a
list of language codes that the parser supports. The `params` is a dictionary
of parameters used to initiate the Stanza DU pipeline. The `max_len` attribute
represents the maximum length of the text to avoid memory errors when parsing
long texts.

The `__extract_lang_params` method is then called to extract the parameters for
each language. The project configuration file defines the parameters used to
initiate the respective parser. This method combines the common parameters, if
any, with the language-specific ones. If there are no common parameters, then
only the language-specific parameters are used.  Next, the `stanza.Pipeline`
method is called for each language in the langs list, initializing a Stanza UD
pipeline object for each language to parse the text. The `nlp` attribute is
then set to a dictionary where the keys are the language codes, and the values
are the corresponding pipeline objects.

## 3. The `scripts.data_manipulation` Module

### 3.1. Introduction

The `scripts.data_manipulation` module provides a flexible and extensible way
to convert the output from the UD parser native format to CoNLL-U formatted
string. This module aims to abstract the converting implementation details,
making it easy to add new parser types in the future.

You can implement concrete classes to convert the output of each parser type
you want to use. In this project, we used UDPipe Rest API and Stanza library
parser. Thus, this module contains two concrete implementation classes:
`UDPipeConverters` and `StanzaConverters`. Both classes inherit from the
ParsersOutputConverter abstract class. The figure below shows the class
relationships discussed earlier.

The module is responsible for converting the output of the parsing process to
CoNLL-U format with the Wikidata entities linked by their indices.

<img
src="https://github.com/zarzouram/MLT_Thesis/blob/8bac9b9c1e23e4aa094dcc4f090fbc4218048b27/imgs/scripts_classes/classes_converters.svg"
width="100%">

### 3.2. `ParsersOutputConverter`

The ParsersOutputConverter abstract class provides a basic framework for
converting data to the Conll-U format. The class contains a single abstract
method, `convert`, which takes the parsed labels in the parser's native format
to be converted to Conll-u. The method receives three parameters: `data`: The
parsed labels to be converted to Conll-u from the parser's native format.
`labels`: a List of Wikidata labels texts.  `idxs`: a List of Wikidata ids for
entities labels to be replaced with the sentence indices produced by the UD
parser.

### 3.3. `UDPipeConverters Class`

The `UDPipeConverters` class inherits from the `ParsersOutputConverter`
abstract class. It implements the convert method and an additional helper
method called `write2desk`.

As discussed above, the `convert` method receives three parameters (the parsed
labels, Wikidata labels, and Wikidata ids). The parsed labels are already in
the Conll-U string format. The method replaces the sentence indices generated
by UDPipe with the Wikidata ids.

The write2desk method takes the data, file path, and mode and writes the
converted data to the desk.  StanzaConverters Class The StanzaConverters class
inherits from the ParsersOutputConverter abstract class. It implements the
convert method and an additional helper method called `write2desk`.

As discussed above, the `convert` method receives three parameters (the parsed
labels, Wikidata labels, and Wikidata ids). However, the parsed labels are a
list of dictionaries, where each dictionary corresponds to a token and its
features. The convert method iterates over the list of dictionaries and builds
a string in the CoNLL-U format, where each line represents a token and its
features. Finally, the method appends a blank line to the output to indicate
the end of the sentence.

The write2desk method takes the data, file path, and mode and writes the
converted data to the desk.

## 4. The WikiData module

The WikiData class is used to read, parse, manipulate, and save Wikidata.

The class initializer takes a path to the Wikidata file, a list of 
language codes to be extracted, and a callable function to read the data 
from the file. The callable function must return the data in a dictionary, 
keyed with the Wikidata entity's labels and language codes. Any missing entity 
label in any language must be `None`; see the example below. The data 
attribute of the class is the read function output.

```python
data = {
    'idx': ['P1', 'P2', 'P3', 'P4'],
    'en': ['instance of', 'country', 'capital', 'currency'],
    'ar': ['عملة' ,'عاصمة' ,'دولة' ,'نوع من الأشياء'],
    'ja': ['インスタンス・オブ', None, '首都', '通貨'],
    'es': ['instancia de', 'país', None, 'moneda']
    }
```

The class has the `parse_data` method  used to parse the WikiData labels, read
during class initialization, and has the following arguments:

  1. `parser_obj`: An instance of the `AbstractUDParser` class that is
     responsible for parsing the WikiData labels.

  2. `converter_obj`: An instance of the `ParsersOutputProcessor` class
     responsible for processing the parsed data in the native parser format and
     converting it to Conll-U

  3. `params`: A dictionary of parameters that parser_obj uses.

  4. `langs`: A list of language codes to be extracted from WikiData.

  5. `write_output`: tuple of a file path and a mode.

The `parse` method parses the Wikidata labels for each language in the `langs`
argument using an instance of the `AbstractUDParser` and an instance of the
`ParsersOutputConverter` class for parsing, converting processes we discussed
above. If the `write_output` parameter is passed, the method will write the
parsed data to a file in the CoNLL-U format. The the Figure below.

The `__filter_none` method removes None records from the data for each
language. It returns a dictionary containing only the index and label pairs
that are None.

<img
src="https://github.com/zarzouram/MLT_Thesis/blob/137ba5ca0fcde024c0f73da12b4ae3f079efa1cf/imgs/scripts_classes/classes_WikiData.svg"
width="100%">
