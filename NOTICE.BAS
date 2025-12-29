10	OPEN "_DP1:[1,95]ADVENT.CHR" AS FILE #1% &
\	DIM #1%, I%(511%), B$(511%)=512% &
\	GOTO 20 IF I%(J%)=0% FOR J%=0% TO 511% &
\	PRINT "?No room." &
\	GOTO 32767 &

20	INPUT "Room number for noticeboard ", I%(J%) &
\	B$(J%)=STRING$(512%,0%) &
\	CLOSE #1% &
\	PRINT "OK." &
\	GOTO 32767 &

32767	END &

