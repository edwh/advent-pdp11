1	ON ERROR GOTO 25000 &

10	KB%=28% &
\	OPEN '_KB'+NUM1$(KB%)+':' AS FILE #2%, RECORDSIZE 512%, MODE 1% &
\	FIELD #2%, 512% AS A$ &
\	OPEN '_KB:' AS FILE #1% &

100	ON ERROR GOTO 25000 &
\	WAIT 0% &
\	PRINT #1% IF CCPOS(1%) &
\	PRINT #1%, 'Master>'; &
\	INPUT LINE #1%, COM$ &
\	COM$=CVT$$(COM$,4%) &
\	J%=INSTR(1%,COM$,' ') &
\	GOTO 110 UNLESS J% &
\	ARG$=RIGHT(COM$,J%+1%) &
\	COM$=CVT$$(LEFT(COM$,J%-1%),255%) &
\	GOTO 120 &

110	COM$=CVT$$(COM$,255%) &
\	ARG$='' &

120	GOTO 1000 IF LEFT('CHECK',LEN(COM$))=COM$ &
\	GOTO 2000 IF LEFT('SEND',LEN(COM$))=COM$ &
\	GOTO 3000 IF LEFT('RECEIVE',LEN(COM$))=COM$ &
\	GOTO 4000 IF LEFT('DIE',LEN(COM$))=COM$ &
\	GOTO 100 &

1000	! CHECK &
	&
	&
	PRINT #2%, 'HELLO?' &
\	ON ERROR GOTO 1100 &
\	WAIT 5% &
\	J$=CVT$$(FNGETLINE$,255%) &
\	IF J$='HELLO!' THEN &
	PRINT #1% &
\	PRINT #1%, 'Slave is alive.' &
\	PRINT #1% &
\	GOTO 100 &

1010	PRINT #1%, 'Garbage from slave...';J$;CHR$(13%); &
\	SLEEP 1% &
\	PRINT #1%, SPACE$(50%);CHR$(13%); &
\	GOTO 1000 &

1100	IF ERR=15 THEN &
	PRINT #1% &
\	PRINT #1%, 'No reply from slave.' &
\	PRINT #1% &
\	RESUME 100 %
1110	GOTO 25000 &

2000	! SEND &
	&
	&
	FILE%=0% &
\	IF LEN(ARG$)=0% THEN &
	PRINT #1% &
\	PRINT #1%, 'Filespec>'; &
\	INPUT LINE #1%, ARG$ &

2010	ARG$=CVT$$(ARG$,255%) &
\	FILE%=0% &
\	UNTIL 0% &
\	THIS.FILE$=FNGET.NEXT.FILE$(ARG$) &
\	GOTO 2100 IF FILE%<0% &
\	UNTIL 0% &
\	WAIT 5% &
\	PRINT #2%, 'RE';THIS.FILE$ &
\	J$=CVT$$(FNGETLINE$,255%) &
\	IF J$='NO' THEN &
	PRINT #1% &
\	PRINT #1%, 'Slave refuses to receive ';THIS.FILE$ &
\	PRINT #1% &
\	GOTO 100 &

2020	IF J$<>'OK' THEN &
	PRINT #1%, 'Garbage from slave...';CHR$(13%); &
\	SLEEP 1% &
\	PRINT #1%, SPACE$(50%);CHR$(13%); &
\	NEXT &

2030	OPEN THIS.FILE$ FOR INPUT AS FILE #3% &
\	BL%=1% &

2035	GET #3% &
\	PUT #2%+SWAP%(3%) &
\	PRINT #1%, 'Block';BL%;' copied.';CHR$(13%) &
\	BL%=BL%+1% &
\	GOTO 2035 &

2040	PRINT #1%, THIS.FILE$;' copied.                        ' &
\	PRINT #2%, CHR$(26%) &
\	NEXT &

2100	PRINT #1% &
\	PRINT #1%, 'Batch copied.' &
\	PRINT #1% &
\	GOTO 100 &

15000	DEF* FNGETLINE$ &
\	J$='' &
\	UNTIL 0% &
\	GET #2% &
\	J$=J$+LEFT(A$,RECOUNT) &
\	GOTO 15010 IF ASCII(RIGHT(J$,LEN(J$)))<32% &
\	NEXT &

15010	FNGETLINE$=J$ &
\	FNEND &

15020	DEF* FNGET.NEXT.FILE$(F$) &
\	DIM V%(30%) &
\	CHANGE SYS(CHR$(6%)+CHR$(-10%)+F$) TO V% &
\	V%(1%)=6% &
\	V%(2%)=17% &
\	V%(3%)=FILE% &
\	V%(4%)=SWAP%(FILE%) &
\	CHANGE V% TO V$ &
\	CHANGE SYS(V$) TO V% &
\	FNGET.NEXT.FILE$=RAD$(V%(7%)+SWAP%(V%(8%)))+ &
	RAD$(V%(9%)+SWAP%(V%(10%)))+'.'+ &
	RAD$(V%(11%)+SWAP%(V%(12%))) &
\	FILE%=FILE%+1% &
\	GOTO 15040 &

15030	FILE%=-1% &

15040	FNEND &

25000	IF ERR=15 THEN &
	PRINT #1% &
\	PRINT #1%, 'No reply from slave.' &
\	PRINT #1% &
\	RESUME 100 &

25010	RESUME 15030 IF ERL=15020 &
\	RESUME 2040 IF ERL=2035 AND ERR=11 &

29000	PRINT ERR,ERL &

32767	END &

