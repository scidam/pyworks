function res=undetermn(x)
[m n]=size(x);
res=0;
for i=1:m,
    for j=1:n,
        if (x(i,j)>eps), res=res+x(i,j)*log2(x(i,j));
        end;
    end;
end;
res=-res;