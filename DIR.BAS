10	DEF FNL%(Z%) &
\	Z0%=(SWAP%(Z%) AND 248%)/16% &
\	Z1%=(SWAP%(Z%) AND 14%)/2% &
\	FNL%=(Z1%*M2%+Z0%)*256%+(Z% AND 511%)/2% &
\	FNEND &
\	PRINT &
\	PRINT "Account "; &
\	INPUT LINE ACC$ &
\	PRINT &
\	ACC$=CVT$$(ACC$,-1%) &
\	OPEN ACC$ FOR INPUT AS FILE #2%, MODE 8192% &
\	DIM #2%, A2%(32767%) &
\	M2%=A2%(248%) &
\	PRINT &
\	PRINT "Clustersize for this account -";M2% &
\	PRINT &
\	N2%=0% &
\	PRINT "Name";TAB(12%);"Size";TAB(17%);"Prot";TAB(23%);"Access"; &
		TAB(34%);"Create";TAB(44%);"Time";TAB(54%);"Clustersize" &

210	N2%=FNL%(A2%(N2%)) &

220	IF N2%=0% THEN 32767 &

250	F$=RAD$(A2%(N2%+1%))+RAD$(A2%(N2%+2%))+"."+RAD$(A2%(N2%+3%)) &
\	PROT%=SWAP%(A2%(N2%+4%)) &
\	PROT%=PROT% AND 255% &
\	M3%=FNL%(A2%(N2%+6%)) &
\	ACCESS$=DATE$(A2%(M3%+1%)) &
\	SIZE%=A2%(M3%+2%) &
\	CREATE$=DATE$(A2%(M3%+3%)) &
\	CREATE.TIME$=TIME$(A2%(M3%+4%)) &
\	CLUS%=A2%(M3%+7%) &

260	PRINT D$;P$;F$;TAB(12%);NUM1$(SIZE%);TAB(17%);"<";NUM1$(PROT%); &
		">";TAB(23%);ACCESS$;TAB(34%);CREATE$;TAB(44%); &
		CREATE.TIME$;TAB(54%);NUM1$(CLUS%) &

270	GOTO 210 &

32767	goto 10 &
\	end &

