function varargout = linkagequestion(varargin)
% LINKAGEQUESTION M-file for linkagequestion.fig
%      LINKAGEQUESTION, by itself, creates a new LINKAGEQUESTION or raises the existing
%      singleton*.
%
%      H = LINKAGEQUESTION returns the handle to a new LINKAGEQUESTION or the handle to
%      the existing singleton*.
%
%      LINKAGEQUESTION('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in LINKAGEQUESTION.M with the given input arguments.
%
%      LINKAGEQUESTION('Property','Value',...) creates a new LINKAGEQUESTION or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before linkagequestion_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to linkagequestion_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help linkagequestion

% Last Modified by GUIDE v2.5 24-Jul-2009 21:06:00

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @linkagequestion_OpeningFcn, ...
                   'gui_OutputFcn',  @linkagequestion_OutputFcn, ...
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


% --- Executes just before linkagequestion is made visible.
function linkagequestion_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to linkagequestion (see VARARGIN)

% Choose default command line output for linkagequestion
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes linkagequestion wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = linkagequestion_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1}=handles.output;


% --- Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
res=[get(handles.checkbox3,'Value');get(handles.checkbox4,'Value');get(handles.checkbox5,'Value');get(handles.checkbox6,'Value')];
x=1:1:4;
if sum(res)~=0,
    res=x(logical(res));
else
    res=1;
end;
save ouYekd3hfEgm7 res;
close(gcf);

% --- Executes on button press in checkbox3.
function checkbox3_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox3
set(handles.checkbox4,'Value',0);
set(handles.checkbox5,'Value',0);
set(handles.checkbox6,'Value',0);

% --- Executes on button press in checkbox4.
function checkbox4_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox4
set(handles.checkbox3,'Value',0);
set(handles.checkbox5,'Value',0);
set(handles.checkbox6,'Value',0);


% --- Executes on button press in checkbox5.
function checkbox5_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
set(handles.checkbox4,'Value',0);
set(handles.checkbox3,'Value',0);
set(handles.checkbox6,'Value',0);

% Hint: get(hObject,'Value') returns toggle state of checkbox5


% --- Executes on button press in checkbox6.
function checkbox6_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox6
set(handles.checkbox4,'Value',0);
set(handles.checkbox3,'Value',0);
set(handles.checkbox5,'Value',0);


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the figure
delete(hObject);


% --- Executes during object deletion, before destroying properties.
function figure1_DeleteFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


