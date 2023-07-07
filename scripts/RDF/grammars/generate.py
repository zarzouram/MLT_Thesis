import pgf
# documented in https://www.grammaticalframework.org/doc/runtime-api.html#python


# produced by gf -make as in README
grammar_file = 'Properties.pgf'


mockup_facts = [
    ('P17', 'Q3392', 'Q79'),
    ('P17', 'Q175582', 'Q79')
    ]

gf_dict = {
  'P17': ['P17_Label_country_Fact', 'P17_located_in_Fact'],
  'Q3392': 'Q3392_Nile_Entity',
  'Q79': 'Qxxx_Egypt_Entity',
  'Q175582': 'Qxxx_pyramids_Entity'
  }

def generate(property, subject, object):
    Ps = gf_dict[property]
    X = pgf.Expr(gf_dict[subject], [])
    Y = pgf.Expr(gf_dict[object], [])
    return [pgf.Expr(P, [X, Y]) for P in Ps]


if __name__ == '__main__':
    grammar = pgf.readPGF(grammar_file)
    eng = grammar.languages['PropertiesEng']
    swe = grammar.languages['PropertiesSwe']
    for fact in mockup_facts:
        trees = generate(*fact)
        for tree in trees:
            print(tree)
            print(eng.linearize(tree))   
            print(swe.linearize(tree))   
