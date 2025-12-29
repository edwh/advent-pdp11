100	&
	&
	!	L O G . B A S &
	&
	&

400	PPN%,PPN.LOG% = 0% &
\	PPN% = PEEK(PEEK(PEEK(520%) + 8%) + 24%) &
\	J$=SYS(CHR$(12%)) &
\	PPN.LOG%=SWAP%(CVT$%(RIGHT(J$,5%))) &
\	IF PPN.LOG%=PPN% THEN INPUT 'Proj,prog ';A%,B% &
\	PPN.LOG%=256%*A%+B% &

520	PROJ.LOG% = SWAP%(PPN.LOG%) AND 255% &
\	PROG.LOG% = PPN.LOG% AND 255% &

700	SY$ = SYS(CHR$(6%) + CHR$(5%)) &
		+ SYS(CHR$(6%) + CHR$(4%) + STRING$(2%,0%) &
		+ CHR$(PROG.LOG%) + CHR$(PROJ.LOG%) &
		+ MID(SYS(CHR$(6%) + CHR$(14%) + STRING$(4%,0%) &
		+ CHR$(PROG.LOG%) + CHR$(PROJ.LOG%) + CHR$(-1%)),9%,4%)) &
\	PRINT "Job logged from [" + NUM1$(SWAP%(PPN%) AND 255%) + "," &
		+ NUM1$(PPN% AND 255%) + "] to [" &
		+ NUM1$(PROJ.LOG%) + "," + NUM1$(PROG.LOG%) + "]" &
\	GOTO 32767 &

5000	PRINT "?You may not use log from this account" &
\	GOTO 32767 &

32767			END &

