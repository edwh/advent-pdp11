5 input "Which disk to sort MFD of";d$
10 open d$+"[1,1]" as file #1,mode 16384%
15 def fnl%(p%,c%):p0%=(swap%(p%) and 248%)/16%:p1%=(swap%(p%) and 14%)/2%:fnl%=(p1%*c%+p0%)*256%+(p% and 511%)/2%:fnend
20 dim #1,a%(4500%)
25 print "MFD copied into memory"
30 dim n%(300%),p%(300%),m%(50%)
35 i%=0:j%=0:k%=0
40 n%(0%)=a%(0%)
50 i%=fnl%(a%(i%),a%(504%))
52 if (a%(i%+4) and 64%)<>64% then goto 500
55 n%(j%+1)=a%(i%)
57 p%(j%)=a%(i%+1):j%=j%+1%
60 if (a%(i%) and -16%)<>0 then goto 50
70 gosub 1000
75 a%(0%)=n%(0)
80 for l%=0 to j%-1
90 a%(fnl%(n%(l%),a%(504%)))=n%(l%+1)
110 next l%
113 a%(fnl%(n%(j%-1%),a%(504%)))=m%(0)
115 for l%=0 to k%-1
117 a%(fnl%(m%(l%),a%(504%)))=m%(l%+1)
118 next l%
120 a%(fnl%(m%(k%-1),a%(504%)))=0%
200 goto 32767
500 rem File in [1,1] needs special treatment.
510 m%(k%)=n%(j%):k%=k%+1%:n%(j%)=a%(i%):goto 50
1000 rem Sort Routine
1005 flag%=0%
1010 for s%=0% to j%-1%
1012 e=p%(s%):if e<0 then e=65536+e
1015 f=p%(s%+1):if f<0 then f=65536+f
1020 if (f>e) then goto 1050
1030 flag%=1%:d%=n%(s%):n%(s%)=n%(s%+1):n%(s%+1)=d%
1040 d%=p%(s%):p%(s%)=p%(s%+1):p%(s%+1)=d%
1050 next s%
1060 if flag% then flag%=0:goto 1010
1070 return
32767 end
