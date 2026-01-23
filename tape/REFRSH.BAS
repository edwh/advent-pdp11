100	open "DP1:[1,95]refrsh.ctl" as file #1%, mode 2% &

200	input "Monster or object  (<CR> to exit)"; typ$ &
\	if typ$="" then 1000 &

300	input "Room number"; room% &
\	input "% chance   "; chance% &
\	input "Name       "; nam$ &

400	if typ$="o" then print #1,"OBJ" else print #1,"MON" &

500	print #1, room% &
\	print #1, chance% &
\	print #1, nam$ &

600	if typ$="o" then 200 &

700	input "Attack level"; attl% &
\	input "Defence level"; defl% &
\	input "Hit points"; hp% &
\	input "Max damage"; dam% &
\	input "Special attacks"; spat$ &
\	input "Experience pts"; xp% &

800	print #1, attl% &
\	print #1, defl% &
\	print #1, hp% &
\	print #1, dam% &
\	print #1, spat$ &
\	print #1, xp% &
\	print #1, 0. &
\	print #1, 0% &
\	print #1, 0% &

900	goto 200 &

1000	close #1% &

32767	end &

