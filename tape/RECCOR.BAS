10	ON ERROR GOTO 25000 &
\	OPEN "A:[1,95]ADVENT.DTA" AS FILE #1%, MODE 1% &
\	PRINT "Backup file "; &
\	INPUT LINE A$ &
\	A$=CVT$$(A$,-1%) &
\	OPEN A$ AS FILE #2%, MODE 4096% &
\	UNTIL 0% &
\	INPUT R% &
\	GET #2%, RECORD R% &
\	PUT #1%+SWAP%(2%), RECORD R% &
\	NEXT &
\	CLOSE #1%,#2% &
\	GOTO 32767 &

25000	PRINT ERR,ERL &

32767	END &

