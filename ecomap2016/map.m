function varargout = map(varargin)
% MAP M-file for map.fig
%      MAP, by itself, creates a new MAP or raises the existing
%      singleton*.
%
%      H = MAP returns the handle to a new MAP or the handle to
%      the existing singleton*.
%
%      MAP('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MAP.M with the given input arguments.
%
%      MAP('Property','Value',...) creates a new MAP or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before map_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to map_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help map

% Last Modified by GUIDE v2.5 11-Aug-2009 15:33:07

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @map_OpeningFcn, ...
                   'gui_OutputFcn',  @map_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before map is made visible.
function map_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to map (see VARARGIN)

% Choose default command line output for map
handles.output = hObject;
if length(varargin)==1, handles.User=varargin{1}; 
else guidata(hObject, handles); return; end;
handles.User.IndicatorToClose=false;
fprintf(handles.User.logfile,'%s: Количество кластеров = %d\n',datestr(now),handles.User.NumberOfClusters);

%----------------------------------------------------Выбранный список
%факторов должен иметь по крайней мере 2 числовых фактора

handles.User.NumFactors_Boolean=strcmpi([handles.User.SelectedFactorTypesEX(1,1:end)],'num');
NumFactors_Boolean=handles.User.NumFactors_Boolean;
if sum(handles.User.NumFactors_Boolean)<2,
   fprintf(handles.User.logfile,'%s: Отсутствуют необходимые данные для картирования. Данные будут использованы в качестве обучающей выборки.\n',datestr(now)); 
    %%%Необходимо дописать запрос на файл с данными для кластеризации
     Res_of_Selected = questdlg('Загрузить файл с данными для картирования?', ...
                         'Необходимы дополнительные данные', ...
                         'Да', 'Нет','Да');
    switch Res_of_Selected,
        case   'Да'
            filename=0;
            while ~ischar(filename),    
             [filename, pathname] = uigetfile({'*.mat'},'Выберите файл с данными');
            end;
  fprintf(handles.User.logfile,'%s: Для картирования выбран файл: %s.\n',datestr(now),strcat(pathname,filename)); 
   %%%%%%%%%%%%%%%%%Проверка синтаксиса выбранного файла%%%%%%%%%%%%%%%%%
  if strcmp(matfinfo(strcat(pathname,filename)), 'MAT-File')~=1, 
      fprintf(handles.User.logfile,'%s: "%s" - файл не правильного формата\n',datestr(now),filename); 
       f_ = warndlg('Неправильный формат файла', 'Ошибка!');
       waitfor(f_);
      handles.User.IndicatorToClose=true;
      guidata(hObject, handles);
      return;
   end;
    load(strcat(pathname,filename)); % Загрузить выбранный файл в память компьютера.
    %По синтаксису файл должен содержать cell-матрицу, название которой
    %DATA
    if ~exist('Table','var'),
      fprintf(handles.User.logfile,'%s: "%s" - не содержит обязательной переменной "Table"\n',datestr(now),filename); 
       f_ = warndlg('Выбранный  файл не содержит обязательной переменной "Table"', 'Ошибка!');
       waitfor(f_);
      handles.User.IndicatorToClose=true;
      guidata(hObject, handles);
      return;
    end;
    if ~iscell(Table),
      fprintf(handles.User.logfile,'%s: Неправильный тип переменной "Table" в файле "%s"\n',datestr(now),filename); 
      f_ = warndlg('Неправильный тип переменной "Table"', 'Ошибка!');
          waitfor(f_);
      handles.User.IndicatorToClose=true;
      guidata(hObject, handles);
      return;
    end;
    
    
 %%%%%%%%%%%%Перевод загруженных данных в строковый тип данных   
 if ~iscellstr(Table),
 Size_of_Table=size(Table);
 Table=Table(:);
 for k=1:length(Table(:)),      %Этот цикл каким-то образом можно заменить для быстроты работы программыы???
     Table{k}=num2str(Table{k});
 end;
 Table=reshape(Table,Size_of_Table(1),Size_of_Table(2));
 end;
 
 if ~iscellstr(FactorTypes),
 Size_of_Fypes=size(FactorTypes);
 FactorTypes=FactorTypes(:);
 for k=1:length(FactorTypes(:)),  %Этот цикл каким-то образом можно заменить для быстроты работы программыы???
     FactorTypes{k}=num2str(FactorTypes{k});
 end;
 FactorTypes=reshape(FactorTypes,Size_of_Fypes(1),Size_of_Fypes(2));
 end;
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
  handles.User.SelectedFactorTypesEX=FactorTypes;
  handles.User.SelectedTableEX=Table;
  handles.User.SelectedFactorNamesEX=FactorNames;
  NumFactors_Boolean=strcmpi([handles.User.SelectedFactorTypesEX(1,1:end)],'num');
  
 res=true;
 for k=1:length(FactorNames),
    res=res&&any(strcmpi(FactorNames{k},handles.User.SelectedFactorNames));
 end;
 if ~res,
 fprintf(handles.User.logfile,'%s: Ошибка: матрицы встречаемости вычислены для набора факторов, отличающегося от набора факторов используемого для картирования\n',datestr(now)); 
 f_ = warndlg('Проверьте выбранные факторы в окне ECOMAP', 'Ошибка!');
 waitfor(f_);
 handles.User.IndicatorToClose=true;
 guidata(hObject, handles);
 return;


 end;
  
  handles.User.SelectedFactorTypes=FactorTypes(:,~NumFactors_Boolean);
  handles.User.SelectedFactorNames=FactorNames(~NumFactors_Boolean);
  handles.User.SelectedTable=Table(:,~NumFactors_Boolean);
 
  
        case   'Нет'
          fprintf(handles.User.logfile,'%s: Для картирования необходимо не менее двух числовых факторов.\n',datestr(now)); 
          f_ = warndlg('Для картирования необходимо не менее двух числовых факторов', 'Ошибка!');
          waitfor(f_);
          handles.User.IndicatorToClose=true;
          guidata(hObject, handles);
          return;
    end;
end;
%-----------------------------------------------------

handles.User.SelectedNumFactors=handles.User.SelectedFactorNamesEX(NumFactors_Boolean,1);

set(handles.popupmenu1,'String',handles.User.SelectedNumFactors);
set(handles.popupmenu1,'Value',1);

set(handles.popupmenu4,'String',handles.User.SelectedNumFactors);
set(handles.popupmenu4,'Value',2);


% Реализация процедуры кластеризации полученных матриц вероятностей
% В результате кластеризации для каждой картируемой точки определяется
% номер кластера к которой она принадлежит.
Chandle=linkagequestion;
waitfor(Chandle);

fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
fprintf(handles.User.logfile,'%s: Выполняется кластеризация данных\n',datestr(now));
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);

