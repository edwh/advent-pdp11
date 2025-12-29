MODULE Check;

(* Check command for MASTER *)

FROM BookLibrary IMPORT Keyboards,Bookings,NextArg,GetData,SaveData,OpenMode,
			NoOfPeriods,NoOfKeyboards,ARG;
FROM InOut IMPORT WriteString,WriteLn,WriteInt,Write;
FROM ModLibrary IMPORT ReadString;
FROM XConversion IMPORT StringToInt,Done;

VAR
	Keyboard,Loop,Period : INTEGER;
	S : ARRAY [0..10] OF CHAR;

BEGIN
	LOOP
	 IF NextArg(ARG,S)=FALSE THEN
	  WriteString('Keyboard >> ');
	  WriteLn;
	  ReadString(S);
	 END; (* IF *)
	 (* Get a keyboard. *)
	 StringToInt(S,Keyboard);
	 IF (Done=TRUE) THEN
	  FOR Loop:=1 TO NoOfKeyboards DO
	   IF Keyboards[Loop]=Keyboard THEN Keyboard:=Loop; EXIT; END;
	   (* If they typed a valid number then look for it in the list
	      of bookable keyboards. *)
	  END; (* FOR *)
	 END; (* IF *)
	END; (* LOOP *)
	(* Now we've got a keyboard number. *)
	GetData(1,ReadRegardless);
	(* Get today's bookings. *)
	WriteLn;
	WriteString('         1           2           3');
	WriteLn;
	WriteString('KB');
	WriteInt(Keyboards[Keyboard],2);
	FOR Period:=1 TO NoOfPeriods DO
	 IF Bookings[Period,Keyboard]=0 THEN
	  WriteString('     -      ');
	 ELSE
	  WriteString(' [');
	  WriteInt((Bookings[Period,Keyboard] DIV 256),3);
	  Write(',');
	  WriteInt((Bookings[Period,Keyboard] MOD 256),3);
	  WriteString(']  ');
	 END; (* IF *)
	END; (* FOR *)
	(* And write the bookings. *)
	WriteLn;
END Check.
