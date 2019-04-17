function varargout = ecomap(varargin)
% ECOMAP M-file for ecomap.fig
%      ECOMAP, by itself, creates a new ECOMAP or raises the existing
%      singleton*.
%
%      H = ECOMAP returns the handle to a new ECOMAP or the handle to
%      the existing singleton*.
%
%      ECOMAP('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in ECOMAP.M with the given input arguments.
%
%      ECOMAP('Property','Value',...) creates a new ECOMAP or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before ecomap_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to ecomap_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help ecomap

% Last Modified by GUIDE v2.5 23-Jul-2009 22:26:49

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @ecomap_OpeningFcn, ...
                   'gui_OutputFcn',  @ecomap_OutputFcn, ...
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


% --- Executes just before ecomap is made visible.
function ecomap_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to ecomap (see VARARGIN)

% Choose default command line output for ecomap
handles.output = hObject;

handles.User.data_FactorNames=cell(1,1);
handles.User.data_Table=cell(1,1);

%%%%%%%%%%%%%Разметка log- файла%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
handles.User.STR_long_minus='---------------------------------------------------------------------------------------------------------------------------------------------';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

fid_log=fopen('log.log','wt');
handles.User.logfile=fid_log;

%%%%%%%%%%%%%%Начало записи log-файла%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
fprintf(handles.User.logfile,'Начата сессия: %s\n', datestr(now));
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes ecomap wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = ecomap_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
[filename, pathname] = uigetfile({'*.mat'},'File Selector');
handles.User.Inputfilename=filename;
handles.User.Inputpathname=pathname;
% uicontrol('Parent', fig2, 'Style', 'edit','String','hello');
if ~ischar(filename), filename='?';  set(hObject,'String','Открыть файл данных'); 
clear FactorNames Table FactorTypes;
set(handles.pushbutton6,'Enable','inactive');
set(handles.listbox1,'String','');
set(handles.listbox4,'String','');
return; 
else
fprintf(handles.User.logfile,'%s: Выбран файл: "%s" \n',datestr(now),filename);
end;
%%%%%%%%%%%%%%%%Проверка файла на правильность%%%%%%%%%%%%%%%%%%%
if strcmp(matfinfo(strcat(pathname,filename)), 'MAT-File')~=1, 
      fprintf(handles.User.logfile,'%s: "%s" - файл неверного формата\n',datestr(now),filename); 
      set(handles.pushbutton6,'Enable','inactive');
      set(handles.listbox1,'String','');
 return;
else
set(handles.text8,'Visible','on');
pause(0.1);
load(strcat(pathname,filename));
set(handles.text8,'Visible','off');

fprintf(handles.User.logfile,'%s:  Файл данных "%s" успешно загружен\n',datestr(now),filename);  
set(handles.pushbutton6,'Enable','on');
end;
if ~exist('Table'), 
    fprintf(handles.User.logfile,'%s:  Файл  не содержит обязательной переменной "Table"\n',datestr(now));
    filename='Открыть файл данных';  set(hObject,'String',filename); return; end;

if isempty('Table'), 
       fprintf(handles.User.logfile,'%s:  Загруженный файл "%s"  не содержит данных\n',datestr(now),filename);
    filename='Открыть файл данных';  set(hObject,'String',filename); return; end;

if  min(size(Table))==1,
       fprintf(handles.User.logfile,'%s:  Переменная "Table" должна быть матрицей\n',datestr(now));
    filename='Открыть файл данных';  set(hObject,'String',filename); return; end;

if  ~iscell(Table),
    fprintf(handles.User.logfile,'%s:  Переменная "Table" должна иметь тип "cell"\n',datestr(now));
    filename='Открыть файл данных';  set(hObject,'String',filename); return; end;
 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%Анализ переменной FactorNames%%%%%%%%%%%%%%%%%%%%%

fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
fprintf(handles.User.logfile,'%s:  Общая проверка корректности файла "%s" завершена\n',datestr(now),filename);
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);

if ~exist('FactorNames','var'),
fprintf(handles.User.logfile,'%s:  Переменная "FactorNames" отсутствует\n',datestr(now)); 
    for k=1:length(Table(1,:)),
    FactorNames(k,1)={num2str(k)};
    end;
 fprintf(handles.User.logfile,'%s: Названия факторов ("FactorNames") даны по умолчанию от "1" до "%d"\n',datestr(now),length(Table(1,:))); 
