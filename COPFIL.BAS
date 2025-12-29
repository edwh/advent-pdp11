10	DEF FNL%(Z%) &
\	Z0%=(SWAP%(Z%) AND 248%)/16% &
\	Z1%=(SWAP%(Z%) AND 14%)/2% &
\	FNL%=(Z1%*M2%+Z0%)*256%+(Z% AND 511%)/2% &
\	FNEND &
\	PRINT &
\	PRINT "Disk "; &
\	INPUT LINE D$ &
\	PRINT &
\	D$=CVT$$(D$,-1%) &
\	PRINT "Date "; &
\	INPUT LINE DA$ &
\	DA$=CVT$$(DA$,-1%) &
\	M%=INSTR(1%,"JANFEBMARAPRMAYJUNJULAUGSEPOCTNOVDEC",MID(DA$,4%,3%)) &
\	D%=VAL(MID("000031059090120151181212243273304334",M%,3%))+VAL(LEFT(DA$,2%)) &
\	D%=D%+1000%*(VAL(RIGHT(DA$,8%))-70%) &

100	OPEN D$+"[1,1]" FOR INPUT AS FILE #1%, MODE 8192% &
\	DIM #1%, A1%(32767%) &
\	M1%=A1%(248%) &

110	Z0%=(SWAP%(A1%(N1%)) AND 248%)/16% &
\	Z1%=(SWAP%(A1%(N1%)) AND 14%)/2% &
\	N1%=(Z1%*M1%+Z0%)*256%+(A1%(N1%) AND 511%)/2% &
\	GOTO 32767 UNLESS N1% &
\	GOTO 110 IF A1%(N1%+7%)=0% &
\	GOTO 110 IF (A1%(N1%+4%) AND 64%)=0% &
\	PROJ%=SWAP%(A1%(N1%+1%)) AND 255% &
\	PROG%=A1%(N1%+1%) AND 255% &
\	ACC$="["+NUM1$(PROJ%)+","+NUM1$(PROG%)+"]" &
\	GOTO 110 IF ACC$="[1,1]" &
\	OPEN D$+ACC$ FOR INPUT AS FILE #2%, MODE 8192% &
\	DIM #2%, A2%(32767%) &
\	M2%=A2%(248%) &
\	N2%=0% &

210	N2%=FNL%(A2%(N2%)) &

220	IF N2%=0% THEN 110 &

250	F$=RAD$(A2%(N2%+1%))+RAD$(A2%(N2%+2%))+"."+RAD$(A2%(N2%+3%)) &
\	PROT%=SWAP%(A2%(N2%+4%)) &
\	PROT%=PROT% AND 255% &
\	M3%=FNL%(A2%(N2%+6%)) &
\	ACCESS$=DATE$(A2%(M3%+1%)) &
\	D1%=A2%(M3%+1%) &
\	SIZE%=A2%(M3%+2%) &
\	CREATE$=DATE$(A2%(M3%+3%)) &
\	CREATE.TIME$=TIME$(A2%(M3%+4%)) &
\	CLUS%=A2%(M3%+7%) &

260	PRINT D$;ACC$;F$;TAB(25%);NUM1$(SIZE%);TAB(30%);"<";NUM1$(PROT%); &
		">";TAB(37%);ACCESS$;TAB(48%);CREATE$;TAB(58%); &
		CREATE.TIME$;TAB(68%);NUM1$(CLUS%) IF D1%<D% &

270	GOTO 210 &

32767	goto 10 &
\	end &

