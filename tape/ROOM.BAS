10	OPEN "A:[1,95]BOARD.NTC" AS FILE #1% &
\	DIM #1%, A%(256%) &
\	INPUT ROOM% &
\	I%=I%+1% UNTIL A%(I%)=0% &
\	A%(I%)=ROOM% &
\	CLOSE #1% &
\	END &

