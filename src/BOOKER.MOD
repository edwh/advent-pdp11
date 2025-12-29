MODULE Booker;

FROM ModLibrary IMPORT ConvertToUpperCase,Len,LeftLen,ReadString;
FROM InOut 	 IMPORT WriteString,WriteLn,Write,WriteInt;
FROM BookLibrary IMPORT SetSpecialRunPriority,SetUpKeyboards,NoOfKeyboards,
		 SetUpDates,NoOfPeriods,
		 Dates,Days,DaysOfWeek,Keyboards,SetUpDays,
		 OpenMode,GetData,BookingsFile,SaveData,Bookings,
		 GetAccount,GetPeriod,DoTrace,LogErr;
FROM Times IMPORT TIME,FORMAT,TimeToString,Now;
FROM SYSTEM IMPORT ADR;
FROM RSTSFiles IMPORT FILE,Lookup,ReadBlock,Close;
FROM RSTS IMPORT ErrorCode,JobStatus,FIRQB,FIRQBType,FIRQBIndex,FIRQBCharIndex;
FROM ASCII IMPORT ctrlx,tab;
FROM XConversion IMPORT Done,StringToInt;
FROM Conversions IMPORT IntegerToString;


CONST
	NumCom=5;
	(* Number of legal commands in Booker. *)

VAR
	Prompt  : ARRAY [0..49] OF CHAR;
	(* Prompt for GetCommand. *)
	Default : ARRAY [0..10] OF CHAR;
	(* Default command for GetCommand. *)
	ValidCommand : ARRAY [0..NumCom-1] OF ARRAY [0..10] OF CHAR;
	(* List of legal commands. *)
	Command : CARDINAL;
	(* Command number as set by GetCommand. *)
	BookPPN : CARDINAL;
	(* The account that the user is currently tracing, etc. *)
	Dummy : BOOLEAN;

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
	WriteString('BOOKER V3.0 ');
	LogErr(OK);
	WriteString(' at ');
	Now(t);
	TimeToString(t,HHMMSS24,':',s);
	WriteString(s);
	Write('.');
	(* Header. *)
	s:='_DP1:[1,95]BOOKER.NTC/MO:4096';
	(* This is where the notice text is kept. *)
	d:='';
	Lookup(NoticeFile,s,d);
	IF NoticeFile.result=OK THEN
	 LOOP
	  ReadBlock(NoticeFile.channel,ADR(s1),0,0,a,NoticeFile.result);
	  IF NoticeFile.result=EOFERR THEN EXIT; END;
	  WriteString(s1);
	 END; (* LOOP *)
	 (* Get all the blocks in the file and write them to the screen. *)
	 Close(NoticeFile);
	END; (* IF *);
	(* Either we've displayed it or it wasn't there. *)
	SetUpKeyboards;
	SetUpDays;
	SetUpDates;
	Prompt:='Trace/Delete/Book/Change/Exit';
	Default:='Book';
	ValidCommand[0]:='TRACE';
	ValidCommand[1]:='DELETE';
	ValidCommand[2]:='BOOK';
	ValidCommand[3]:='CHANGE';
	ValidCommand[4]:='EXIT';
	BookPPN:=GetAccount('Enter account to be used');
	(* Set up some variables and some things used in GetCommand. *)
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
	 WriteString(Prompt); WriteString(' <'); WriteString(Default);
	 WriteString('> >> ');
	 ReadString(Input);
	 Length:=Len(Input);
	 IF Length=0 THEN FOR Loop:=0 TO 10 DO Input[Loop]:=Default[Loop];
	  END; (* FOR *) END; (* IF *)
	 ConvertToUpperCase(Input);
	 (* Prompt and get reply, in upper case. *)
	 Command:=0;
	 Match:=0;
	 FOR Loop:=0 TO NumCom-1 DO
	  IF LeftLen(ValidCommand[Loop],Input)=TRUE THEN
	   Command:=Loop; INC(Match); END;
	   (* If it matches then save it and increment match counter. *)
	 END; (* FOR *)
	UNTIL Match=1;
	(* This way we only exit this loop when we have a unique command. *)
	RETURN Command;
END GetCommand;

PROCEDURE DoBook;

VAR
	Loop	: INTEGER;
	s	: ARRAY [0..15] OF CHAR;
	BookingDay : CARDINAL;
	BookingPeriod : INTEGER;
	BookingKeyboard : INTEGER;