else

 fprintf(handles.User.logfile,'%s: Анализ переменной "FactorNames", определенной в файле данных\n',datestr(now));


flag=false;

for k=1:length(FactorNames(:,1)),
    for j=k+1:length(FactorNames(:,1)),
    if  strcmpi(num2str(FactorNames{k,1}),num2str(FactorNames{j,1})),
         fprintf(handles.User.logfile,'%s: Фактор "%s" встречается более одного раза\n',datestr(now),num2str(FactorNames{k,1})); 
         flag=true;
    end;
    end;
end;

if flag==true,
    fprintf(handles.User.logfile,'%s:  Переменная "FactorNames" будет заменена по умолчанию\n',datestr(now)); 
    for k=1:length(Table(1,:)),
    FactorNames(k,1)={num2str(k)};
    end;
 fprintf(handles.User.logfile,'%s: Названия факторов ("FactorNames") даны по умолчанию от "1" до "%d"\n',datestr(now),length(Table(1,:)));
end;
end;


%%%%%%%%%%%%%%Анализ альтернативной перемнной FactorTypes%%%%%%%%%%%%%%%%%%%%
if ~exist('FactorTypes','var'),
    
 fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
 fprintf(handles.User.logfile,'%s:  Переменная "FactorTypes" отсутствует\n',datestr(now)); 
 fprintf(handles.User.logfile,'%s:  Переменная "FactorTypes"  будет построена по таблице данных:\n',datestr(now)); 
 fprintf(handles.User.logfile,'все данные имеют категоризированный тип, градации определяются из таблицы данных\n'); 
 fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
 
 for k=1:length(Table(1,:)),
    FactorTypes(1,k)={'CaT'}; % Флаг категоризированного типа данных
 end;
 fprintf(handles.User.logfile,'%s: Всем факторам присвоен категоризированный тип данных\n',datestr(now)); 

 if  length(FactorTypes(1,:))~=length(FactorNames(:,1)), 
fprintf(handles.User.logfile,'%s:  Неправильно определен массив  "FactorTypes"  или "FactorNames" \n',datestr(now)); 
return;
 end;
 
%%%%%%%%%%%%%%Построение переменной
%%%%%%%%%%%%%%FactorTypes%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
 fprintf(handles.User.logfile,'%s:  Построение переменной FactorTypes \n',datestr(now)); 
Wbar=waitbar(0,'Построение массива факторов...');
 for k=1:length(Table(1,:)),
[res,nans]=GetFactorsFromVector(Table(:,k));
 waitbar(k/length(Table(1,:)),Wbar);   
if ~isempty(res),  
    FactorTypes(2:length(res)+1,k)=res; 
end;

      fprintf(handles.User.logfile,'Фактор "%s" содержит %d градаций; Пропущено %d позиций\n',FactorNames{k,1},length(res),sum(nans)); 
 end;
 close(Wbar);
  fprintf(handles.User.logfile,'Общее число строк описаний %d\n',length(Table(:,1)));
  fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else
    
   fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus); 
   fprintf(handles.User.logfile,'%s: Анализ массива "FactorTypes", определенной пользователем\n',datestr(now));
   fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
    
    %%%%%%%%%%%%%%%%%Анализ FactorTypes, заданного в файле данных%%%%%%%%%%
 if (length(FactorTypes(1,:))~=length(FactorNames(:,1)))||(length(FactorTypes(:,1))<2), 
          fprintf(handles.User.logfile,'%s:  Неправильно определен массив  "FactorTypes" \n',datestr(now)); 
          
          %%%%%%%%%%%%%%Построение переменной FactorTypes

 fprintf(handles.User.logfile,'%s:  Переменная "FactorTypes" будет построена по таблице данных \n',datestr(now)); 
Wbar=waitbar(0,'Построение массива факторов...');
 for k=1:length(Table(1,:)),

[res,nans]=GetFactorsFromVector(Table(:,k));
 waitbar(k/length(Table(1,:)),Wbar);
if ~isempty(res),FactorTypes(2:length(res)+1,k)=res; end;

      fprintf(handles.User.logfile,'Фактор "%s" содержит %d градаций; Пропущено %d позиций\n',FactorNames{k,1},length(res),sum(nans)); 
 end;
close(Wbar);
  fprintf(handles.User.logfile,'Общее число строк описаний %d\n',length(Table(:,1)));
  fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    end;
    
