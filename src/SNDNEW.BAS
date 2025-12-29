10	PRINT "Message "; &
\	INPUT LINE J$ &
\	J$=CVT$$(J$,4%) &

15	J$=SYS(CHR$(6%)+CHR$(22%)+CHR$(-1%)+CHR$(0%)+"ADVNEW"+STRING$(10%,0%)+ &
		J$) &

20	GOTO 10 &

30	J$=SYS(CHR$(7%)) &
\	J$=RIGHT(J$,INSTR(1%,J$," ")+1%) &
\	J$=SYS(CHR$(6%)+CHR$(22%)+CHR$(-1%)+CHR$(0%)+"ADVNEW"+STRING$(10%,0%)+ &
		J$) &

32767	END &

