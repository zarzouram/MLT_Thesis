concrete MorphoDictPNAra of MorphoDictPNAraAbs = CatAra ** open ParadigmsAra in {
-- Construct Nouns for GN. To define it as human without gender.
-- Note that Human Names could have a plural form. However, here
-- sg==pl
-- N
lin 'آرثر_N' = mkN hum (wmkN {sg = "آرثر" ; pl = "آرثر"}) ;

-- SN
lin 'آرثر_sn_PN' = mkPN 'آرثر_N' ;  -- arthur_2_PN

-- GN
lin 'آرثر_PN' = mkPN "آرثر" masc hum ;  -- arthur_SN
lin 'بارت_PN' = mkPN "بارت" masc hum ;  -- bart_GN
}