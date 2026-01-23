IMPLEMENTATION MODULE BookLibrary;

FROM InOut IMPORT WriteString,WriteLn,WriteInt,Write;
FROM RSTSFiles IMPORT FILE,Create,Lookup,ReadBlock,WriteBlock,Close;
FROM RSTS IMPORT
    CALFIP, CLSFQ, OPNFQ, CREFQ, DLNFQ, RENFQ, DIRFQ, UUOFQ,
            ERRFQ, RSTFQ, LOKFQ, ASSFQ, DEAFQ, DALFQ, CRTFQ, CRBFQ,
    PLAS, ATRFQ, DTRFQ, CRAFQ, ELAFQ, MAPFQ, UMPFQ,
    UUO, UUACT, UUASS, UUATR, UUATT, UUBCK, UUBYE, UUCCL, UUCHE,
	 UUCHU, UUCLN, UUCNV, UUDAL, UUDAT, UUDEA, UUDET, UUDIE,
	 UUDIR, UUDLU, UUDMP, UUERR, UUFCB, UUFIL, UUHNG, UUJOB,
	 UULIN, UULOG, UULOK, UUMNT, UUNAM, UUNLG, UUPAS, UUPOK,
	 UUPPN, UUPRI, UURAD, UURTS, UUSLN, UUSPL, UUSWP, UUSYS,
	 UUTB1, UUTB2, UUTB3, UUTRM, UUYLG, UUZER,
    READ, WRITE, CORE, SLEEP, PEEK, SPEC, 
    TTAPE, TTECH, TTNCH, TTDDT, TTRST,
    POSTN, SETKEY, STAT, RUN, NAME, EXITRTS, 
    RTS, ERLOG, LOGS, CLEARKEY, MESAG, CCL, FSS, CHAIN, RSX, ULOG,

    Keyword, ErrorByte, FIRQB, XRB, CoreCommon,

    JobStatus, JobNumber, CurrentPPN,
    GetCoreCommon, PutCoreCommon,
    Chain, EntryPoint, Detach, ReAttach, 
    DropTempPrivileges, RegainTempPrivileges,
    KBRead, KBWrite, KBFlush, KBEcho, 
    GiveErrorText, GetSpec, TimeToString, Clear, CopyStr,
    PostName, DoCCL,

    FIRQBType, FIRQBCharIndex, FIRQBIndex, FQNAM2, FQNAM2A, FQEXT2,
    XRBType, XRBIndex, XRBLKM, XRBSIZ,
    ErrorCode;


FROM SYSTEM IMPORT RSTSCALL,ADR;
FROM Dates IMPORT DATE,Today,DateToString,FORMAT;
FROM ModLibrary IMPORT Len,ReadString,ClearFIRQB;
FROM FileNames IMPORT FileStringScan;
FROM Times IMPORT TIME,StringToTime,Now,Before;
FROM ASCII IMPORT tab;

PROCEDURE SetSpecialRunPriority;

BEGIN
	XRB[XRLEN]:=256;
	(* Set up code. *)
	RSTSCALL(SETKEY);
	(* And ask RSTS to do it for us. *)
END SetSpecialRunPriority;

PROCEDURE SetUpKeyboards;

VAR
	Loop		:	INTEGER;

BEGIN
	FOR Loop:=1 TO NoOfKeyboards-1 DO
	 IF Loop<=8 THEN Keyboards[Loop]:=Loop ELSE Keyboards[Loop]:=Loop+26;
	  END; (* IF *)
	END; (* FOR *)
	Keyboards[NoOfKeyboards-1]:=42;
	Keyboards[NoOfKeyboards]:=15;
	(* Set up keyboards in inelegant manner.  Edit this to change
	   the keyboard number (eg after a SYSGEN). *)
END SetUpKeyboards;

PROCEDURE SetUpDates;

VAR
	Loop : CARDINAL;
	Loop1 : CARDINAL;
	Day : DATE;
	DayOfWeek : CARDINAL;

