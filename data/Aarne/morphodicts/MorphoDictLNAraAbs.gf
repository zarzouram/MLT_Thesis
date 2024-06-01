abstract MorphoDictLNAraAbs = Cat ** {
-- Although there is "mkLN : Str -> Gender -> LN", thr 'mkLN : N -> LN' is used
-- as there are situation where the location name in Noun construct may be
-- needed. Like in north_america_1_LN.
fun 'أمِيرِكا_N' : N ;
fun 'أُوْرُوبّا_N' : N ;
fun 'إِفْرِيقْيا_N' : N ;
fun 'مِصْر_N' : N ;
fun 'السُّوَيْد_N' : N ;
fun 'ستُوكْهُولم_N' : N ;

fun 'أمِيرِكا_LN' : LN ;
fun 'أُوْرُوبّا_LN' : LN ;
fun 'إِفْرِيقْيا_LN' : LN ;
fun 'مِصْر_LN' : LN ;
fun 'السُّوَيْد_LN' : LN ;
fun 'ستُوكْهُولم_LN' : LN ;
}