program recordtest(tty);

{ This is a test of the record get/put features of the Swedish Pascal. }

type
  rec = record
	  number : integer;
	  string : array [1..10] of char;
	end;

var
  recfile : file of rec;
  i : integer;

procedure display( entry : integer);

begin
  reset(recfile,,,,[RANDOM]);
  get(recfile,entry);
  if ioresult(recfile)<0 then writeln('Error getting record (',ioresult(recfile),')')
  else
  begin
    writeln;
    writeln('Number : ',recfile^.number);
    writeln('String : ',recfile^.string);
    writeln;
  end;
end;

begin
  reset(recfile,'record.rec');
  writeln(ioresult(recfile));
  if ioresult(recfile)<0 then
  begin
    writeln('Initializing file');
    rewrite(recfile,'record.rec',,,[RANDOM]);
    for i:=1 to 10 do
    begin
      recfile^.number:=i;
      recfile^.string:='Hello     ';
      put(recfile,i);
      if ioresult(recfile)<0 then writeln('Error in put (',ioresult(recfile),')');
    end;
  end
  else
  begin
    display(1);
    i:=1;
    while i>=0 do
    begin
      write('Record number : '); break(tty);
      read(i);
      if i>0 then
      begin
        display(i);
        write('Number : '); break(tty); read(tty,recfile^.number);
        writeln;
        write('String : '); break(tty); readln;
        read(tty,recfile^.string); writeln;
        put(recfile,i);
        if ioresult(recfile)<0 then writeln('Error in put (',ioresult(recfile),')');
      end;
    end;
  end;
end.