BEGIN
	Day:=Today();
	(* Best try for date is today. *)
	FOR Loop:=1 TO 5 DO
	 LOOP
	 DayOfWeek:=(Day MOD 7);
	  IF (DayOfWeek>0) AND (DayOfWeek<6) THEN
	   DateToString(Day,DDMONYY,'-',Dates[Loop]);
	   FOR Loop1:=0 TO 8 DO
	    Days[Loop,Loop1]:=DaysOfWeek[DayOfWeek,Loop1];
	   END; (* FOR *)
	   EXIT;
	  END; (* IF *)
	  (* If it is a weekday then copy it across. *)
	  INC(Day);
	 END; (* LOOP *)
	 (* And try again with the next day. *)
	 INC(Day);
	END; (* FOR *)
	(* Try for the next one. *)
END SetUpDates;

PROCEDURE SetUpDays;

BEGIN
	DaysOfWeek[0]:='SUNDAY   ';
	DaysOfWeek[1]:='MONDAY   ';
	DaysOfWeek[2]:='TUESDAY  ';
	DaysOfWeek[3]:='WEDNESDAY';
	DaysOfWeek[4]:='THURSDAY ';
	DaysOfWeek[5]:='FRIDAY   ';
	DaysOfWeek[6]:='SATURDAY ';
	(* Fairly obvious.... *)
END SetUpDays;

PROCEDURE GetData ( DayToGet : CARDINAL ; HowOpen : OpenMode );

VAR
	Loop,Loop1	: CARDINAL;
	Filename,
	DefaultFilename	: ARRAY [0..50] OF CHAR;

