MODULE Master;

FROM ModLibrary IMPORT ConvertToUpperCase,Len,LeftLen,ReadString;
FROM InOut IMPORT WriteString,WriteLn,Write,WriteInt;
FROM BookLibrary IMPORT SetSpecialRunPriority,SetUpKeyboards,NoOfKeyboards,
			SetUpDates,NoOfPeriods,Dates,Days,DaysOfWeek,Keyboards,
			SetUpDays,OpenMode,GetData,BookingsFile,SaveData,
			Bookings,GetAccount,GetPeriod,DoTrace,LogErr,NextArg,
			ARG;
FROM Times IMPORT TIME,FORMAT,TimeToString,Now;
FROM SYSTEM IMPORT ADR,RSTSCALL;
FROM RSTSFiles IMPORT FILE,Lookup,ReadBlock,Close;
FROM FileNames IMPORT FileStringScan;
FROM RSTS IMPORT ErrorCode,JobStatus,FIRQB,FIRQBType,FIRQBIndex,UUTRM,UUSYS,
		 UUO,UUCHU;
FROM ASCII IMPORT ctrlx,tab;
FROM XConversion IMPORT Done,StringToInt;
FROM Conversions IMPORT IntegerToString;
FROM RAD50 IMPORT RAD50ToString;
FROM Loader IMPORT Call;
FROM SystemTypes IMPORT LoadResultType,ErrorType;

CONST
	NumCom=8;
	(* Number of valid commands constant for GetCommand. *)

VAR
	Prompt : ARRAY [0..49] OF CHAR;
	(* Prompt for GetCommand. *)
	Default : ARRAY [0..10] OF CHAR;
	(* Default command. *)
	ValidCommand : ARRAY [0..NumCom-1] OF ARRAY [0..10] OF CHAR;
	(* List of valid commands. *)
	Command : CARDINAL;
	(* Command number as set by GetCommand. *)
	Dummy : BOOLEAN;
	LoadResult : LoadResultType;
	Error : ErrorType;

PROCEDURE Initialise;

VAR
	NoticeFile	: FILE;
	t		: TIME;
	s		: ARRAY [0..49] OF CHAR;
	d		: ARRAY [0..9] OF CHAR;
	s1		: ARRAY [0..511] OF CHAR;
	a		: CARDINAL;

BEGIN
	a:=512;
	Write(ctrlx);
	Write(tab);
	WriteString('MASTER V3.0 ');
	LogErr(OK);
	WriteString(' at ');
	Now(t);
	TimeToString(t,HHMMSS24,':',s);
	WriteString(s);
	Write('.');
	(* Print header. *)
	s:='_DP1:[1,95]MASTER.NTC/MO:4096';
	d:='';
	Lookup(NoticeFile,s,d);
	IF NoticeFile.result=OK THEN
	 LOOP
	  ReadBlock(NoticeFile.channel,ADR(s1),0,0,a,NoticeFile.result);
	  IF NoticeFile.result=EOFERR THEN EXIT; END;
	  WriteString(s1);
	 END; (* LOOP *)
	 Close(NoticeFile);
	END; (* IF *);
	(* Display notice text if there is one. *)
	SetUpKeyboards;
	SetUpDays;
	SetUpDates;
	Prompt:='Master';
	Default:='Summary';
	ValidCommand[0]:='TRACE';
	ValidCommand[1]:='DELETE';
	ValidCommand[2]:='CHECK';
	ValidCommand[3]:='LIST';
	ValidCommand[4]:='VERIFY';
	ValidCommand[5]:='EXIT';
	ValidCommand[6]:='SEND';
	ValidCommand[7]:='ANALYSE';
	(* Set up some variables. *)
END Initialise;

PROCEDURE GetCommand () : CARDINAL;

(* Accepts a command from the user, and checks it against the list.
   It relies on the external variables : NumCom : CONSTANT
					 Prompt,
					 Default : ARRAY OF CHAR
					 ValidCommand : ARRAY [0..Numcom-1] OF
							ARRAY [0.10] OF CHAR
   This routine will be called from both Booker and Master. *)

VAR
	Input	: ARRAY [0..10] OF CHAR;
	Length  : CARDINAL;
	Loop    : CARDINAL;
	Command : CARDINAL;
	Match	: CARDINAL;

BEGIN
	REPEAT
	 WriteLn;
	 WriteString(Prompt);
	 WriteString(' >> ');
	 ReadString(ARG);
	 Dummy:=NextArg(ARG,Input);
	 Length:=Len(Input);
	 IF Length=0 THEN FOR Loop:=0 TO 10 DO Input[Loop]:=Default[Loop];
	  END; (* FOR *) END; (* IF *)
	 ConvertToUpperCase(Input);
	 Command:=0;
	 Match:=0;
	 FOR Loop:=0 TO NumCom-1 DO
	  IF LeftLen(ValidCommand[Loop],Input)=TRUE THEN
	   Command:=Loop; INC(Match); END;
	 END; (* FOR *)
	UNTIL Match=1;
	(* Check against list for unique match. *)
	WriteLn;
	RETURN Command;
	(* Basically same as the one in Booker, but it strips of any
	   arguments that the user types in before checking the command. *)
END GetCommand;

PROCEDURE Trace;

VAR
	e : ErrorCode;
	Acct : ARRAY [0..10] OF CHAR;

BEGIN
	LOOP
	 IF NextArg(ARG,Acct)=FALSE THEN
	  WriteString('Account >> ');
	  ReadString(Acct);
	  WriteLn;
	 END; (* IF *)
	 (* Did they specify an account in the command line ? *)
	 FIRQB.cardinal[FQPPN]:=0;
	 FileStringScan(Acct,e);
	 IF (e=OK) AND (FIRQB.cardinal[FQPPN]<>0) THEN EXIT; END;
	 (* Check account for validity via filename string scan. *)
	END; (* LOOP *)
	Dummy:=DoTrace(FIRQB.cardinal[FQPPN]);
	(* And do the trace when we've extracted an account from them. *)
END Trace;

BEGIN
	Initialise;
	LOOP
	 Command:=GetCommand();
	 CASE Command OF
	   0 : Trace;
	 | 1 : Call('_DP0:[1,95]DELETE.MAS',LoadResult,Error);
	 | 2 : Call('_DP0:[1,95]CHECK .MAS',LoadResult,Error);
	 | 3 : Call('_DP0:[1,95]LIST  .MAS',LoadResult,Error);
	 | 4 : Call('_DP0:[1,95]VERIFY.MAS',LoadResult,Error);
	 | 5 : EXIT;
	 | 6 : Call('_DP0:[1,95]SEND  .MAS',LoadResult,Error);
	 | 7 : Call('_DP0:[1,95]ANALYS.MAS',LoadResult,Error);
	 ELSE WriteLn; WriteString('?Not yet implemented.'); WriteLn;
	 END; (* CASE *)
	 (* Trace is in this module because it is fairly small. The rest
	    are in seperate overlays, and should be called like this.  If
	    one of the overlays does not exist, then a run-time error (hence
	    a core dump) will be generated. *)
	END; (* LOOP *)

END Master.
