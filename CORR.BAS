10	open "a:advent.dta" as file #1%, mode 4096% &
\	ch%=0% &
\	field #1%, 1% as room$, 16% as ex$, 83% as people$, 100% as object$, &
	312% as desc$ &
\	for room%=1% to 850% &
\	get #1%, record room% &
\	if instr(1%,desc$,"/") or cvt$$(left(desc$,8%),255%)="" then print room% &
\	ch%=ch%+1% &

20	next room% &
\	close #1% &
\	print &
\	print ch% &

32767	end &

