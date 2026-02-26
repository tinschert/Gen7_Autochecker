proc MyStartProc {key name args} {
    # Log "MyStartProc $key $name $args"
    switch $key {
      TestSeries      {
		SaveMode $TS::SaveMode
		}
      Group           { }
      TestRunGroup    { }
      TestRun         { }
    }
}



proc MyEndProc {key name args} {
    # Log "MyEndProc $key $name $args"
    switch $key {
      TestSeries      { }
      Group           { }
      TestRunGroup    { }
      TestRun {
	    # only evaluate criteria if simulation was successful so far
      	    if {[TestMgr::GetResult] != "good"} return

	    if {[catch {expr $TestMgr::Criteria} res]} {
		TestMgr::TestLog err "TestMgr: tcl error in criteria"
		Log "TestMgr: tcl error in criteria:\n$res"
		return
	    }
	    if {!$res} { 
	    	TestMgr::TestLog bad "criteria failed" 
	    }
      }
    }
}