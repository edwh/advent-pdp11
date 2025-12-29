10	&
	!	M  F  D  R  E  C  .  B  A  S    & 
	&

20	ON ERROR GOTO 30000 &
	\ DIM FDCM%(7%) &

100	OPEN "_KB:MFDREC.CMD" AS FILE 12% &

200	PRINT "INPUT FROM FILE  >> "; &
	\ INPUT LINE #12%,IN.FILE$ &
		! GET THE INPUT FILE I.D. &
	\ PRINT "OUTPUT TO DISK >> "; &
	\ INPUT LINE #12%,OUT.DISK$ &
		! AND THE DISK TO OUTPUT TO. &
	& 
	!	****  NOTE THAT THEY ARE NOT CHECKED....  **** &
	&

300	OPEN IN.FILE$ FOR INPUT AS FILE 1%, RECORDSIZE 1024%, MODE 8192% &
		! OPEN THE FILE WE'RE TAKING THE DUMP FROM &
		! RECORDSIZE=1024 (NEED THIS SIZE TO COVER BOOTSTRAP) &
		! MODE=8192 (READ ONLY-- JUST IN CASE.) &

350	OPEN OUT.DISK$ FOR OUTPUT AS FILE 2%, RECORDSIZE 1024%  &
		! OPEN THE OUTPUT DISK, SAME RECORDSIZE. &

400	&
	!	C O P Y   T H E   B O O T S T R A P    &
	&

410	GET #1%, RECORD 1% &
	\ PUT #2%+SWAP%(1%), RECORD 0% &
	&
	! PUT THE BOOTSTRAP BACK INTO RECORD 0 OF THE OUTPUT DISK. &
	&

500	&
	!	F I E L D   T H E   F I L E S   &
	&

510	FIELD #1%, 496% AS DUMMY$, 16% AS FDCM.1$, &
		   496% AS DUMMY$, 16% AS FDCM.2$ &
		! THE FIELDS FOR THE FILE. &
	&

600	&
	!	G E T   T H E   F . D . C . M .   F R O M   T H E   F I L E   &
	&

610	GET #1%, RECORD 3%			! GET THE FIRST RECORD OF THE MFD. &
	&
	\ FDCM%(P%)=SWAP%(CVT$%(MID(FDCM.1$,(P%*2%)+1%,2%))) &
					FOR P%=0% TO 7% &
						! TURN THE FDCM INTO AN ARRAY &
	&
	\ FDCM.CHECK$=FDCM.1$+""		! USE THIS FOR CHECKING LATER &
	&
	\ MFD.CLUSTERSIZE%=FDCM%(0%)		! EXTRACT THE MFD CLUSTERSIZE &
	&

700	&
	!	C O P Y   T H E   M . F . D .   &
	&

710	for mfd.sector%=1% to 7% &
		! For each mfd sector.. &
	&
	\ for sec%=1% to mfd.clustersize%/2% &
		! For Each disk sector in this mfd sector... &
	&
		\ GET #1%, RECORD (MFD.SECTOR%-1%)*16%+(SEC%-1%)*2%+3% &
\ PRINT "FROM";(MFD.SECTOR%-1%)*16%+(SEC%-1%)*2%+3%; &
					! Get that block of the mfd. &
	&
		\ print "%FDCM's Don't match for: "; &
			"Mfd sector=";num1$(mfd.sector%); &
			",Disk sector=";num1$(sec%); &
			",Record =";num1$((fdcm%(mfd.sector%)+sec%-2%)*2%+1%) &
				if fdcm.1$<>fdcm.check$ &
				or fdcm.2$<>fdcm.check$ &
	&
		\ PUT #2%+SWAP%(1%), record ((fdcm%(mfd.sector%) &
				  + sec% - 1% ) -1% )*2% +1% &
\ PRINT "  TO";((FDCM%(MFD.SECTOR%)+SEC%-1%)-1%)*2%+1% &
	&
	\ next sec% &
	\ next mfd.sector% &

1000	&
	!	D  O  N  E  .   &
	&

1010	close 1%,2% &
	\ print "Done O.K." &
	\ print &
	\ goto 200 &

20000	def * fnert$(x%)=cvt$$(right(sys(chr$(6%)+chr$(9%)+chr$(x%)),3%),140%) &

30000	& 
	!	E R R O R   T R A P   &
	&

30010	resume 32767 if err=11% and erl=200% &

30030	if erl=300% then &
		  print "?Error opening input disk : ";fnert$(err) &
		\ print &
		\ resume 200 &

30040	if erl=350% Then &
		  print "?Error opening output file : ";fnert$(err) &
		\ print &
		\ resume 200 &

32000	print "?Error in 'MFDBAK' : ";fnert$(err);" at line";erl &
	\ resume 32767 &

32767	close 1%,2%,12% &
	\ end &

