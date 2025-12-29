1	ON ERROR GOTO 20000 &

10	!		M O N E Y . B A S  &
	&
	&
	!	This is designed to return accounting data for users &
	! in privileged accounts without having to answer all the MONEY &
	! questions. Thus the accounting data for the user's account can &
	! be obtained simply by running this program. &

20	DIM A%(30%) &
\	PROJ%=0% &
\	PROG%=0% &
\	PRINT &
\	PRINT "Proj,prog < Own > "; &
\	INPUT LINE ACC$ &
\	ACC$=CVT$$(ACC$,-1%) &
\	ACC$="0,0" UNLESS LEN(ACC$) &
\	J%=INSTR(1%,ACC$,",") &
\	PROJ%=VAL(LEFT(ACC$,J%-1%)) &
\	PROG%=VAL(RIGHT(ACC$,J%+1%)) &

30	CHANGE STRING$(30%,0%) TO A% &
\	A%(0%)=30% &
\	A%(1%)=6% &
\	A%(2%)=14% &
\	A%(8%)=PROJ% &
\	A%(7%)=PROG% &
\	CHANGE A% TO A$ &
\	CHANGE SYS(A$) TO A% &

40	BLOCKS.USED.=A%(6%)*256%+A%(5%) &
\	QUOTA.=A%(27%)+SWAP%(A%(28%)) &
\	PROJ%=A%(8%) &
\	PROG%=A%(7%) &

50	T0=256.*A%(14%)+A%(13%)+16384.*(A%(22%) AND 252%) &
	\ T=INT(T0/10.) &
	\ T0=T0-10.*T &
	\ GOSUB 4000 &
		! CPU TIME. &

60	PRINT &
\	PRINT "Account	Used	Quota	Run-time" &
\	PRINT NUM1$(PROJ%);",";NUM1$(PROG%);CHR$(9%); &
\	PRINT NUM1$(BLOCKS.USED.);CHR$(9%);NUM1$(QUOTA.);CHR$(9%); &
		M$ &

3999	GOTO 20 &

4000	M$="" &
	\ T%=0% &
	\ C0%=T/3600. &
	\ IF C0% THEN &
		T=T-3600.*C0% &
	\	GOSUB 4100 &
	\	M$=M$+":" &

4010	C0%=T/60. &
	\ IF C0% OR T% THEN &
		T=T-60.*C0% &
	\	GOSUB 4100 &
	\	M$=M$+":" &

4020	C0%=T &

4100	T$=NUM$(C0%+T%*100%) &
	\ M$=M$+MID(T$,2%+T%,LEN(T$)-2%-T%) &
	\ T%=1% &
	\ RETURN &
	&

20000	IF ERR=52% THEN PRINT &
\	PRINT "?Illegal account number." &
\	RESUME 20 &

32767	END &

