10 !	&
!		Private CCL definitions &

20 ! Initialisation &

30	ON ERROR GOTO 30000 &
\	OPEN 'CCL.CCL' FOR INPUT AS FILE #1%, MODE 8192% &
\	DIM V%(30%) &

40 ! Decode CCL string &

50	CCL$ = CVT$$(SYS(CHR$(7%)), 1% + 4% + 8% + 16% + 32% + 128%) &
\	POSN% = INSTR(1%, CCL$, ' ') &
\	CCL$ = RIGHT(CCL$, POSN% + 1%)	! Strip this program's name out &
\	CCL$ = '' UNLESS POSN% &
\	POSN% = INSTR(1%, CCL$, ' ') &
\	PS2% = INSTR(1%, CCL$, '/') &
\	POSN% = PS2% IF ((POSN% = 0%) OR ((PS2% < POSN%) AND PS2%)) &
\	ARG$ = '' &
\	ARG$ = RIGHT(CCL$, POSN%) IF POSN% &
\	CCL$ = LEFT(CCL$, POSN% - 1%) IF POSN% &

60 ! Find program in CCL.CCL file &

70	INPUT LINE #1%, GT$ &
\	GOT$ = CVT$$(GT$, 255% - 64%) &
\	GOTO 70 UNLESS (LEN(GOT$) AND LEFT(GOT$, 1%) <> '!') &
\	POSN% = INSTR(1%, GOT$, '=') &
\	IF POSN% = 0% THEN PRG$ = CVT$$(GT$, 4%) &
\	P% = INSTR(1%, PRG$, ';') &
\	P% = LEN(PRG$) + 1% UNLESS P% &
\	PROG$ = LEFT(PRG$, P% - 1%) &
\	CHANGE SYS(CHR$(6%) + CHR$(-10%) + PROG$) TO V% &
\	NAM$ = CVT$$(RAD$(V%(7%) + SWAP%(V%(8%))) + &
		RAD$(V%(9%) + SWAP%(V%(10%))), 2%) &
\	GOTO 100 IF LEFT(NAM$, LEN(CCL$)) = CCL$ &
\	GOTO 70 &

80	NAM$ = LEFT(GOT$, POSN% - 1%) &
\	PRG$ = RIGHT(GOT$, POSN% + 1%) &
\	OPT% = INSTR(1%, NAM$, '-') &
\	OPT$ = '' &
\	OPT$ = RIGHT(NAM$, OPT% + 1%) IF OPT% &
\	NAM$ = LEFT(NAM$, OPT% - 1%) IF OPT% &
\	GOTO 70 UNLESS (LEFT(NAM$ + OPT$, LEN(CCL$)) = CCL$) &
				AND (LEN(CCL$) >= LEN(NAM$)) &

90 ! Chain to program now that we have found it in the CCL file &

100	PS2% = INSTR(1%, PRG$, ';') &
\	PS% = PS2% &
\	PS% = LEN(PRG$) + 1% UNLESS PS2% &
\	LIN% = 0% &
\	LIN% = VAL(RIGHT(PRG$, PS% + 1%)) IF PS2% &
\	PRG$ = LEFT(PRG$, PS% - 1%) &

120	JUNK$ = SYS(CHR$(8%) + NAM$ + OPT$ + ARG$) &
\	CHAIN PRG$ LINE LIN% + 32767% + 1% &

29999 ! Error trapping &

30000	IF ERL = 30 THEN PRINT &
\	PRINT "Can't open CCL.CCL file." &
\	RESUME 32767 &

30010	IF ERL = 70 AND ERR = 11 THEN PRINT &
\	PRINT "Can't find that CCL (" + CCL$ + ")." &
\	RESUME 32767 &

30015	IF ERL = 70 AND ERR = 2 THEN PRINT &
\	PRINT 'Illegal file name - ' + CVT$$(PRG$, 153%); &
\	RESUME 32767 &

30020	IF ERL = 100 THEN PRINT &
\	PRINT 'Illegal line number - ' + CVT$$(LIN$, 153%); &
\	RESUME 32767 &

30030	IF ERL = 120 THEN PRINT &
\	PRINT "Can't chain to program - " + CVT$$(PRG$, 153%) &
\	RESUME 32767 &

30040	PRINT &
\	PRINT 'Unexpected error ' + NUM1$(ERR) + ' at line ' + NUM1$(ERL) + &
			' in private CCL definitions.' &
\	RESUME 32767 &

32766 ! Finish &

32767	END &