TheFunctionIsJaccard=strcmp(char(handles.User.UserFunction),'c/(a+b-c)');
 % Вычисление по матрице вероятностей 
        % взаимозависимости факторов на основе функции, определенной
        % пользователем (под кнопкой выбора файла данных)
Wbar=waitbar(0,'Сканирование массива данных...');   
Factor_Indeces=zeros(length(handles.User.SelectedFactorTypes(1,:)),1);% Определение массива индексов градаций факторов для текущей точки
Sopr_matrix =zeros(length(Factor_Indeces)*(length(Factor_Indeces)-1)/2,length( handles.User.SelectedTable(:,1)));  
ToDisplay=true(length( handles.User.SelectedTable(:,1)),1);

for k=1:length( handles.User.SelectedTable(:,1)),
         waitbar(k/length(handles.User.SelectedTable(:,1)),Wbar);   
         % Нахождение вектора с номерами текущих для данной точки градаций
         % факторов (Factor_Indeces);
  ToCompare=repmat(handles.User.SelectedTable(k,1:end),length(handles.User.SelectedFactorTypes(2:end,1)),1);
  res=strcmpi(handles.User.SelectedFactorTypes(2:end,:),ToCompare);
  ToGenerate=repmat((1:1:length(handles.User.SelectedFactorTypes(2:end,1)))',1,length(handles.User.SelectedFactorTypes(1,:)));
  Factor_Indeces=ToGenerate(res);
        
%Вычисление массива матриц сопряженности, расчитанного на основе определенной функции пользователем
if  length(Factor_Indeces)==length(handles.User.SelectedFactorTypes(1,:)),
    f_variants=combntns(1:length(Factor_Indeces(:,1)),2);
    index_sopr=1;
    for k1=1:1:length(Factor_Indeces),
        for k2=k1+1:1:length(Factor_Indeces),
 
    numofP=1:1:length(f_variants(:,1));
    numofP=numofP(1,(f_variants(:,1)==k1)&(f_variants(:,2)==k2));     
    numofP=strcat('P',num2str(numofP));
    W=handles.User.ProbabilityMatrices.(numofP);

    c=W(Factor_Indeces(k1,1),Factor_Indeces(k2,1));
    a=sum(W(Factor_Indeces(k1,1),:));
    b=sum(W(:,Factor_Indeces(k2,1)));

    if TheFunctionIsJaccard,
        Sopr_matrix(index_sopr,k)=c/(a+b-c);
    else
    Sopr_matrix(index_sopr,k)=handles.User.UserFunction(a,b,c);
    end;
    index_sopr=index_sopr+1;
    end;
    end;

else
    fprintf(handles.User.logfile,'%s: Строка картируемых данных %d пропущена (содержит неопределенную градацию)\n',datestr(now),k);  
    ToDisplay(k,1)=false; 
end;   

end;
close(Wbar);
fprintf(handles.User.logfile,'%s: Построение массива классифицируемых матриц завершено\n',datestr(now));  
fprintf(handles.User.logfile,'%s: Пропущено %d записей\n',datestr(now),sum(~ToDisplay));  
%%%%%%%%%%%%%%%%%%Технология создания классов%%%%%%%%%%%%%%%%%

if exist('ouYekd3hfEgm7.mat','file'),
load ouYekd3hfEgm7;else res=0;end;
switch res,
    case 1, Linkageparametr='single';
    case 2, Linkageparametr='complete';
    case 3, Linkageparametr='centroid';
    case 4, Linkageparametr='average';
    otherwise
        Linkageparametr='complete';
end;

%%%%%%%%%%%%%%Выбор метода кластеризации данных%%%%%%%%%%%%%%%%%%%%%%
switch handles.User.SelectedClusteringMethod,
    case 1, % Вписать процедуру кластеризации данных, встроенную в MatLab (организовать ее вызов)
        distances_Y=pdist(Sopr_matrix','euclidean');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));
    case 2,
      distances_Y=pdist(Sopr_matrix','cityblock');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));   
    case 3,
        distances_Y=pdist(Sopr_matrix','minkowski');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));   
    case 4,
         distances_Y=pdist(Sopr_matrix','mahalanobis');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));   
     case 5,
         distances_Y=pdist(Sopr_matrix','hamming');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));   
    case 6,
         distances_Y=pdist(Sopr_matrix','jaccard');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));  
     case 7,
         distances_Y=pdist(Sopr_matrix','cosine');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));   
    case 8,
         distances_Y=pdist(Sopr_matrix','chebychev');
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));   
    case 9,  
         distances_Y=zeros(length(Sopr_matrix(1,:)));
          Wbar=waitbar(0,'Кластеризация данных...');   
        for s1=1:length(Sopr_matrix(1,:)),
            waitbar(s1/length(handles.User.SelectedTable(:,1)),Wbar); 
            for s2=s1+1:length(Sopr_matrix(1,:)),
                 distances_Y(s1,s2)=handles.User.UserClusteringFunction(Sopr_matrix(:,s1),Sopr_matrix(:,s2));
                 distances_Y(s2,s1)=distances_Y(s1,s2);
            end;
        end;
        distances_Y=squareform(distances_Y); 
        C_Out=linkage(distances_Y,Linkageparametr);
        clear distances_Y;
        Cluster_out=cluster(C_Out,'MaxClust',double(handles.User.NumberOfClusters));
        close(Wbar);
      
end;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% L_N=length(handles.User.SelectedNumFactors(:,1));
if exist('Cluster_out','var'), 
    handles.User.SelectedNumFactors{end+1,1}='Кластеры';
    handles.User.Cluster_out=Cluster_out;
end;
handles.User.ToDisplay=ToDisplay;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Update handles structure
guidata(hObject, handles);
% UIWAIT makes map wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = map_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;
varargout{2} = handles.User;


% --- Executes on selection change in popupmenu1.
function popupmenu1_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns popupmenu1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu1


% --- Executes during object creation, after setting all properties.
function popupmenu1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



% --- Executes on selection change in popupmenu2.
function popupmenu2_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns popupmenu2 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu2


% --- Executes during object creation, after setting all properties.
function popupmenu2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in popupmenu3.
function popupmenu3_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns popupmenu3 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu3


% --- Executes during object creation, after setting all properties.
function popupmenu3_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

CheckFills=get(handles.checkbox1,'Value');
CheckBox=get(handles.checkbox3,'Value');
CheckDiamond=get(handles.checkbox2,'Value');
CheckCircle=get(handles.checkbox4,'Value');
CheckStar=get(handles.checkbox5,'Value');
CheckSmoothing=get(handles.checkbox6,'Value');

if CheckBox,
        SymbolType='s';
end;
if CheckDiamond,
        SymbolType='d';
end;
if CheckCircle,
        SymbolType='o';
end;
if CheckStar,
        SymbolType='*';
end;



ValueX=get(handles.popupmenu1,'Value');
ValueY=get(handles.popupmenu4,'Value');

NameX=get(handles.popupmenu1,'String');
NameY=get(handles.popupmenu4,'String');

NameX=NameX{ValueX,1};
NameY=NameY{ValueY,1};

for k=1:length(handles.User.SelectedFactorTypesEX(1,:)),
  
  if strcmpi(NameX,handles.User.SelectedFactorNamesEX{k,1}),
      IndX=k;
  end;
  if strcmpi(NameY,handles.User.SelectedFactorNamesEX{k,1}),
      IndY=k;
  end;
    
end;
%%%%%%%%%%%%%%%%Подготовка к построению карты кластерных отношений.%%%%%%%%%%%
XX=str2num(char(handles.User.SelectedTableEX(:,IndX)));
YY=str2num(char(handles.User.SelectedTableEX(:,IndY)));

CLASS_out=handles.User.Cluster_out;

if CheckSmoothing, 
    %Дополнительная процедура осреднения 
    knn_number=get(handles.slider2,'Value');
    knn_number=fix(knn_number*100)+10;
    CLASS_out = knnclassify([XX YY],[XX YY],handles.User.Cluster_out,knn_number);

end;

XX=XX(handles.User.ToDisplay);
YY=YY(handles.User.ToDisplay);
CLASS_out=CLASS_out(handles.User.ToDisplay);
SQR=get(handles.slider1,'Value');
SQR=SQR*200;


if CheckFills,
    if ~CheckStar,
    scatter(XX,YY,SQR, CLASS_out,SymbolType,'filled');
    else
    scatter(XX,YY,SQR, CLASS_out,SymbolType);
    end;
else
    scatter(XX,YY,SQR, CLASS_out,SymbolType);
end;

guidata(hObject, handles);

% --- Executes on selection change in popupmenu4.
function popupmenu4_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hints: contents = get(hObject,'String') returns popupmenu4 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu4


% --- Executes during object creation, after setting all properties.
function popupmenu4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



% --- Executes on button press in checkbox1.
function checkbox1_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of checkbox1


% --- Executes on slider movement.
function slider1_Callback(hObject, eventdata, handles)
% hObject    handle to slider1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider


% --- Executes during object creation, after setting all properties.
function slider1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slider1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on button press in checkbox2.
function checkbox2_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of checkbox2
set(handles.checkbox3,'Value',0);
set(handles.checkbox4,'Value',0);
set(handles.checkbox5,'Value',0);



% --- Executes on button press in checkbox3.
function checkbox3_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of checkbox3
set(handles.checkbox2,'Value',0);
set(handles.checkbox4,'Value',0);
set(handles.checkbox5,'Value',0);

% --- Executes on button press in checkbox4.
function checkbox4_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of checkbox4
set(handles.checkbox2,'Value',0);
set(handles.checkbox3,'Value',0);
set(handles.checkbox5,'Value',0);

% --- Executes on button press in checkbox5.
function checkbox5_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of checkbox5
set(handles.checkbox2,'Value',0);
set(handles.checkbox3,'Value',0);
set(handles.checkbox4,'Value',0);



% --------------------------------------------------------------------
function ASaveAs_Callback(hObject, eventdata, handles)
% hObject    handle to ASaveAs (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
CheckFills=get(handles.checkbox1,'Value');
CheckBox=get(handles.checkbox3,'Value');
CheckDiamond=get(handles.checkbox2,'Value');
CheckCircle=get(handles.checkbox4,'Value');
CheckStar=get(handles.checkbox5,'Value');
CheckSmoothing=get(handles.checkbox6,'Value');
NewFigureHandle=figure;
if CheckBox,
        SymbolType='s';
end;
if CheckDiamond,
        SymbolType='d';
end;
if CheckCircle,
        SymbolType='o';
end;
if CheckStar,
        SymbolType='*';
end;


ValueX=get(handles.popupmenu1,'Value');
ValueY=get(handles.popupmenu4,'Value');

NameX=get(handles.popupmenu1,'String');
NameY=get(handles.popupmenu4,'String');

NameX=NameX{ValueX,1};
NameY=NameY{ValueY,1};

for k=1:length(handles.User.SelectedFactorTypesEX(1,:)),
    
  if strcmpi(NameX,handles.User.SelectedFactorNamesEX{k,1}),
      IndX=k;
  end;
  if strcmpi(NameY,handles.User.SelectedFactorNamesEX{k,1}),
      IndY=k;
  end;
    
end;
XX=str2num(char(handles.User.SelectedTableEX(:,IndX)));
YY=str2num(char(handles.User.SelectedTableEX(:,IndY)));
if CheckSmoothing, 
    %Дополнительная процедура осреднения 
    knn_number=get(handles.slider2,'Value');
    knn_number=fix(knn_number*100)+10;
    CLASS_out = knnclassify([XX YY],[XX YY],handles.User.Cluster_out,knn_number);
else CLASS_out=handles.User.Cluster_out;end  ;

SQR=get(handles.slider1,'Value');
SQR=SQR*200;

XX=XX(handles.User.ToDisplay);
YY=YY(handles.User.ToDisplay);
CLASS_out=CLASS_out(handles.User.ToDisplay);

if CheckFills,
    if ~CheckStar,
    scatter(XX,YY,SQR,CLASS_out,SymbolType,'filled');
    else
    scatter(XX,YY,SQR, CLASS_out,SymbolType);
    end;
else
    scatter(XX,YY,SQR, CLASS_out,SymbolType);
end;

% --------------------------------------------------------------------
function AFirstFie_Callback(hObject, eventdata, handles)
% hObject    handle to AFirstFie (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function Aexit_Callback(hObject, eventdata, handles)
% hObject    handle to Aexit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
close('map');


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the figure
delete('ouYekd3hfEgm7.mat');
delete(hObject);


% --- Executes on button press in checkbox6.
function checkbox6_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox6


% --- Executes on slider movement.
function slider2_Callback(hObject, eventdata, handles)
% hObject    handle to slider2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider


% --- Executes during object creation, after setting all properties.
function slider2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slider2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


