10	OPEN 'A:[1,95]ADVENT.DTA' AS FILE #1% , MODE 4096% &
\	FIELD #1%, 1% AS ROOM$, 16% AS EX$ &
\	INPUT 'Exit into which room';A% &
\	INPUT 'Start';S% &
\	INPUT 'Finish';F% &
\	FOR ROOM%=S% TO F% &
\	GET #1%, RECORD ROOM% &
\	PRINT ROOM% IF INSTR(1%,'NESW',MID(EX$,INSTR(1%,EX$,CVT%$(A%))-1%, &
	1%)) IF INSTR(1%,EX$,CVT%$(A%)) &
\	NEXT ROOM% &
\	CLOSE #1% &
\	END &

