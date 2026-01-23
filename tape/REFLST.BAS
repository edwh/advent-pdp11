5	on error goto 30000 &

10	open "A:[1,95]REFRSH.CTL" as file #1%, mode 4096% &

15	print &
\	input "<M>onsters or <O>bjects "; typ$ &
\	typ$=left(cvt$$(typ$,-1%),1%) &
\	goto 15 if typ$="" &
\	goto 15 if instr(1%,"MO",typ$)=0% &

16	if typ$="M" then open "REFMON.LST" for output as file #2% &
	else open "REFOBJ.LST" for output as file #2% &

17	if typ$="M" then what$="monsters" &
	else what$="objects" &

18	print #2% &
\	print #2%, "Listing of ";what$;" in REFRSH.CTL on ";date$(0%) &
\	print #2% &
\	print #2%, "Name";tab(30%);"Room";tab(35%);"%   ";tab(40%); &
\	if typ$="M" then &
	print #2%,"Att  Def  HP   Dam  Spec      XP" &
	else print #2% &

20	input #1%, t$ &
\	input #1%, room% &
\	input #1%, chance% &
\	input #1%, nam$ &

30	if t$<>"MON" then goto 50 &

40	input #1%, attl% &
\	input #1%, defl% &
\	input #1%, hp% &
\	input #1%, dam% &
\	input #1%, spat$ &
\	input #1%, xp% &
\	input #1%, dummy &
\	input #1%, dummy% &
\	input #1%, dummy% &

50	if typ$<>left(t$,1%) then goto 20 &

60	print #2% &
\	print #2%, nam$;tab(30%); &
\	print #2%, num1$(room%);tab(35%); &
\	print #2%, num1$(chance%);tab(40%); &
\	if t$="OBJ" then goto 20 &

70	print #2%, num1$(attl%);tab(45%); &
\	print #2%, num1$(defl%);tab(50%); &
\	print #2%, num1$(hp%);tab(55%); &
\	print #2%, num1$(dam%);tab(60%); &
\	print #2%, spat$;tab(70%); &
\	print #2%, num1$(xp%); &

80	goto 20 &

30000	if err<>11 then print "Unexpected error";err;"at line";erl &
\	close #1% &
\	close #2% &

32767	end &

