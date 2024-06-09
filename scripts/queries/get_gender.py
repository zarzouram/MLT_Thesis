# flake8: noqa

GN_GENDER_SPARQL_TEMPLATE = """SELECT ?givenName ?genderLabel  ?hasMaleAndFemale WHERE {
  VALUES ?givenName { QIDS_PLACEHOLDER } # Replace with your actual Q-identifiers
  ?givenName p:P31 ?statement .
  ?statement ps:P31 ?genderType .

  # Check for unisex given name
  OPTIONAL {
    ?givenName p:P31 ?unisexStatement .
    ?unisexStatement ps:P31 wd:Q3409032 .
    BIND("uni" AS ?unisexLabel)
  }

  # Check for female given name
  OPTIONAL {
    ?givenName p:P31 ?femaleStatement .
    ?femaleStatement ps:P31 wd:Q11879590 .
    BIND("fem" AS ?femaleLabel)
  }

  # Check for male given name
  OPTIONAL {
    ?givenName p:P31 ?maleStatement .
    ?maleStatement ps:P31 wd:Q12308941 .
    BIND("masc" AS ?maleLabel)
  }

  # Prioritize unisex, then male, then female
  BIND(COALESCE(?unisexLabel, ?maleLabel, ?femaleLabel) AS ?genderLabel)

  # Check if both male and female labels are bound and unisex is not
  BIND(IF(BOUND(?maleLabel) && BOUND(?femaleLabel) && !BOUND(?unisexLabel), "true", "false") AS ?hasMaleAndFemale)

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?givenName ?genderLabel ?hasMaleAndFemale
"""