10	print 'Message '; &
\	input line a$ &
\	a$=cvt$$(a$,4%) &
\	open 'kb:' as file #1%, mode 256% &
\	print #1%, chr$(155%)+'0'; &
\	print #1%, chr$(155%)+'XB'; &
\	print #1%, chr$(155%)+'XU'; &
\	print #1%, chr$(155%)+'P0'; &
\	print #1%, chr$(155%)+'S"'; &
\	print #1%, chr$(155%)+':' &
\	print #1%, chr$(155%)+'6'; &
\	print #1%, chr$(155%)+'Y'+'""' &
\	print #1%, a$; &
\	print #1%, chr$(155%)+'Y'+chr$(31%+20%)+chr$(32%) &
\	print #1%, chr$(155%)+';'; &
\	print #1%, chr$(155%)+'Xb'; &
\	print #1%, chr$(155%)+'Xu'; &
\	print #1%, chr$(155%)+'5'; &
\	close #1% &

32767	end &

