MODULE RealMath;

FROM InOut IMPORT WriteString,WriteLn;
FROM RealInOut IMPORT WriteReal;

VAR
  X , Y : REAL;
  I     : CARDINAL;

BEGIN
  X := 0.0;
  Y := 9.9;
  WriteString('Start'); WriteLn;
  FOR I:=1 TO 1000 DO
    X := X + ( Y * Y - Y ) / Y;
  END;
  WriteString('Finish'); WriteLn;
  WriteReal(X,10); WriteLn;
END RealMath.