Wbar=waitbar(0,'Анализ переменной "FactorTypes"...'); 
for k=1:length(FactorTypes(1,:)),
     waitbar(k/length(FactorTypes(1,:)),Wbar);
      if  ~strcmpi(num2str(FactorTypes{1,k}),'num')&&~strcmpi(num2str(FactorTypes{1,k}),'cat'), 
   
          fprintf(handles.User.logfile,'%s: Для фактора "%s"  указан неправильный тип; изменен по умолчанию: категория\n',datestr(now),FactorNames{k,1}); 
      FactorTypes{1,k}='cat';% присвоение неверно определенному типу типа "категория".
      end;
      
 if strcmpi(num2str(FactorTypes{1,k}),'num'), 
     %Градации должны быть только целые!!!
IsEmptyFactor=false;   
for j=2:length(FactorTypes(:,k)),
    
    if ischar(FactorTypes{j,k}),
              if ~(ceil(str2double((FactorTypes{j,k})))==floor(str2double((FactorTypes{j,k})))), 
              fprintf(handles.User.logfile,'%s: Фактор "%s"  числового типа имеет нецелую градацию %s\n',datestr(now),FactorNames{k,1}, num2str(FactorTypes{j,k})); 
              fprintf(handles.User.logfile,'%s: Градации %s установлено пустое значение \n',datestr(now), num2str(FactorTypes{j,k})); 
              FactorTypes{j,k}=[];
              end;
    end;
    
     if isnumeric(FactorTypes{j,k}),
              if ~(ceil(((FactorTypes{j,k})))==floor(((FactorTypes{j,k})))), 
              fprintf(handles.User.logfile,'%s: Фактор "%s"  числового типа имеет нецелую градацию %s\n',datestr(now),FactorNames{k,1}, num2str(FactorTypes{j,k})); 
              fprintf(handles.User.logfile,'%s: Градации %s установлено пустое значение \n',datestr(now), num2str(FactorTypes{j,k})); 
              FactorTypes{j,k}=[];
              end;
    end;
              
              
             if isempty(FactorTypes{j,k}), 
                  IsEmptyFactor=true;   
             end;
     
end;
          
if  IsEmptyFactor==true,
fprintf(handles.User.logfile,'%s: Числовой фактор "%s"  не имеет градаций \n',datestr(now),FactorNames{k,1}); 
end;
  
end;

%%%%%%%%%%%%%Здесь необходимо вставить код, завершающий фильтрацию j-го
%%%%%%%%%%%%%столбца переменной FactorTypes

      
end;
close(Wbar);
  
    
    
  end;

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%%%%%%%%%%Все загруженные данные конвертируются в cellstr - arrays 
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
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
set(handles.listbox1,'String',FactorNames);
handles.User.data_FactorNames=FactorNames;
handles.User.data_Table=Table;
handles.User.data_FactorTypes=FactorTypes;
set(gcbo,'String',filename); 
set(handles.text8,'Visible','off');
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function pushbutton1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --- Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called



