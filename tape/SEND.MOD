MODULE Send;

(*  Send command for MASTER *)

FROM BookLibrary IMPORT NextArg,ARG,Send,Keyboards,NoOfKeyboards;
FROM InOut IMPORT WriteString,WriteLn;
FROM ModLibrary IMPORT ReadString,LeftLen,ConvertToUpperCase,Len;
FROM XConversion IMPORT StringToInt,Done;
FROM ASCII IMPORT cr,lf;

VAR
	S,S1 : ARRAY [0..90] OF CHAR;
	CRLF : ARRAY [0..1] OF CHAR;
	KB : INTEGER;
	A,Loop : INTEGER;
	All : BOOLEAN;

BEGIN
	CRLF[0]:=cr;
	CRLF[1]:=lf;
	(* Set up newline characters. *)
	LOOP
	 IF NextArg(ARG,S)=FALSE THEN
	  WriteString('Keyboard >> ');
	  ReadString(S);
	  ConvertToUpperCase(S);
	  WriteLn;
	 END; (* IF *)
	 (* Have they specified a keyboard already ? *)
	 All:=LeftLen('ALL',S);
	 (* They can type a keyboard number or 'ALL' to send to all bookable
	     keyboards. *)
	 IF All=TRUE THEN EXIT; END;
	 (* We've got the spec. so exit. *)
	 StringToInt(S,A);
	 KB:=A;
	 IF Done=TRUE THEN
	  FOR Loop:=1 TO NoOfKeyboards DO
	   IF Keyboards[Loop]=KB THEN KB:=Loop; EXIT; END;
	   (* Convert what they typed into a number and try to convert that to
	      internal format. *)
	  END; (* FOR *)
	 END; (* IF *)
	END; (* LOOP *)
	IF Len(ARG)=0 THEN
	 WriteString('Message >> ');
	 ReadString(ARG);
	 WriteLn;
	END; (* IF *)
	(* Get the message. *)
	IF All=FALSE THEN
	 Send(KB,CRLF);
	 Send(KB,'Booker >> ');
	 Send(KB,ARG);
	 Send(KB,CRLF);
	 (* Send to specified keyboard. *)
	ELSE
	 FOR Loop:=1 TO NoOfKeyboards DO
	  KB:=Keyboards[Loop];
	  Send(KB,CRLF);
	  Send(KB,'Booker >> ');
	  Send(KB,ARG);
	  Send(KB,CRLF);
	 END; (* FOR *)
	 (* Or do the same for all bookable keyboards. *)
	END; (* IF *)
END Send.

