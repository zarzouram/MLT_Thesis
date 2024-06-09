concrete MorphoDictPNAra of MorphoDictPNAraAbs = CatAra ** open ParadigmsAra in {
-- Construct Nouns for SN. To define it as human without gender.
-- Note that Human Names could have a plural form. However, here
-- sg==pl
-- N (SN)
lin 'آرثر_sn_N' = mkN hum (wmkN {sg = "آرثر" ; pl = "آرثر"}) ;

-- SN
lin 'آرثر_sn_PN' = mkPN 'آرثر_sn_N' ;  -- arthur_2_PN

-- GN
lin 'آرثر_gn_PN' = mkPN "آرثر" masc hum ;  -- arthur_SN
lin 'بارت_gn_PN' = mkPN "بارت" masc hum ;  -- bart_GN
}