BEGIN
	Filename:='BOOK                                               ';
	FOR Loop:=0 TO 5 DO Filename[Loop+4]:=Dates[DayToGet,Loop]; END;
	Filename[6]:='.';
	(* Set up a unique filename from the date. *)
	CASE HowOpen OF
	  ReadRegardless : DefaultFilename:='_DP0:[1,95]/MO:4096';
	| ReadWrite	 : DefaultFilename:='_DP0:[1,95]/MO:1';
	(* Decide how we out to open it.  NB Files are stored in
	   [1,95] - edit this to change location. *)
	END; (* CASE *)
	LOOP
	 Lookup(BookingsFile,Filename,DefaultFilename);
	 (* Try to get the file. *)
	 Loop:=512;
	 ReadBlock(BookingsFile.channel,ADR(Bookings),1,0,
	  Loop,BookingsFile.result);
	 (* Try to get the first block.  If we failed to open then
	    we'll get an error here, so no need to check earlier. *)
	 IF BookingsFile.result=OK THEN EXIT; END;
	 (* Was it OK ? *)
	 IF BookingsFile.result=INTLCK THEN XRB[XRLEN]:=5; RSTSCALL(SLEEP);
	 (* No, but it was interlocked so sleep for a bit and retry. *)
	 ELSE
	 Create(BookingsFile,Filename,'_DP0:[1,95]',1);
	 FOR Loop:=1 TO NoOfPeriods DO
	  FOR Loop1:=1 TO NoOfKeyboards DO
	   Bookings[Loop,Loop1]:=0;
	  END; (* FOR *)
	 END; (* FOR *)
	 SaveData(TRUE);
	 (* Must have been a weird error so recreate the file blank. *)
	 END; (* ELSE *)
	 Close(BookingsFile);
	 (* Get ready to retry. *)
	END; (* LOOP *)
END GetData;

PROCEDURE SaveData ( Really : BOOLEAN);

VAR
	Count : CARDINAL;

BEGIN
	Count:=512;
	IF Really=TRUE THEN WriteBlock(BookingsFile.channel,ADR(Bookings),
	 1,0,Count,BookingsFile.result); END;
	(* Save the data if they want us to. *)
	Close(BookingsFile);
	(* Free the file slot. *)
END SaveData;

PROCEDURE GetAccount ( Prompt : ARRAY OF CHAR ) : CARDINAL;

VAR
	PPN	: CARDINAL;
	UserPPN	: CARDINAL;
	S	: ARRAY [0..20] OF CHAR;
	E	: ErrorCode;
	A	: CARDINAL;
	B	: CARDINAL;
	Priv	: BOOLEAN;

BEGIN
	LOOP
	LOOP
	 WriteString(Prompt);
	 JobStatus(0);
	 UserPPN:=FIRQB.cardinal[FQW13];
	 (* Find what account they're in now. *)
	 Priv:=((UserPPN DIV 256)=1);
	 (* Set privilege flag for later. *)
	 PPN:=UserPPN;
	 WriteString(' <[');
	 WriteInt((PPN DIV 256),0);
	 Write(',');
	 WriteInt((PPN MOD 256),0);
	 WriteString(']> >> ');
	 ReadString(S);
	 IF Len(S)=0 THEN EXIT; END;
	 (* Get the account - NB if they hit return then their PPN will 
	    be taken. *)
	 FIRQB.cardinal[FQPPN]:=0;
	 FileStringScan(S,E);
	 IF (E=OK) AND (FIRQB.cardinal[FQPPN]<>0) THEN 
	  PPN:=FIRQB.cardinal[FQPPN];
	  IF (PPN DIV 256)>=(UserPPN DIV 256) THEN EXIT; END;
	 END;
	 (* Valid account and less than or equal to their own ?
	    The reason for the project check is to stop hackers using
	    BOOKER as a way of testing out passwords. *)
	 WriteString('?Illegal account.');
	 WriteLn;
	 WriteLn;
	 (* Illegal so try again. *)
	END; (* LOOP *)
	IF Priv=TRUE THEN EXIT; END;
	(* Don't bother them with the password check if they can find it
	   out anyway. *)
	FIRQB.cardinal[FQW1]:=UURAD*400B;
	FIRQB.cardinal[FQPPN]:=0;
	FIRQB.cardinal[FQNAM1]:=PPN;
	FIRQB.cardinal[FQNAM1A]:=1;  (* Don't get no. of blocks used. *)
	FIRQB.cardinal[FQW2]:=0;
	FIRQB.cardinal[FQDEV]:=0;
	FIRQB.cardinal[FQUNIT]:=0;
	RSTSCALL(UUO);
	IF (FIRQB.cardinal[FQW0] DIV 400B)=0 THEN KBEcho(FALSE);
	 WriteString('Password >> ');
	 ReadString(S);
	 KBEcho(TRUE);
	 A:=FIRQB.cardinal[FQNAM1A];
	 B:=FIRQB.cardinal[FQEXT];
	 FileStringScan(S,E);
	 IF (A=FIRQB.cardinal[FQNAM1]) AND (B=FIRQB.cardinal[FQNAM1A]) THEN
	  EXIT; END;
	 (* If no errors then check password. *)
	END; (* IF *)
	WriteLn;
	WriteString('?Illegal account.');
	WriteLn;
	WriteLn;
	(* Otherwise try again. *)
	END; (* LOOP *)
	WriteLn;
	IF Priv=FALSE THEN
	 WriteString('Password accepted.');
	 WriteLn;
	END; (* IF *)
	(* If they're privileged then we can't have tested the password. *)
	WriteLn;
	RETURN PPN;
END GetAccount;

PROCEDURE LogErr ( e : ErrorCode );

VAR
	S : ARRAY [0..30] OF CHAR;

BEGIN
	GiveErrorText(e,S);
	WriteString(S);
END LogErr;

PROCEDURE GetPeriod () : CARDINAL;

VAR
	s : ARRAY [0..10] OF CHAR;
	bad : BOOLEAN;
	Period : CARDINAL;
	P1,P2,N : TIME;

BEGIN
	Now(N);
	Period:=0;
	s:='08:45';
	StringToTime(s,P1,bad);
	s:='09:15';
	StringToTime(s,P2,bad);
	IF (Before(N,P1)=FALSE) AND (Before(N,P2)=TRUE) THEN Period:=1; END;
	s:='13:10';
	StringToTime(s,P1,bad);
	s:='13:40';
	StringToTime(s,P2,bad);
	IF (Before(N,P1)=FALSE) AND (Before(N,P2)=TRUE) THEN Period:=2; END;
	s:='13:40';
	StringToTime(s,P1,bad);
	s:='14:10';
	StringToTime(s,P2,bad);
	IF (Before(N,P1)=FALSE) AND (Before(N,P2)=TRUE) THEN Period:=3; END;
	RETURN Period;
	(* Basically just check if it is between the times.  May have to
	   be edited if the periods change. *)
END GetPeriod;

PROCEDURE DoTrace ( PPN : CARDINAL) : BOOLEAN;

VAR
	Loop,Loop1,Loop2,NoOfBookings,MaxBookings,Period : CARDINAL;

BEGIN
	Period:=GetPeriod();
	IF Period=0 THEN Period:=1; END;
	(* Start trace after already used bookings. *)
	NoOfBookings:=0;
	MaxBookings:=0;
	FOR Loop:=1 TO 5  DO
	 GetData(Loop,ReadRegardless);
	 FOR Loop1:=Period TO NoOfPeriods DO
	  FOR Loop2:=1 TO NoOfKeyboards DO
	   IF Bookings[Loop1,Loop2]=PPN THEN WriteString(Days[Loop]);
	    WriteString('   '); WriteString('Period'); WriteInt(Loop1,2);
	    Write(tab); WriteString('Keyboard'); WriteInt(Keyboards[Loop2],3);
	    WriteLn; INC(NoOfBookings); END; (* IF *)
	  END; (* FOR *)
	 END; (* FOR *)
	SaveData(FALSE);
	Period:=1;
	END; (* FOR *)
	(* Cycle through Days, Periods and Keyboards checking for their
	   bookings. *)
	WriteLn;
	CASE (PPN DIV 256) OF
	   1 : MaxBookings:=10;
	| 10 : MaxBookings:=6;
	| 40 : MaxBookings:=4;
	| 60 : MaxBookings:=3;
	| 80 : MaxBookings:=2;
	ELSE WriteLn; WriteString('?Not a BOOKable account.'); WriteLn;
	END; (* CASE *)
	(* Find their maximum number of bookings. *)
	WriteLn;
	WriteInt(NoOfBookings,0);
	WriteString(' bookings out of a maximum of ');
	WriteInt(MaxBookings,0);
	WriteLn;
	IF NoOfBookings>=MaxBookings THEN WriteLn;
	 WriteString('Bookings limit reached.'); WriteLn; WriteLn;
	 RETURN FALSE;
	ELSE RETURN TRUE; END; (* IF *)
END DoTrace;

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

PROCEDURE CheckLegality(KB : INTEGER;
			Period : CARDINAL;
			VAR Job,Who,Where,What1,What2 : CARDINAL) : Legality;

VAR
	Loop : INTEGER;

BEGIN
	ClearFIRQB;
	FIRQB.cardinal[FQW1]:=256*UUTRM;
	FIRQB.cardinal[FQW2]:=256*KB;
	RSTSCALL(UUO);
	Job:=((FIRQB.cardinal[FQW2] MOD 256) DIV 2);
	IF Job>=256 THEN Job:=0; END;
	IF Job=0 THEN RETURN Legal;
	(* Get the job on that keyboard if any. *)
	ELSE
	 FIRQB.cardinal[FQW1]:=256*UUSYS;
	 FIRQB.cardinal[FQW2]:=Job;
	 RSTSCALL(UUO);
	 (* Do status on that job. *)
	 Where:=KB;
	 IF (FIRQB.cardinal[FQW2] DIV 256)<>Where THEN RETURN Legal;
	 (* It is possible that the job which owns the keyboard is
	    not actually attached to that keyboard.  For example
	    my multi-user adventure works by owning the keyboard
	    rather than communicating via message recievers with
	    a job on that keyboard. *)
	 ELSE
	  Who:=FIRQB.cardinal[FQW13];
	  What1:=FIRQB.cardinal[FQMODE];
	  What2:=FIRQB.cardinal[FQFLAG];
	  Loop:=1;
	  IF Bookings[Period,KB]=0 THEN RETURN FreeTerminal;
	  ELSE RETURN Illegal; END; (* IF *)
	 END; (* IF *)
	  (* Set up variables and get status. *)
	  (* NB We're assuming that the file is open here. *)
	END; (* IF *)
END CheckLegality;

PROCEDURE Send(KB : CARDINAL; Message : ARRAY OF CHAR);

BEGIN
	XRB[XRLEN]:=6;
	XRB[XRBC]:=Len(Message)+1;
	XRB[XRLOC]:=ADR(Message);
	XRB[XRCI]:=512;
	XRB[XRBLK]:=KB;
	RSTSCALL(SPEC);
	(* Set up and ask RSTS. *)
END Send;

PROCEDURE Kill(Job : CARDINAL);

BEGIN
	FIRQB.cardinal[FQW1]:=256*UUCHU;
	FIRQB.cardinal[FQW2]:=Job;
	RSTSCALL(UUO);
	(* The job will go after tidy up. *)
END Kill;

END BookLibrary.
