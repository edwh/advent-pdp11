10	INPUT 'ID';ID$ &
\	INPUT 'Message';MESS$ &
\	J$=SYS(CHR$(6%)+CHR$(22%)+CHR$(-1%)+CHR$(0%)+ID$+STRING$(10%,0%)+MESS$) &
\	END &

