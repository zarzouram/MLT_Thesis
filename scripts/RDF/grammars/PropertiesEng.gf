concrete PropertiesEng of Properties = open
  SyntaxEng,
  ParadigmsEng

in {

lincat
  Fact = Cl ;
  Entity = NP ;
--  SourceEntity = NP ;
  
lin
  P1343_Label_described_by_source_Fact X Y = mkCl X (passiveVP (mkV2 (mkV "describe")) Y) ;
  P1343_describes_Fact X Y = mkCl Y (mkV2 (mkV "describe")) X ;
--  P1343_includes_descriptions_Fact : Entity -> Entity -> Fact ;

  P17_Label_country_Fact X Y = mkCl (mkNP the_Det (mkCN (mkN "country") (SyntaxEng.mkAdv possess_Prep X))) Y ;
  P17_located_in_Fact X Y = mkCl X (mkAP (mkA2 "located" in_Prep) Y) ;

  Q3392_Nile_Entity = mkNP the_Det (mkN "Nile") ;
  Qxxx_Nuttall_Encyclopedia_Entity = mkNP the_Det (mkN "Nuttall Encyclopedia") ;

  Qxxx_Egypt_Entity = mkNP (mkPN "Egypt") ;
  Qxxx_pyramids_Entity = mkNP thePl_Det (mkN "pyramid") ;
}