# WikiData Labels Universal Dependency Parsering Documentation

## Intorduction

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

## `scripts.parsers_m` Module

### Introduction

The `scripts.parsers_m` module provides a flexible and extensible way to parse Wikidata labels using Universal Dependency parsers. This module aims to abstract the parsing implementation details, making it easy to add new parser types in the future.

You can implement concrete classes for each parser type you want to use and then easily switch between them by passing the appropriate object to the WikiData class. There are two interface classes: `scripts.parsers_m.interfaces.LibraryParser` and `scripts.parsers_m.interfaces.RestAPIParser`. `RestAPIParser` is an interface class for UD parsers with a REST API-based, while `LibraryParser` is an interface class for UD parsers using a library. Both interface classes inherit from the abstract base class `AbstractUDParser`.

If the parser's implementation is a library, the new implementation should inherit from `LibraryParser.` On the other hand, if the parser's implementation is a REST API, the new implementation should inherit from `RestAPIParser`. The figure below shows the class relationships discussed above where there are two concrete classes; one uses the `Stanza` library for UD parsing, and the other use the `UDPipe` Rest API UD parser.

<img src="https://github.com/zarzouram/MLT_Thesis/blob/main/imgs/scripts_classes/classes_parsers.svg" width="100">
