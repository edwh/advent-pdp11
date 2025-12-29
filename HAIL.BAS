10	! Run under BASICS &

20	INPUT 'Number ';NM$ &

30	WHILE NM$>'1' &
\	J$=QUO$(NM$,'2',1%) &
\	IF INSTR(1%,J$,'.')=0% THEN NM$=J$ ELSE NM$=SUM$(PROD$(NM$,'3',0%), &
	'1') &

40	PRINT NM$ &
\	NEXT &
\	GOTO 20 &

32767	END &

