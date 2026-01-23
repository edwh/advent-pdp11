MODULE Dir;

(* Directory demo program.  NB Can't do both protection code and create time
   because GetSpec expects filename string scan format in the FIRQB, rather
   than directory lookup, which is the same except that the protection code
   is in the wrong place.  I edited Directory to move the protection code
   across if the user wants it, but if you do that then the create time
   gets corrupted.

   The upshot of all this is that you can have protection code OR create
   time, but NOT both.

		Edward D.W. Hibbert 12/2/88

*)

FROM Directory IMPORT Lookup,LookupNext;
FROM InOut IMPORT ReadString,WriteString,WriteLn,WriteCard;
FROM RSTS IMPORT ErrorCode;

VAR
  FileSpec	:	ARRAY [0..79] OF CHAR;
  FileName	:	ARRAY [0..79] OF CHAR;
  Result	:	ErrorCode;

BEGIN
  WriteLn; WriteString('FileSpec >> '); ReadString(FileSpec); WriteLn;
  Lookup(FileSpec,{0..8,15},FileName,Result);
  IF Result<>OK THEN
    WriteString('Error ('); WriteCard(ORD(Result),5); WriteString(').'); 
    WriteLn;
  ELSE
    WriteString(FileName); WriteLn;
    LOOP
      LookupNext({0..8,15},FileName,Result);
      IF Result<>OK THEN EXIT; END;
      WriteString(FileName); WriteLn;
    END;
  END;
END Dir.
