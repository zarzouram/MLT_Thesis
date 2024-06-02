# Regex to build linearizations/abstracts given a word entry and its word
    pl_n_regex = r'pl = "{1:}"'
    sg_n_regex = r'sg = "{1:}"'
    lin_n_ara_regex = (
        r"lin '{0:}_N' = mkN nohum (wmkN {{g = fem ; "
        + rf"{pl_n_regex} ; "
        + rf"{sg_n_regex} "
        + r"}}) ;\n"
    )
    lin_pn_ara_regex = r"lin '{0:}_{1:}' = mk{1:} '{0:}_{1:}' ;\n"
    abs_ara_regex = r"fun '{0:}_{1:}' : {1:} ;\n"