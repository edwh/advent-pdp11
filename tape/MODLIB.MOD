IMPLEMENTATION MODULE ModLibrary;

FROM RSTS IMPORT XRB,XRBType,XRBIndex,READ,KBFlush,FIRQB,FIRQBType,FIRQBIndex,
	         EXITRTS;
FROM SYSTEM IMPORT ADR,RSTSCALL;
FROM InOut IMPORT WriteString,WriteLn,WriteInt;

PROCEDURE ConvertToUpperCase ( VAR s : ARRAY OF CHAR);

VAR Loop : CARDINAL;

BEGIN
	FOR Loop:=0 TO HIGH(s) DO
	 IF (s[Loop]>=141C) AND (s[Loop]<=172C) THEN s[Loop]:=
	  CHR(ORD(s[Loop])-32); END;
	 (* If the character is lower case, then make it upper case. *)
	END; (* FOR *)
	(* And repeat for all the string. *)
END ConvertToUpperCase;

PROCEDURE Len(VAR s : ARRAY OF CHAR) : CARDINAL;

VAR Loop : CARDINAL;

BEGIN
	Loop:=0;
	WHILE (s[Loop]<>0C) AND (Loop<HIGH(s)) DO INC(Loop); END;
	RETURN Loop;
	(* Find end of string, either terminated by a null or by the end
	   of the array. *)
END Len;

PROCEDURE LeftLen( s : ARRAY OF CHAR;
		   VAR t : ARRAY OF CHAR) : BOOLEAN;

(* Checks for LEFT(s$,LEN(t$))=t$ *)

VAR Loop : CARDINAL;
    Flag : BOOLEAN;

BEGIN
	Flag:=TRUE;
	FOR Loop:=0 TO Len(t)-1 DO
	 IF s[Loop]<>t[Loop] THEN Flag:=FALSE; END;
	 (* Check for a difference in character. *)
	END; (* FOR *)
	RETURN Flag;
END LeftLen;

PROCEDURE ReadString ( VAR STR : ARRAY OF CHAR );

(* My own procedure to read in a string, as the library one does not
   allow you to turn of the echo.  Editing of the library routines is
   possible, but would be fairly extensive, as module RSTS would need
   changing.  Thus the RTS would need to be rebuilt, leading to two
   RTS's to avoid ?Wrong RTS message.  Too much effort. *)

(* Later - I tried editing the library.  Far too much effort, as the
   modules needed to be recompiled in the right order. *)

VAR
	Loop : CARDINAL;
	S : ARRAY [0..256] OF CHAR;

BEGIN
	KBFlush();
	(* Flush output buffer, in case of prompt. *)
	XRB[XRLEN]:=HIGH(STR); (* Maximum length to read *)
	XRB[XRBC]:=0;
	XRB[XRLOC]:=ADR(S);
	XRB[XRCI]:=0;
	XRB[XRBLK]:=0;
	XRB[XRTIME]:=0;
	XRB[XRMOD]:=0;
	RSTSCALL(READ);		(* Read into the array *)
	Loop:=0;
	LOOP
	 IF S[Loop]<' ' THEN EXIT; END;
	 STR[Loop]:=S[Loop];
	 INC(Loop);
	 IF Loop=HIGH(STR) THEN EXIT; END;
	END; (* LOOP *);
	(* Copy into parameter. *)
	STR[Loop]:=0C; (* Terminator *);
END ReadString;

PROCEDURE ClearFIRQB;

BEGIN
	FIRQB.cardinal[FQW0]:=0;
	FIRQB.cardinal[FQW1]:=0;
	FIRQB.cardinal[FQW2]:=0;
	FIRQB.cardinal[FQPPN]:=0;
	FIRQB.cardinal[FQNAM1]:=0;
	FIRQB.cardinal[FQNAM1A]:=0;
	FIRQB.cardinal[FQEXT]:=0;
	FIRQB.cardinal[FQSIZ]:=0;
	FIRQB.cardinal[FQBUFL]:=0;
	FIRQB.cardinal[FQMODE]:=0;
	FIRQB.cardinal[FQFLAG]:=0;
	FIRQB.cardinal[FQW13]:=0;
	FIRQB.cardinal[FQDEV]:=0;
	FIRQB.cardinal[FQUNIT]:=0;
	FIRQB.cardinal[FQCLUS]:=0;
	FIRQB.cardinal[FQNENT]:=0;
END ClearFIRQB;

PROCEDURE Exit;

BEGIN
  RSTSCALL(EXITRTS);
END Exit;

PROCEDURE NextArg ( VAR S,ARG : ARRAY OF CHAR) : BOOLEAN;

VAR
	Loop,Loop1 : CARDINAL;

BEGIN
	IF Len(S)=0 THEN RETURN FALSE ELSE
	Loop:=0;
	LOOP
	 IF (S[Loop]=' ') OR (S[Loop]=0C) THEN EXIT; END;
	 INC(Loop);
	 IF Loop>HIGH(S) THEN EXIT; END;
	END; (* LOOP *)
	IF Loop>HIGH(S) THEN Loop:=HIGH(S); END;
	(* Find a space if there is one. *)
	FOR Loop1:=0 TO (Loop-1) DO ARG[Loop1]:=S[Loop1]; END;
	(* Copy it across. *)
	ARG[Loop]:=0C;
	(* Terminator. *)
	FOR Loop1:=(Loop+1) TO HIGH(S) DO
	 S[Loop1-Loop-1]:=S[Loop1];
	 S[Loop1]:=0C;
	END; (* FOR *)
	(* Copy that across now. *)
	RETURN TRUE;
	END; (* IF *)
END NextArg;

END ModLibrary.
