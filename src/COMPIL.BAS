10	ON ERROR GOTO 25000 &
\	DIM V%(30%) &

20	OPEN 'KB:' AS FILE #1% &
\	PRINT #1% &
\	PRINT #1%, 'Control file >> '; &
\	INPUT LINE #1%, FIL$ &
\	PRINT #1% &
\	PRINT #1% &
\	FIL$=CVT$$(FIL$,255%) &
\	FIL$=FIL$+'.CPL' UNLESS INSTR(1%,FIL$,'.') &
\	OPEN FIL$ FOR INPUT AS FILE #2% &

100	INPUT LINE #2%, CTL.FIL$ &
\	CTL.FIL$=CVT$$(CTL.FIL$,255%) &
\	J%=INSTR(1%,CTL.FIL$,'/') &
\	GOTO 109 UNLESS J% &
\	J$=RIGHT(CTL.FIL$,J%+1%) &
\	CTL.FIL$=LEFT(CTL.FIL$,J%-1%) &
\	CHANGE SYS(CHR$(6%)+CHR$(-10%)+J$) TO V% &
\	V%(1%)=6% &
\	V%(2%)=17% &
\	V%(3%)=0% &
\	V%(4%)=SWAP%(0%) &
\	CHANGE V% TO V$ &
\	CHANGE SYS(V$) TO V% &
\	DATE.AFTER%=V%(19%)+SWAP%(V%(20%)) &
\	TIME.AFTER%=V%(21%)+SWAP%(V%(22%)) &
\	AUTO%=-1% &

109	OPEN CTL.FIL$ FOR OUTPUT AS FILE #3% &

110	INPUT LINE #2%, LIN$ &
\	GOTO 150 IF LEFT(LIN$,5%)='$$$$$' &
\	PRINT #3%, LIN$; &
\	GOTO 110 &

150	INPUT LINE #2%, LIN$ &
\	GOTO 200 IF LEFT(LIN$,5%)='$$$$$' &
\	EACH$=EACH$+LIN$ &
\	GOTO 150 &

200	INPUT LINE #2%, LIN$ &
\	GOTO 250 IF LEFT(LIN$,5%)='$$$$$' &
\	LAST$=LAST$+LIN$ &
\	GOTO 200 &

250	INPUT LINE #2%, LIN$ &
\	I%=0% &

260	CHANGE SYS(CHR$(6%)+CHR$(-10%)+LIN$) TO V% &
\	V%(1%)=6% &
\	V%(2%)=17% &
\	V%(3%)=I% &
\	V%(4%)=SWAP%(I%) &
\	CHANGE V% TO V$ &
\	CHANGE SYS(V$) TO V% &
\	NAM$=CHR$(V%(23%))+CHR$(V%(24%))+NUM1$(V%(25%))+':'+ &
	'['+NUM1$(V%(6%))+','+NUM1$(V%(5%))+']'+ &
	RAD$(V%(7%)+SWAP%(V%(8%)))+RAD$(V%(9%)+SWAP%(V%(10%)))+'.'+ &
	RAD$(V%(11%)+SWAP%(V%(12%))) &
\	J%=V%(21%)+SWAP%(V%(22%)) &
\	GOTO 261 IF AUTO%=-1% AND (V%(19%)+SWAP%(V%(20%))>DATE.AFTER% OR &
	((V%(19%)+SWAP%(V%(20%)))=DATE.AFTER%) AND &
	J%<TIME.AFTER%) &
\	GOTO 270 IF AUTO%=-1% &
\	PRINT #1%, NAM$;'   ';DATE$(V%(19%)+SWAP%(V%(20%)));'   '; &
	TIME$(V%(21%)+SWAP%(V%(22%)));'  ? '; &
\	INPUT #1%, J$ &
\	J$=CVT$$(J$,255%) &
\	GOTO 270 UNLESS LEN(J$) &
\	GOTO 270 UNLESS LEFT('YES',LEN(J$))=J$ &
\	GOTO 262 &

261	PRINT #1%, NAM$;'   ';DATE$(V%(19%)+SWAP%(V%(20%)));'   '; &
	TIME$(V%(21%)+SWAP%(V%(22%))) &

262	J$=EACH$ &
\	J$=LEFT(J$,INSTR(1%,J$,"@@@@@")-1%)+NAM$+RIGHT(J$,INSTR(1%,J$, &
	"@@@@@")+5%) WHILE INSTR(1%,J$,"@@@@@") &
\	PRINT #3%, J$; &

270	I%=I%+1% &
\	GOTO 260 &

300	GOTO 250 &

500	PRINT #3%, LAST$; &
\	CLOSE #3% &
\	J$=SYS(CHR$(14%)+'@ '+LEFT(CTL.FIL$,INSTR(1%,CTL.FIL$,'.')-1%)+ &
	'='+CTL.FIL$+'/TIM/DET') &
\	GOTO 32767 &

999	GOTO 32767 &

25000	! ERRORS &
	&
	&
	RESUME 500 IF ERL=260 AND ERR=11 &
\	RESUME 32767 IF ERR=11 AND ERL=20 &
\	IF ERL=20 THEN &
	PRINT #1% &
\	PRINT #1%, '?Illegal control file.' &
\	RESUME 20 &

25010	IF ERL=100 THEN &
	PRINT #1% &
\	PRINT #1%, '?Illegal .CTL file.' &
\	RESUME 32767 &

25020	RESUME 500 IF ERL=250 AND ERR=11 &
\	IF ERL=250 THEN PRINT #1% &
\	PRINT #1%, '?Illegal file specification.' &
\	RESUME 32767 &

25030	RESUME 300 IF ERL=260 AND ERR=5 &
\	RESUME 500 IF ERL=250 AND ERR=11 &

32767	END &

