10	B%(1%)=4% : B%(2%)=1% : B%(3%)=5% : B%(4%)=9% : B%(5%)=13%
15	INPUT "ZERO THE MFD ON DP1:"; Z$ : IF Z$<>"YES" THEN 99
20	OPEN "DP1:[1,1]" AS FILE 1%
30	DIM#1%, A%(32767%)
40	FOR I%=0% TO 15%
50	A%((256%*I%)+(247%+J%)) = B%(J%) FOR J%=1% TO 5%
60	NEXT I%
99	END
