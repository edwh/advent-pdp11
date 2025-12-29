5 input "Which disc";a$
10 open a$+"[1,1]" as file #1
15 def fnl%(p%,c%):p0%=(swap%(p%) and 248%)/16%:p1%=(swap%(p%) and 14%)/2%:fnl%=(p1%*c%+p0%)*256%+(p% and 511%)/2%:fnend
17 f%=0:input "(0) Accounts only (1) Full info";f%
20 dim #1,a%(32767)
35 i%=0
50 i%=fnl%(a%(i%),a%(504%))
52 if (a%(i%+4) and 64%)=0% then goto 300
55 print int(a%(i%+1)/256);",";a%(i%+1)-256*int(a%(i%+1)/256)
57 if f% then gosub 70
60 if (a%(i%) and -16%)<>0% then goto 50
65 goto 32767
70 for l%=i% to i%+7%
80 print l%,a%(l%),rad$(a%(l%))
90 next l%
100 return
300 print "File:";rad$(a%(i%+1));rad$(a%(i%+2));".";rad$(a%(i%+3))
310 goto 60
32767 end