BEGIN
	WriteLn;
	Write(tab);
	WriteString('Days available for booking :');
	WriteLn;
	WriteLn;
	FOR Loop:=1 TO 5 DO
	 Write(tab); Write(tab); Write(tab); Write(tab); Write(tab);
	 WriteString(Days[Loop]);
	 WriteLn;
	END; (* FOR *)
	(* Display the bookable days in the right order. *)
	LOOP
	 WriteLn;
	 WriteString('Day to book for <');
	 WriteString(Days[1]);
	 WriteString('> >> ');
	 ReadString(s);
	 (* Prompt for day and get it. *)
	 IF Len(s)=0 THEN FOR Loop:=0 TO 8 DO s[Loop]:=Days[1,Loop]; END; END;
	 (* Default of current day. *)
	 ConvertToUpperCase(s);
	 FOR Loop:=1 TO 5 DO IF LeftLen(Days[Loop],s)=TRUE THEN EXIT; END; END;
	 (* Find a match if there is one. *)
	END; (* LOOP *)
	BookingDay:=Loop;
	LOOP
	 WriteLn;
	 BookingPeriod:=1;
	 IF BookingDay=1 THEN BookingPeriod:=GetPeriod(); IF BookingPeriod=0
	  THEN BookingPeriod:=1; END; (* IF *) END; (* IF *)
	 (* Default period is 1, or the current period if they want to 
	    book for today. *)
	 WriteString('Period <');
	 WriteInt(BookingPeriod,1);
	 WriteString('> >> ');
	 ReadString(s);
	 IF Len(s)=0 THEN IntegerToString(BookingPeriod,0,s); END;
	 StringToInt(s,BookingPeriod);
	 IF (Done=TRUE) AND (BookingPeriod<=NoOfPeriods) AND (BookingPeriod>0)
	  THEN EXIT; END;
	 (* Ask for a period and check it. *)
	END; (* LOOP *)
	WriteLn;
	WriteString('Free terminals for period');
	WriteInt(BookingPeriod,2);
	WriteString(' on ');
	WriteString(Days[BookingDay]);
	WriteLn;
	WriteLn;
	GetData(BookingDay,ReadRegardless);
	(* Prepare to list free terminals. *)
	FOR Loop:=1 TO NoOfKeyboards DO
	 IF Bookings[BookingPeriod,Loop]=0 THEN WriteInt(Keyboards[Loop],0);
	  WriteLn; END; (* IF *)
	END; (* FOR *)
	(* List free terminals. *)
	LOOP
	 WriteLn;
	 JobStatus(0);
	 BookingKeyboard:=ORD(FIRQB.char[FQSIZM]);
	 FOR Loop:=1 TO NoOfKeyboards DO
	  IF (Keyboards[Loop]=BookingKeyboard) AND
	   (Bookings[BookingPeriod,Loop]<>0) THEN BookingKeyboard:=0; END;
	 END;
	 IF BookingKeyboard=0 THEN
	 Loop:=1;
 	 LOOP
 	  IF Bookings[BookingPeriod,Loop]=0 THEN BookingKeyboard:=
 	   Keyboards[Loop]; EXIT; END; (* IF *)
 	  IF Loop=NoOfKeyboards THEN BookingKeyboard:=0;
 	   WriteString('?No free terminals.'); EXIT; END;
 	  INC(Loop);
 	 END; (* LOOP *)
	 END; (* IF *)
	 (* Try to find a free terminal for default. *)
	 (* First default is own KB if free, otherwise first free one. *)
	 IF BookingKeyboard=0 THEN EXIT; END;
	 (* No free terminals so exit. *)
	 WriteString('Keyboard <'); WriteInt(BookingKeyboard,0);
	 WriteString('> >> ');
	 ReadString(s);
	 IF Len(s)=0 THEN IntegerToString(BookingKeyboard,0,s); END;
	 StringToInt(s,BookingKeyboard);
	 FOR Loop:=1 TO NoOfKeyboards DO IF (Keyboards[Loop]=BookingKeyboard)
	  AND (Bookings[BookingPeriod,Loop]=0) THEN BookingKeyboard:=Loop;
	  EXIT; END; (* IF *)
	 END; (* FOR *)
	END; (* LOOP *)
	(* Get keyboard and convert to internal format. *)
	SaveData(FALSE);
	IF BookingKeyboard<>0 THEN
	GetData(BookingDay,ReadWrite);
	Bookings[BookingPeriod,BookingKeyboard]:=BookPPN;
	SaveData(TRUE);
	WriteLn;
	WriteString('Booking made for Keyboard');
	WriteInt(Keyboards[BookingKeyboard],3);
	WriteString(' in period');
	WriteInt(BookingPeriod,2);
	WriteString(' on ');
	WriteString(Days[BookingDay]);
	WriteLn;
	END; (* IF *)
	(* Make the booking. *)
END DoBook;

PROCEDURE DoDelete;

VAR
	S : ARRAY [0..5] OF CHAR;
	Loop,Loop1,Loop2,Period : CARDINAL;
BEGIN
	FOR Loop:=1 TO 5 DO
	 GetData(Loop,ReadWrite);
	 (* Get the data for that day.  ReadWrite as may want to delete. *)
	 FOR Loop1:=1 TO NoOfPeriods DO
	  FOR Loop2:=1 TO NoOfKeyboards DO
	   IF Bookings[Loop1,Loop2]=BookPPN THEN WriteString(Days[Loop]);
	    WriteString('   '); WriteString('Period'); WriteInt(Loop1,2);
	    Write(tab); WriteString('Keyboard'); WriteInt(Keyboards[Loop2],3);
	    WriteString(' ? '); ReadString(S); ConvertToUpperCase(S);
	    IF Len(S)=0 THEN S:='NO'; END;
	    IF LeftLen('YES',S)=TRUE THEN Bookings[Loop1,Loop2]:=0; END;
	    (* Display booking if found and query for deletion. *)
	   END; (* IF *)
	  END; (* FOR *)
	 END; (* FOR *)
	SaveData(TRUE);
	(* Store the data. *)
	END; (* FOR *)
	WriteLn;
END DoDelete;

BEGIN
	Initialise;
	LOOP
	 Command:=GetCommand();
	 CASE Command OF
	   0 : WriteLn; Dummy:=DoTrace(BookPPN);
	 | 1 : WriteLn; DoDelete; 
	 | 2 : WriteLn; IF DoTrace(BookPPN)=TRUE THEN DoBook; END;
		(* Only allow to book if they're under their maximum. *)
	 | 3 : WriteLn; BookPPN:=GetAccount('New account');
		(* Change the current account. *)
	 | 4 : EXIT;
		(* Handy to be able to do this ! *)
	 ELSE WriteLn; WriteString('?Not yet implemented.'); WriteLn;
	 (* While developing, if I haven't put the call in, the else
	    traps all commands which have been defined as valid but
	    I haven't written the routines for yet.  I've written all
	    the routines now anyway, but I'll leave this here. *)
	 END; (* CASE *)
	END; (* LOOP *)

END Booker.
