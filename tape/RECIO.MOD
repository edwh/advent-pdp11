MODULE RecordIOTest;

FROM InOut IMPORT WriteString,WriteLn,WriteInt,ReadInt,ReadString,WriteCard,
		  ReadCard;
FROM RecordIO IMPORT IOResult,FILE,Mode,Lookup,Create,Reset,Close,
		     RecCount,Get,Put,GetPos,SetPos;

TYPE
  RecType = RECORD
              Number : INTEGER;
              String : ARRAY [0..9] OF CHAR;
            END;

VAR
  Rec : RecType;
  f : FILE;
  Count : CARDINAL;
  Record : INTEGER;

BEGIN
  WriteLn;
  WriteString('RecordIOTest'); WriteLn;
  WriteLn;
  WriteString('Re-creating SY:TEST.REC');
  WriteLn;
  ReadCard(Count);
  Create(f,'SY:TEST.REC','',SingleUser,Rec,Count);
  Reset(f);
  WriteCard(ORD(f^.result),5); WriteLn;
  REPEAT
    WriteString('Record >> '); ReadInt(Record); WriteLn;
    WriteString('Number >> '); ReadInt(Rec.Number); WriteLn;
    WriteString('String >> '); ReadString(Rec.String); WriteLn;
    Put(f,Record,Rec);
    Reset(f);
    WriteCard(ORD(f^.result),5); WriteLn;
    WriteLn; WriteString ('Record to read >> '); ReadInt(Record); WriteLn;
    Get(f,Record,Rec);
    WriteCard(ORD(f^.result),5); WriteLn;
    WriteLn;
    WriteString('Record >> '); WriteInt(Record,5); WriteLn;
    WriteString('Number >> '); WriteInt(Rec.Number,5); WriteLn;
    WriteString('String >> '); WriteString(Rec.String); WriteLn; WriteLn;
  UNTIL FALSE;
END RecordIOTest.
