MODULE PRIME;

FROM InOut IMPORT WriteLn,WriteInt;

CONST
	maxprime=20000;
VAR
	notprime : ARRAY [1..maxprime] OF BOOLEAN;
	num   : CARDINAL;
	temp  : CARDINAL;

BEGIN
	num:=3;
	WHILE num<=maxprime DO
		IF notprime[num]=FALSE THEN
		WriteInt(num,5);
		temp:=num;
		WHILE temp<maxprime DO
			notprime[temp]:=TRUE;
			temp:=temp+num*2;
		END;
		END;
	num:=num+2;
	END;
END PRIME.
