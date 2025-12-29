MODULE List;

(* List command for MASTER. *)

FROM BookLibrary IMPORT Days,Bookings,GetData,ARG,NextArg,NoOfKeyboards,
			Keyboards,NoOfPeriods,OpenMode,SaveData;
FROM InOut IMPORT WriteString,WriteLn,WriteInt,Write;
FROM ModLibrary IMPORT ConvertToUpperCase,ReadString,Len,LeftLen;

VAR
	S : ARRAY [0..10] OF CHAR;
	Loop,Loop1,Day : INTEGER;

BEGIN
	LOOP
	 IF NextArg(ARG,S)=FALSE THEN
	  WriteString('Day <');
	  WriteString(Days[1]);
	  WriteString('> >> ');
	  ReadString(S);
	  IF Len(S)=0 THEN FOR Loop:=0 TO 8 DO S[Loop]:=Days[1,Loop]; END; END;
	  WriteLn;
	 END; (* IF *)
	 (* Ask for a day unless they have already given one. *)
	 ConvertToUpperCase(S);
	 FOR Loop:=1 TO 5 DO
	  IF LeftLen(Days[Loop],S)=TRUE THEN Day:=Loop; EXIT; END;
	  (* Look for a match. *)
	 END; (* FOR *)
	END; (* LOOP *)
	GetData(Day,ReadRegardless);
	WriteLn;
	WriteString('         1           2           3');
	WriteLn;
	FOR Loop:=1 TO NoOfKeyboards DO
	 WriteString('KB');
	 WriteInt(Keyboards[Loop],2);
	 FOR Loop1:=1 TO NoOfPeriods DO
	  IF Bookings[Loop1,Loop]=0 THEN WriteString('     -      ');
	  ELSE
	   WriteString(' [');
	   WriteInt((Bookings[Loop1,Loop] DIV 256),3);
	   Write(',');
	   WriteInt((Bookings[Loop1,Loop] MOD 256),3);
	   WriteString(']  ');
	  END; (* IF *)
	 END; (* FOR *)
	WriteLn;
	END; (* FOR *)
	WriteLn;
	(* Loop through and print it nicely. *)
	SaveData(FALSE);
END List.