function edit2_Callback(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hints: get(hObject,'String') returns contents of edit2 as text
%        str2double(get(hObject,'String')) returns contents of edit2 as a double
Str_F=get(hObject,'String');
Function=inline(Str_F);
if sum(Str_F=='a')==0||sum(Str_F=='b')==0||sum(Str_F=='c')==0, set(gcbo,'String','Некорректная функция'); 
    Function=inline('c/(a+b-c)','a','b','c');
   f_ = warndlg('Использована мера сходства Жаккара', 'Внимание');
   waitfor(f_);
end;
if length(symvar(Function))~=3, 
    set(gcbo,'String','Некорректная функция'); 
    Function=inline('c/(a+b-c)','a','b','c');
   f_ = warndlg('Использована мера сходства Жаккара', 'Внимание');
   waitfor(f_);
end;
handles.User.UserFunction=Function;
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function edit2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
Str_F=get(hObject,'String');Function=inline(Str_F);
handles.User.UserFunction=Function;
guidata(hObject, handles);

% --- Executes on selection change in listbox1.
function listbox1_Callback(hObject, eventdata, handles)
% hObject    handle to listbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns listbox1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from listbox1




% --- Executes during object creation, after setting all properties.
function listbox1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to listbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object deletion, before destroying properties.
function listbox1_DeleteFcn(hObject, eventdata, handles)
% hObject    handle to listbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- If Enable == 'on', executes on mouse press in 5 pixel border.
% --- Otherwise, executes on mouse press in 5 pixel border or over listbox1.
function listbox1_ButtonDownFcn(hObject, eventdata, handles)
% hObject    handle to listbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on selection change in listbox2.
function listbox2_Callback(hObject, eventdata, handles)
% hObject    handle to listbox2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns listbox2 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from listbox2
num = get(hObject,'Value');


% switch num,
%        
% end;

if num==length(get(hObject,'String')), set(handles.text6,'Visible','on');set(handles.edit3,'Visible','on'); 
else  set(handles.text6,'Visible','off');set(handles.edit3,'Visible','off'); 
end;



% --- Executes during object creation, after setting all properties.
function listbox2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to listbox2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end




% --- Executes during object creation, after setting all properties.
function edit3_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object creation, after setting all properties.
function edit4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object creation, after setting all properties.
function listbox4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to listbox4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton3.
function pushbutton3_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
num = get(handles.listbox1,'Value');
Current_OUT=get(handles.listbox1,'String');
if isempty(Current_OUT), return; end;

Current_IN=get(handles.listbox4,'String');
if isempty(Current_IN), 
    Current_IN=cell(1,1); Current_IN(1,1)=Current_OUT(num); 
else Current_IN(length(Current_IN)+1)=Current_OUT(num);
end;

Current_OUT=Current_OUT(1:1:length(Current_OUT)~=num);
set(handles.listbox4,'String',Current_IN);
set(handles.listbox1,'String',Current_OUT);
set(handles.listbox1,'Value',1);
set(handles.listbox4,'Value',1);
handles.User.CheckToMapping=false;
guidata(hObject, handles);

% --- Executes on button press in pushbutton4.
function pushbutton4_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

num = get(handles.listbox1,'Value');
Current_OUT=get(handles.listbox1,'String');
if isempty(Current_OUT), return; end;

Current_IN=get(handles.listbox4,'String');

if isempty(Current_IN), 
    Current_IN=Current_OUT;
else
    Current_IN(length(Current_IN)+1:length(Current_IN)+length(Current_OUT))=Current_OUT;
end;
Current_OUT={};

set(handles.listbox4,'String',Current_IN);
set(handles.listbox1,'String',Current_OUT);
set(handles.listbox1,'Value',1);
set(handles.listbox4,'Value',1);
handles.User.CheckToMapping=false;
guidata(hObject, handles);

% --- Executes on button press in pushbutton5.
function pushbutton5_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
num = get(handles.listbox4,'Value');
Current_OUT=get(handles.listbox4,'String');
if isempty(Current_OUT), return; end;

Current_IN=get(handles.listbox1,'String');
if isempty(Current_IN), 
    Current_IN=cell(1,1); Current_IN(1,1)=Current_OUT(num); 
else Current_IN(length(Current_IN)+1)=Current_OUT(num);
end;

Current_OUT=Current_OUT(1:1:length(Current_OUT)~=num);
set(handles.listbox1,'String',Current_IN);
set(handles.listbox4,'String',Current_OUT);
set(handles.listbox4,'Value',1);
set(handles.listbox1,'Value',1);
handles.User.CheckToMapping=false;
guidata(hObject, handles);


% --- Executes on button press in pushbutton6.
function pushbutton6_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
set(handles.listbox4,'Value',1);
Current_OUT={};
set(handles.listbox4,'String',Current_OUT);
if ~isempty(handles.User.data_FactorNames{1,1}),
set(handles.listbox1,'String',handles.User.data_FactorNames);
end;



 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% --- Executes during object deletion, before destroying properties.
function figure1_DeleteFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

 fprintf(handles.User.logfile,'%s:  Работа с программой завершена',datestr(now)); 
 fclose(handles.User.logfile); 


% --- Executes on button press in pushbutton7.
function pushbutton7_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton7 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
dos('notepad log.log'); % Просмотр Блокнотом лога...


% --- Executes on button press in pushbutton8.
function pushbutton8_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton8 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

CurrentFactors=get(handles.listbox4,'String');
if isempty(CurrentFactors),
%    state_of_the_window = uisuspend(gcf);
   f_ = warndlg('Не определен список анализируемых факторов', 'Ошибка');
   waitfor(f_);
%    uirestore(state_of_the_window);
   fprintf(handles.User.logfile,'%s: Не определен список анализируемых факторов. Анализ не выполнен.\n',datestr(now));    
   return;
end;

if max(size(CurrentFactors))<2,
 fprintf(handles.User.logfile,'%s: Необходимо выбрать не менее двух факторов\n',datestr(now));    
% state_of_the_window = uisuspend(gcf);
f_ = warndlg('Необходимо выбрать не менее двух факторов', 'Ошибка');
waitfor(f_);
% uirestore(state_of_the_window);
 return;
end;

%%%%%%%%%%%%%%%%Выполнение предварительного макроанализа взаимозависимости
%%%%%%%%%%%%%%%%факторов. Анализ выполняется только для факторов, выбранных
%%%%%%%%%%%%%%%%во втором  списке%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

FactorNames=handles.User.data_FactorNames;
FactorTypes=handles.User.data_FactorTypes;
Table=handles.User.data_Table;

CF=false(size(FactorNames)); %Булевый набор, определяющий выбранные для анализа фаткоры
CFEX=CF;
for k=1:length(FactorNames),
     for j=1:length(CurrentFactors),
      if  strcmp(CurrentFactors{j,1},FactorNames{k,1}),
          CF(k,1)=true;
          CFEX(k,1)=true;
    if isempty(FactorTypes{2,k}),   
    fprintf(handles.User.logfile,'%s: Фактор "%s" не имеет градаций и будет искючен при анализе данных\n',datestr(now),FactorNames{k,1}); 
    CF(k,1)=false;
    end;
     end;
    end;
end;
 %%%%%%%%%%%%%%%%%%%Факторы должны иметь несколько градаций%%%%%%%%%%%%
CurrentFactorTypes=FactorTypes(:,CF);
CurrentFactorNames=FactorNames(CF,:);
CurrentTable=Table(:,CF);
 
if length(CurrentFactorNames)<2,
fprintf(handles.User.logfile,'%s: Несколько из выбранных факторов не имеют градаций\n',datestr(now));    
% state_of_the_window = uisuspend(gcf);
f_ = warndlg('Несколько из выбранных факторов не имеют градаций', 'Ошибка');
waitfor(f_);
% uirestore(state_of_the_window);
return;
end

%%%%%%%%%%%%%%%%%%%Преступить к анализу факторных отношений%%%%%%%%%%%%
  set(handles.text8,'Visible','on');
  pause(0.1);
  fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
  fprintf(handles.User.logfile,'%s: Начато вычисление матриц парных взаимозависимостей\n',datestr(now));
  fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
  fprintf(handles.User.logfile,'%s: Общее число матриц равно %d\n',datestr(now),length(CurrentFactors)*(length(CurrentFactors)-1)/2); 
  %%%%%%%%%%%%% Формирование матриц, содержащих оценки вероятностей

 factor_variants=combntns(1:1:length(CurrentFactorNames),2);
 
 for k=1:length(CurrentFactorNames), 
     for j=2:length(CurrentFactorTypes(:,k)),
         if isempty(CurrentFactorTypes{j,k}),
            factor_lengthes(k,1)=j-2; 
            break;
         else
                factor_lengthes(k,1)=j-1; %было 'j'. значение 
         end;
     end;
 end;
 
 for k=1:length(factor_variants(:,1)),
     name=strcat('P',num2str(k));
     P_matrix.(name)=zeros(factor_lengthes(factor_variants(k,1),1),factor_lengthes(factor_variants(k,2),1));
 end;
 
 Wbar=waitbar(0,'Расчет матриц парных вероятностей...');
 
for k=1:length(CurrentTable(:,1)), 
    
waitbar(k/length(CurrentTable(:,1)),Wbar);   

for j=1:length(factor_variants(:,1)),
     
     fact_1=CurrentTable{k,factor_variants(j,1)};
     fact_2=CurrentTable{k,factor_variants(j,2)};
     
%%%%%%%%%%альтернатива вычисления k1%%%%%%%%%%%%%%%%%%
ordered=1:1:(factor_lengthes(factor_variants(j,1),1)+1);
k1=ordered(strcmpi(fact_1,CurrentFactorTypes(:,factor_variants(j,1))))-1;
if isempty(k1),
fprintf(handles.User.logfile,'%s: В %d строке отсутствующее (или неопределенное) значение фактора "%s" будет проигнорировано\n',datestr(now),k,CurrentFactorNames{factor_variants(j,1),1}); 
break;
end;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%альтернатива вычисления k2%%%%%%%%%%%%%%%%%%
ordered=1:1:(factor_lengthes(factor_variants(j,2),1)+1);
k2=ordered(strcmpi(fact_2,CurrentFactorTypes(:,factor_variants(j,2))))-1;
if isempty(k2),
fprintf(handles.User.logfile,'%s: В %d строке отсутствующее (или неопределенное) значение фактора "%s" будет проигнорировано\n',datestr(now),k,CurrentFactorNames{factor_variants(j,2),1}); 
break;
end;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
name=strcat('P',num2str(j));
P_matrix.(name)(k1,k2)=P_matrix.(name)(k1,k2)+1;
     
end;

end;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close(Wbar);
set(handles.text8,'Visible','off');
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
fprintf(handles.User.logfile,'%s: Завершено вычисление матриц парных взаимозависимостей\n',datestr(now));    
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
if exist('P_matrix','var'), handles.User.ProbabilityMatrices=P_matrix; end;
if exist('CurrentFactorTypes','var'),handles.User.SelectedFactorTypes=CurrentFactorTypes; end;
if exist('CurrentFactorNames','var'),handles.User.SelectedFactorNames=CurrentFactorNames; end;
if exist('CurrentTable','var'),handles.User.SelectedTable=CurrentTable; end;

%Выделенные пользователем массивы, содержащие числовые факторы не имеющие
%градаций
handles.User.SelectedFactorNamesEX=FactorNames(CFEX,:);
handles.User.SelectedFactorTypesEX=FactorTypes(:,CFEX);
handles.User.SelectedTableEX=Table(:,CFEX);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
handles.User.CheckToMapping=true;
guidata(hObject, handles);


% --- Executes on button press in pushbutton2. %Кнопка "Построить карту".
function pushbutton2_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if ~handles.User.CheckToMapping,
fprintf(handles.User.logfile,'%s: Вычислите предварительно массив матриц встречаемости\n',datestr(now));
% state_of_the_window = uisuspend(gcf);
f_ = warndlg('Не вычислены матрицы встречаемости', 'Ошибка');
waitfor(f_);
% uirestore(state_of_the_window);
return;
end;

if   ~isfield(handles.User,'ProbabilityMatrices')||~isfield(handles.User,'SelectedFactorTypes')||...
     ~isfield(handles.User,'SelectedFactorNames')||~isfield(handles.User,'SelectedTable')||...
     isempty(get(handles.listbox4,'String')),
fprintf(handles.User.logfile,'%s: Попытка построить карту при остутствии данных\n',datestr(now));
% state_of_the_window = uisuspend(gcf);
f_ = warndlg('Не выбраны факторы или не выполнен анализ факторных отношений', 'Ошибка');
waitfor(f_);
% uirestore(state_of_the_window);
return;
else
    fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
    fprintf(handles.User.logfile,'%s: Запуск картографического приложения\n',datestr(now));
    fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
%------------------------------------------------------------------
    User.logfile=handles.User.logfile;
    User.ProbabilityMatrices=handles.User.ProbabilityMatrices;
    User.SelectedFactorNames=handles.User.SelectedFactorNames;
    User.SelectedFactorTypes=handles.User.SelectedFactorTypes;
    User.SelectedTable=handles.User.SelectedTable;
    User.SelectedTableEX=handles.User.SelectedTableEX;
    User.SelectedFactorTypesEX=handles.User.SelectedFactorTypesEX;
    User.SelectedFactorNamesEX=handles.User.SelectedFactorNamesEX;
%------------------------------------------------------------------
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
fprintf(handles.User.logfile,'%s: Расчет информационных мер: Результаты будут представлены в генерируемом отчете "Отчет.html"\n',datestr(now));

%---------------Выполнение макроанализа данных: расчет парных информационных коэффициентов и вывод файла отчета в html-виде.

factor_variants=combntns(1:1:length(handles.User.SelectedFactorNames),2);
%Посчитаем сначала 
for k=1:length(factor_variants(:,1)),
STR=strcat('P',num2str(k));
User.ProbabilityMatrices.(STR)=User.ProbabilityMatrices.(STR)/sum(sum(User.ProbabilityMatrices.(STR)));
Cur_mat=User.ProbabilityMatrices.(STR);

H_AB=undetermn(Cur_mat);
H_A=undetermn(sum(Cur_mat')); % Сумма вероятностей идет вдоль строк
H_B=undetermn(sum(Cur_mat)); % Сумма вероятностей идет вдоль столбцов

T_AB=H_A+H_B-H_AB; % Симметричный информационный коэффициент взаимозависимости

K_AB=T_AB/H_B; % Сколько инфомации содержится в "А" относительно "В"
K_BA=T_AB/H_A; % Сколько инфомации содержится в "B" относительно "A"

UNdet_matrix(k+1,2:7)={H_A H_B H_AB T_AB K_AB K_BA};
UNdet_matrix(k+1,1)={strcat('A="',User.SelectedFactorNames(factor_variants(k,1),1),'"/','B="',User.SelectedFactorNames(factor_variants(k,2),1),'"')};
end;
%--------------------------------------------------------------------------
UNdet_matrix(1,2:7)={'Мера H(A)'  'Мера H(B)'  'Мера H(AB)'  'Мера Т(AВ)'  'Коэффициент K(A;B)'  'Коэффициент K(B;A)'};
UNdet_matrix(1,1)={'Наименование фактора'};
%--------------------------------------------------------------------------
fprintf(handles.User.logfile,'%s: Расчет информационных мер успешно завершен\n',datestr(now));
fprintf(handles.User.logfile,'%s: Генерируется отсчет с вычисленными информационными мерами \n',datestr(now));
fprintf(handles.User.logfile,'%s\n',handles.User.STR_long_minus);
save infmesdta UNdet_matrix;
report ecomap;
delete('infmesdta.mat');
%--------------------------------------------------------------------------
Clusters=get(handles.edit4,'String');
Clusters=int8(str2num(Clusters));
if ~isinteger(Clusters)||Clusters>9||Clusters<1;
% state_of_the_window = uisuspend(gcf);
fprintf(handles.User.logfile,'%s: Число кластеров должно быть цифрой\n',datestr(now));
f_ = warndlg('Число кластеров должно быть цифрой', 'Ошибка');
waitfor(f_);
% uirestore(state_of_the_window);
return;
else User.NumberOfClusters=Clusters; end;
%-------------------------------------------
SelectedClusteringMethod=get(handles.listbox2,'Value');
User.SelectedClusteringMethod=SelectedClusteringMethod;
if SelectedClusteringMethod==...
length(get(handles.listbox2,'String')),

FcnStr=get(handles.edit3,'String');

        if isempty(FcnStr),
%         state_of_the_window = uisuspend(gcf);
        fprintf(handles.User.logfile,'%s: Функция кластеризации не задана\n',datestr(now));
        f_ = warndlg('Не задана функция кластеризации', 'Ошибка');
        waitfor(f_);
%         uirestore(state_of_the_window);
        return;
        end;

% state_of_the_window = uisuspend(gcf);
fprintf(handles.User.logfile,'%s: Функция кластеризации выбрана d(x,y)=%s\n',datestr(now),FcnStr);
f_ = warndlg('Проверьте правильность функции кластеризации', 'Внимание!');
waitfor(f_);
% uirestore(state_of_the_window);
        
SelectedClusteringFunction=inline(FcnStr,'x','y');
User.UserClusteringFunction=SelectedClusteringFunction;
    
end;

%-------------------------------------------
User.UserFunction=handles.User.UserFunction;
User.STR_long_minus=handles.User.STR_long_minus;
%--------------------------------------------


[output,User]=map(User);

if User.IndicatorToClose==true,
    close('map');
end;

end;


% --- Executes on selection change in listbox4.
function listbox4_Callback(hObject, eventdata, handles)
% hObject    handle to listbox4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns listbox4 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from listbox4



function edit4_Callback(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit4 as text
%        str2double(get(hObject,'String')) returns contents of edit4 as a double



function edit3_Callback(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit3 as text
%        str2double(get(hObject,'String')) returns contents of edit3 as a double
fprintf(handles.User.logfile,'%s: Задается пользовательская функция расстояния\n',datestr(now));
Str_F=get(hObject,'String');
if sum(Str_F=='x')==0||sum(Str_F=='y')==0, set(gcbo,'String','Некорректная функция'); 
    fprintf(handles.User.logfile,'%s: Ошибка в задании пользовательской функции расстояния\n',datestr(now));
    fprintf(handles.User.logfile,'%s: Использована стандартная функция - евклидово расстояние\n',datestr(now));
    f_ = warndlg('Использована функция по умолчанию', 'Внимание');
    waitfor(f_);
   set(handles.listbox2,'Value',1);
   set(handles.text6,'Visible','off');
   set(handles.edit3,'Visible','off'); 
end;
