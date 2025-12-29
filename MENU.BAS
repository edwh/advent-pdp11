10	TEST$=CHR$(2%)+CHR$(15%)+'Menu Demo      Help           '+ &
	'Exit           ' &
\	UNTIL 0% &
\	J%=FNMENU%(TEST$) &
\	ON J%+1% GOTO 20,32767 &

20	PRINT 'Look at the program!' &
\	SLEEP 2% &
\	NEXT &

15000	! MENU Function. &
	&
	&
	! Format is : &
	&
	&
	!	Byte	Function &
	&
	!	1	Number of options. &
	!	2	Maximum length of string (used for box size). &
	&
	! Next comes header, then options.  All must be padded to the &
	! length specified in 2 by the user. &
	&
	! If you don't pass it the right stuff it will fall over!! &
	&
	&
	DEF* FNMENU%(MENU$) &
\	NO.OF.OPTIONS%=ASCII(MENU$) &
\	LENGTH.OF.STRING%=ASCII(RIGHT(MENU$,2%)) &
\	HEADER$=MID(MENU$,3%,LENGTH.OF.STRING%) &
\	OPTIONS$=RIGHT(MENU$,3%+LENGTH.OF.STRING%) &
\	PRINT CHR$(155%)+'Wf'+CHR$(155%)+'WB'+CHR$(155%)+'P3'+ &
	CHR$(155%)+'O2'+CHR$(155%)+'P3' &
	! Display both pages. &
	! Write on page 2 &
	! Clear screen. &
\	PRINT CHR$(155)+'S'+CHR$(32%+2%+3%+NO.OF.OPTIONS%+1%) &
	! Set size of window. &
\	LEFT.SIDE%=(80%-LENGTH.OF.STRING%)/2% &
\	PRINT CHR$(155%)+'}B'+CHR$(LEFT.SIDE%+30%)+CHR$(32%)+ &
	CHR$(LENGTH.OF.STRING%+34%)+CHR$(32%+3%+NO.OF.OPTIONS%) &
	! Draw box. &
\	PRINT CHR$(155%)+'}H'+CHR$(LEFT.SIDE%+30%)+CHR$(34%)+ &
	CHR$(LENGTH.OF.STRING%+34%) &
	! Draw line. &
\	J$=SYS(CHR$(3%)) &
	! Echo off. &
\	PRINT CHR$(155%)+'O1' &
	! Display on page 1 &
\	PRINT CHR$(155%)+'XU' &
\	PRINT CHR$(155%)+'Y'+CHR$(33%)+CHR$(32%+LEFT.SIDE%)+CVT$$(HEADER$,128%) &
\	PRINT CHR$(155%)+'Xu' &
\	PRINT CHR$(155%)+'XH' &
\	PRINT CHR$(155%)+'Y'+CHR$(35%+J%)+CHR$(32%+LEFT.SIDE%)+ &
	MID(OPTIONS$,J%*LENGTH.OF.STRING%+1%,LENGTH.OF.STRING%) FOR &
	J%=0% TO NO.OF.OPTIONS%-1% &
\	CURRENT.OPTION%=0% &

15010	PRINT CHR$(155%)+'Xh'+CHR$(155%)+'Y'+CHR$(35%+CURRENT.OPTION%)+ &
	CHR$(32%+LEFT.SIDE%)+ &
	MID(OPTIONS$,CURRENT.OPTION%*LENGTH.OF.STRING%+1%,LENGTH.OF.STRING%) &
\	PRINT CHR$(155%)+'XH' &
\	J$=SYS(CHR$(4%)) &
\	FIELD #0%, 1% AS J$ &
\	GET #0% &
\	IF INSTR(1%,'852',J$)=0% THEN &
	PRINT CHR$(7%) &
\	GOTO 15010 &

15020	IF J$='5' THEN &
	FNMENU%=CURRENT.OPTION% &
\	GOTO 16000 &

15030	GOTO 15040 UNLESS J$='8' &
\	IF CURRENT.OPTION%=0% THEN PRINT CHR$(7%) &
\	GOTO 15010 &

15035	CH%=-1% &
\	GOTO 15050 &

15040	IF CURRENT.OPTION%=NO.OF.OPTIONS%-1% THEN &
	PRINT CHR$(7%) &
\	GOTO 15010 &

15045	CH%=+1% &

15050	PRINT CHR$(155%)+'XH' &
\	PRINT CHR$(155%)+'Y'+CHR$(35%+CURRENT.OPTION%)+CHR$(32%+LEFT.SIDE%)+ &
	MID(OPTIONS$,CURRENT.OPTION%*LENGTH.OF.STRING%+1%,LENGTH.OF.STRING%) &
\	CURRENT.OPTION%=CURRENT.OPTION%+CH% &
\	GOTO 15010 &

16000	PRINT CHR$(155%)+'Xh'+CHR$(155%)+'Y'+CHR$(31%+20%)+CHR$(31%); &
\	J$=SYS(CHR$(2%)) &
\	FNEND &

32767	PRINT CHR$(155%)+'0'+CHR$(24%) &
\	END &

