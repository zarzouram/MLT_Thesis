concrete MorphoDictLNAra of MorphoDictLNAraAbs = CatAra ** open ParadigmsAra in {
-- Although there is "mkLN : Str -> Gender -> LN", thr 'mkLN : N -> LN' is used
-- as there are situation where the location name in Noun construct may be
-- needed. Like in north_america_1_LN.
lin 'أمِيرِكا_N' = mkN nohum (wmkN { g = fem ; pl = "أمِيرِكا" ; sg = "أمِيرِكا" }) ;
lin 'أُوْرُوبّا_N' = mkN nohum (wmkN { g = fem ; pl = "أُوْرُوبّا" ; sg = "أُوْرُوبّا" }) ;
lin 'إِفْرِيقْيا_N' = mkN nohum (wmkN { g = fem ; pl = "إِفْرِيقْيا" ; sg = "إِفْرِيقْيا" }) ;
lin 'مِصْر_N' = mkN nohum (wmkN { g = fem ; pl = "مِصْر" ; sg = "مِصْر"}) ;
lin 'السُّوَيْد_N' = mkN nohum (wmkN { g = fem ; pl = "السُّوَيْد" ; sg = "السُّوَيْد"}) ;
lin 'ستُوكْهُولم_N' = mkN nohum  (wmkN { g = fem ; pl = "ستُوكْهُولم" ; sg = "ستُوكْهُولم"}) ;

lin 'أمِيرِكا_LN' = mkLN 'أمِيرِكا_N' ;
lin 'أُوْرُوبّا_LN' = mkLN 'أُوْرُوبّا_N' ;
lin 'إِفْرِيقْيا_LN' = mkLN 'إِفْرِيقْيا_N' ;
lin 'مِصْر_LN' = mkLN 'مِصْر_N' ;
lin 'السُّوَيْد_LN' = mkLN 'السُّوَيْد_N' ;
lin 'ستُوكْهُولم_LN' = mkLN 'ستُوكْهُولم_N' ;
}