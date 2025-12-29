10	open 'a:advent.chr' for input as file #1%, mode 4096% &

20	dim #1%, a$(100%)=512% &
\	for i%=0% to 100% &
\	print left(a$(i%),30%);' : ' &
\	j%=82% &

30	j%=instr(j%,a$(i%),'$') &
\	goto 40 unless j% &
\	print mid(a$(i%),j%,instr(j%,a$(i%),' ')-j%) &
\	j%=j%+1% &
\	goto 30 &

40	next i% &
\	close #1% &

32767	end &

