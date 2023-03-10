# WikiData Labels Universal Dependency Parsering Documentation

## 1. Intorduction

This project aims to parse Wikidata labels using different Universal Dependency
(UD) parsers. The project is divided into three modules:

  1. `scripts.parsers_m` defines classes responsible for parsing Wikidata
     labels using Universal Dependency parsers.

  2. `scripts.data_manipulation` defines classes that handle the conversion of
     parser output into the CoNLL-U format. The second module,

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
width="70">

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
UD parser. The project configuration file defines the `params` dictionary.

### 2.3. `RestAPIParser` and `LibraryParser`

Those are interface classes for UD parsers that are REST API-based and
library-based, inheriting from `AbstractUDParser`.  The `RestAPIParser` class
defines the URL property.

### 2.4. `UDPipeRestParser`

This concrete class implements the REST API for the `UDPipe` parser. It
inherits from the `RestAPIParser` class and implements the `parse` method.
`parse(self, texts: List[str], lang: str) -> str`: This method splits the list
of strings to avoid long request errors, then implements the parsing process
using the UDPipe REST API and returns the output in the CoNLL-U format as a
string.  There is no need to use the abstract method `get_model_mapping` as the
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
of parameters used to initiate the Stanza DU pipeline. The `max_len` attribute represents the maximum length of the text to avoid
memory errors when parsing long texts.

The `__extract_lang_params` method is then called to extract the parameters for
each language. The project configuration file defines the parameters used to
initiate the respective parser. This method combines the common parameters, if
any, with the language-specific ones. If there are no common parameters, then
only the language-specific parameters are used.  Next, the `stanza.Pipeline`
method is called for each language in the langs list, initializing a Stanza UD
pipeline object for each language to parse the text. The `nlp` attribute is
then set to a dictionary where the keys are the language codes, and the values
are the corresponding pipeline objects.

# The `scripts.data_manipulation` Module

