function [res,indeces_of_nans]=GetFactorsFromVector(X)
%indeces_of_nans(i)=1, если X(i)=NaN;
warning off all
index_r=1;
indeces_of_nans=zeros(size(X));
Y=cell(0,0);
for k=1:length(X),
    if ~IsInSet(X(k,1) ,Y)&&~sum(isnan(X{k,1}))&&~strcmpi(num2str(X{k,1}),'nan'),         
        Y{index_r,1}=X{k,1};
        index_r=index_r+1;
    end;
  if  isnan(X{k,1}),  indeces_of_nans(k,1)=1;  end; 
end;
    res=Y;
    
    
    
    function  res=IsInSet(x,Y)
    %Устанавливает всречается ли где-либо х  массиве Y;
    res=false;
    for k=1:length(Y),
        
        if isnumeric(x{1,1})&&isnumeric(Y{k,1}), 
           if  x{1,1}==Y{k,1}, res=true; 
            break; end;
        elseif strcmp(num2str(Y{k,1}),num2str(x{1,1})), 
            res=true; 
            break; 
        end;
        
    end;
