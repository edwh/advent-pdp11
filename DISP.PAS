PROGRAM DISPLAY;

VAR
	F1,F2 : FILE OF CHAR;
	S1,S2 : ARRAY [1..30] OF CHAR;
	A     : CHAR;

PROCEDURE PROMPT ( VAR S1,S2 : ARRAY [1..30] OF CHAR);

VAR I : INTEGER;

BEGIN
	I := 0;
	WHILE S2[I]<>CHR(0) DO
		BEGIN
			I := I + 1;
			WRITE (S2[I]);
		END;
	READLN (S1);
END;

BEGIN
	S2[1]:='D';
	S2[2]:='i';
	S2[3]:='s';
	S2[4]:='p';
	S2[5]:='l';
	S2[6]:='a';
	S2[7]:='y';
	S2[8]:=' ';
	S2[9]:='>';
	S2[10]:='>';
	S2[11]:=' ';
	PROMPT(S2,S2);
END.
