10	ON ERROR GOTO 0 &

20	DIM SY%(30%) &

30	CHANGE SYS(CHR$(6%) + CHR$(-3%)) TO SY% &
\	DEVPTR% = SY%(7%) + SWAP%(SY%(8%)) &
\	DEVCNT% = SY%(5%) + SWAP%(SY%(6%)) &
\	CHANGE STRING$(30%,0%) TO SY% &
\	CHANGE SYS(CHR$(6%) + CHR$(-12%)) TO SY% &
\	DEVNAM% = SY%(5%) + SWAP%(SY%(6%)) &
\	DEVOKB% = SY%(9%) + SWAP%(SY%(10%)) &
\	DEVSYN% = SY%(23%) + SWAP%(SY%(24%)) &

100	FOR D% = (DEVNAM% + DEVOKB%) TO (DEVSYN% - 2%) STEP 2% &
\	J1% = DEVCNT% + DEVOKB% &
\	J2% = PEEK(DEVPTR% + DEVOKB%) &
\	D$ = CVT%$(SWAP%(PEEK(D%))) &
\	A% = PEEK(DEVPTR% + D% - DEVNAM%) &
\	FOR U% = PEEK(PEEK(A%)-8%)/8% TO PEEK(DEVCNT% - DEVNAM% + D%) &
\	J% = PEEK(PEEK(J2 + 28%) + 2%) &
\	PRINT D$ + NUM1$(U%); &
\	PRINT "		Disabled "; IF ((J% AND 1%)<>0% AND (J%<>3% AND J%<>5%)) &
\	PRINT &
\	J2% = J2% + 2% &
\	NEXT U% &
\	J1% = J1% + 2% &
\	NEXT D% &

32767			END &

