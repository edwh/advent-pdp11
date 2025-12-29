PROGRAM PI (INPUT,OUTPUT,F);
CONST
	PIFACTOR = 6.0;
VAR
	significance,noofterms,DENOMINATOR,X,XSQUARED,NUMERATOR,SUM,TERM : REAL;
	sigfigs : integer;
BEGIN
	WRITELN ("TO WHAT SIGNIFICANCE DO YOU WANT ?");
	READ (SIGNIFICANCE);
	X := 1.0/SQRT(3); XSQUARED := SQR (X);
	NUMERATOR := X; DENOMINATOR :=1 ; SUM := X;
	REPEAT
		NUMERATOR := -NUMERATOR * XSQUARED;
		DENOMINATOR := DENOMINATOR + 2.0;
		TERM := NUMERATOR / DENOMINATOR;
		SUM := SUM + TERM;
	UNTIL ABS(TERM) < SIGNIFICANCE;
	NOOFTERMS := (DENOMINATOR+1.0) / 2.0;
	writeln ("For the series up to term ",noofterms);
	sigfigs := trunc(noofterms);
	WRITELN;
	writeln ("Pi is ",sum*pifactor:sigfigs);
END.
