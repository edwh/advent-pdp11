MODULE Delete;

(* Delete command for MASTER *)

FROM BookLibrary IMPORT Days,Bookings,GetData,OpenMode,ARG,NextArg,
			NoOfKeyboards,NoOfPeriods,SaveData,Keyboards;
FROM InOut IMPORT WriteString,WriteLn,WriteInt,Write;
FROM ModLibrary IMPORT ConvertToUpperCase,ReadString,Len,LeftLen;
FROM XConversion IMPORT Done,StringToInt;

VAR
	Day : ARRAY [0..10] OF CHAR;
	Loop : INTEGER;
	DDay : INTEGER;
	S : ARRAY [0..10] OF CHAR;
	Period : INTEGER;
	Keyboard : INTEGER;

BEGIN
	LOOP
	 IF NextArg(ARG,Day)=FALSE THEN
	  WriteString('Day >> ');
	  ReadString(Day);
	  WriteLn;
	 END; (* IF *)
	 (* Did they specify a day ? *)
	 ConvertToUpperCase(Day);
	 FOR Loop:=1 TO 5 DO IF LeftLen(Days[Loop],Day)=TRUE THEN
	  DDay:=Loop; EXIT; END;
	 (* Try to find a day match. *)
	 END; (* FOR *)
	END; (* LOOP *)
	(* Now we've got a day. *)
	LOOP
	 IF NextArg(ARG,S)=FALSE THEN
	  WriteString('Period >> ');
	  ReadString(S);
	  WriteLn;
	 END; (* IF *)
	 (* Period ? *)
	 StringToInt(S,Period);
	 IF (Done=TRUE) AND (Period<=NoOfPeriods) AND (Period>0) THEN
	  EXIT; END;
	 (* Check the period. *)
	END; (* LOOP *)
	LOOP
	 IF NextArg(ARG,S)=FALSE THEN
	  WriteString('Keyboard >> ');
	  ReadString(S);
	  WriteLn;
	 END; (* IF *)
	 (* Keyboard ? *)
	 StringToInt(S,Keyboard);
	 IF Done=TRUE THEN
	  FOR Loop:=1 TO NoOfKeyboards DO
	   IF Keyboards[Loop]=Keyboard THEN EXIT; END;
	   (* Look for match in the list. *)
	  END; (* FOR *)
	 END; (* IF *)
	END; (* LOOP *)
	GetData(DDay,ReadWrite);
	IF Bookings[Period,Keyboard]=0 THEN
	 WriteString('?This space is free.');
	 WriteLn;
	ELSE
	 WriteString('Really delete booking for [');
	 WriteInt((Bookings[Period,Keyboard] DIV 256),3);
	 Write(',');
	 WriteInt((Bookings[Period,Keyboard] MOD 256),3);
	 WriteString('] <NO> ? ');
	 ReadString(S);
	 IF Len(S)=0 THEN S:='NO'; END;
	 ConvertToUpperCase(S);
	 IF LeftLen('YES',S)=TRUE THEN Bookings[Period,Keyboard]:=0;
	 WriteLn;
	 WriteString('Deleted OK.');
	 WriteLn;
	 END; (* IF *)
	END; (* IF *)
	(* Make sure. *)
	SaveData(TRUE);
END Delete.
