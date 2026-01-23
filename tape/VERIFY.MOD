MODULE Verify;

(* Verify command for MASTER *)

FROM BookLibrary IMPORT Legality,GetPeriod,GetData,SaveData,OpenMode,
			CheckLegality,NextArg,Send,Kill,NoOfKeyboards,Keyboards,
			ARG,Bookings;
FROM InOut IMPORT WriteString,WriteLn,WriteInt,Write;
FROM ModLibrary IMPORT ReadString,Len,LeftLen;
FROM XConversion IMPORT StringToInt,Done;
FROM Conversions IMPORT IntegerToString;
FROM RAD50 IMPORT RAD50ToString;
FROM ASCII IMPORT cr,lf;

VAR
	Kb,Kb1,Loop : INTEGER;
	KB : ARRAY [0..10] OF CHAR;

PROCEDURE DoVerify ( KB : INTEGER);

VAR
	Period,Job,Who,Where,What1,What2 : CARDINAL;
	Status : Legality;
	S : ARRAY [0..3] OF CHAR;
	S1 : ARRAY [0..88] OF CHAR;
	S2 : ARRAY [0..88] OF CHAR;
	Loop,Loop1 : INTEGER;
	CRLF : ARRAY [0..1] OF CHAR;

BEGIN
	CRLF[0]:=cr;
	CRLF[1]:=lf;
	Period:=GetPeriod();
	IF Period=0 THEN Period:=1; END;
	(* Get current bookings period. *)
	LOOP
	 Status:=CheckLegality(KB,Period,Job,Who,Where,What1,What2);
	 (* Find out the status of that keyboard. *)
	 CASE Status OF
	   Legal : EXIT;
	 | FreeTerminal : WriteLn; WriteString('Free Terminal');
	 | Illegal : WriteLn; WriteString('Illegal - booked for [');
		     WriteInt((Bookings[Period,KB] DIV 256),3);
		     Write(',');
		     WriteInt((Bookings[Period,KB] MOD 256),3);
		     WriteString('].');
	 END; (* CASE *)
	 (* Write the appropriate message. *)
	 WriteLn;
	 WriteString('Job   Who   Where  What');
	 WriteLn;
	 WriteInt(Job,2);
	 Write(' ');
	 WriteInt((Who DIV 256),3);
	 Write(',');
	 WriteInt((Who MOD 256),3);
	 WriteString('  KB');
	 WriteInt(Where,2);
	 WriteString('  ');
	 RAD50ToString(What1,S);
	 WriteString(S);
	 RAD50ToString(What2,S);
	 WriteString(S);
	 WriteLn;
	 (* Display the short job status. *)
	 WriteLn;
	 WriteString('Option >> ');
	 ReadString(S);
	 IF Len(S)=0 THEN IntegerToString(3,0,S); END;
	 (* Default option is 3. *)
	 StringToInt(S,Loop);
	 IF (Done=TRUE) AND (Loop>0) AND (Loop<4) THEN
	  CASE Loop OF
	    1 : Kill(Job); Send(Where,CRLF); Send(Where,
	        'Booker >> You have been killed for running illegally.');
		Send(Where,CRLF);
		EXIT;
	  | 2 : WriteLn; WriteString('Message >> ');
		FOR Loop1:=0 TO 88 DO S1[Loop1]:=0C; END;
	        ReadString(S1);
	        S2:='Booker >> ';
	        FOR Loop1:=0 TO 78 DO S2[Loop1+10]:=S1[Loop1]; END;
		Send(Where,CRLF);
	        Send(Where,S2);
		Send(Where,CRLF);
	  | 3 : EXIT;
	  END; (* CASE *)
	  (* Get the option and do the appropriate thing if it's legal. *)
	 ELSE
	  WriteLn;
	  WriteString('Valid options are 1) Kill job 2) Send message ');
	  WriteString('3) Do nothing (Default)');
	  WriteLn;
	  WriteLn;
	 END; (* IF *)
	 (* Otherwise tell them the valid options. *)
	END; (* LOOP *)
END DoVerify;

BEGIN
	GetData(1,ReadRegardless);
	(* Get today's data. *)
	IF NextArg(ARG,KB)=TRUE THEN
	 StringToInt(KB,Kb);
	 IF Done=FALSE THEN WriteLn; WriteString('?Please supply a number.');
	  WriteLn;
	 ELSE
	  Kb1:=0;
	  FOR Loop:=1 TO NoOfKeyboards DO
	   IF Keyboards[Loop]=Kb THEN
	    Kb1:=Loop;
	   END; (* IF *)
	  END; (* FOR *)
	  IF Kb1=0 THEN WriteLn; WriteString('?Not a BOOKable keyboard.');
	   WriteLn;
	  ELSE
	   DoVerify(Kb1);
	  END; (* IF *)
	 END; (* IF *)
	 (* If they specified a keyboard then check it and do a verify *)
	ELSE
	 FOR Loop:=1 TO NoOfKeyboards DO DoVerify(Loop); END;
	END; (* IF *)
	(* Otherwise the verify consists of all bookable keyboards. *)
	SaveData(FALSE);
	(* Close the file. *)
END Verify.
