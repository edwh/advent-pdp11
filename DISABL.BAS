1	! Builds a command file to disable all unused accounts &
	! + all system accounts marked as SYSTEM ACCT. &
	ON ERROR GOTO 25000 &

10	OPEN "$ACCT.SYS" FOR INPUT AS FILE #1%, MODE 4096% &
\	OPEN "DISABL.CMD" FOR OUTPUT AS FILE #2% &
\	PRINT #2%, "RUN $UTILTY" &

20	UNTIL 0% &
\	INPUT #1%, PROJ%,PROG%,PASS$,QUOTA.,CLUS%,OWNER$ &
\	PRINT #2%, "CHANGE ["+NUM1$(PROJ%)+","+NUM1$(PROG%)+"] *" &
	IF OWNER$="UNUSED" OR OWNER$="SYSTEM ACCT." &
	!IF PROJ% > 9% &
	! Just swap the comment round to do the different things. &
\	NEXT &

9999	GOTO 32767 &

25000	IF ERR=11 AND ERL=20 THEN PRINT #2%, "EXIT" &
\	CLOSE #2% &
\	RESUME 32767 &

25010	PRINT "Error ";ERR,ERL &
\	RESUME 32767 &

32767	END &

