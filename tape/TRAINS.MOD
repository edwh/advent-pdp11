MODULE Trains;

(* If anybody wonders why I've written this stupid program, it was an A-Level
   Computer Studies question.  

  This just goes to show what a technical exam the A-Level is. *)


FROM InOut IMPORT ReadInt,WriteInt,WriteLn,WriteString;

VAR
  List : ARRAY [1..51] OF CARDINAL;
  Number : INTEGER;
  Loop : CARDINAL;

BEGIN
  WriteString('Enter passenger totals terminated by a negative number.');
  WriteLn;
  FOR Loop:=1 TO 51 DO List[Loop]:=0; END;
  REPEAT
    ReadInt(Number);
    IF Number>0 THEN
      IF Number>999 THEN
        INC(List[51]);
      ELSE
        INC(List[((Number DIV 20)+1)]);
      END;
    END;
  UNTIL Number<0;
  WriteLn;
  FOR Loop:=1 TO 50 DO
    WriteInt((Loop-1)*20,3);  WriteString('...'); WriteInt(Loop*20-1,3);
    WriteInt(List[Loop],5);
    WriteLn;
  END;
  WriteString('>999'); WriteInt(List[51],5); WriteLn;
END Trains.
