10	open 'kb:' as file #1%, mode 256% &
\	until 0% &
\	input #1%, a$ &
\	print #1%, chr$(155%)+a$ &
\	next &

32767	end &

