abstract Properties = {

cat
  Fact ;
  Entity ;
--  SourceEntity ;
  
fun
  P1343_Label_described_by_source_Fact : Entity -> Entity -> Fact ;
  P1343_describes_Fact : Entity -> Entity -> Fact ;
  P1343_includes_descriptions_Fact : Entity -> Entity -> Fact ;

--  P17 : Entity -> Entity -> Fact ;
  P17_Label_country_Fact : Entity -> Entity -> Fact ;
  P17_located_in_Fact : Entity -> Entity -> Fact ;

  Q3392_Nile_Entity : Entity ;
  Qxxx_Nuttall_Encyclopedia_Entity : Entity ; -- SourceEntity ;

  Qxxx_Egypt_Entity : Entity ;
  Qxxx_pyramids_Entity : Entity ;
  
}