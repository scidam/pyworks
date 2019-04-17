#!/usr/bin/env python
 
# This simple example shows how to do basic rendering and pipeline
# creation.
import vtk
# The colors module defines various useful colors.
from vtk.util.colors import tomato,cobalt
import numpy as np 

DEFAULT_CYL_RES=50
DEFAULT_RES = 30

STACK = []
def plotcylinder(c,color=tomato):
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetResolution(DEFAULT_CYL_RES)
    cylinder.SetRadius(c.r)
    cc = c.o+c.l*(c.b+c.a)/2.0
    cc = cc.tolist()
    transform = vtk.vtkTransform()
    transform.Translate(*(cc[0],cc[1],cc[2]))
    transform.RotateX(np.arccos(c.l[0])/np.pi*180)
    transform.RotateY(np.arccos(c.l[1])/np.pi*180)
    transform.RotateZ(np.arccos(c.l[2])/np.pi*180)
    transform.Translate(*(-cc[0],-cc[1],-cc[2]))
    cylinder.SetCenter(*cc)
    cylinder.SetHeight(abs(c.b-c.a))
    cylinderMapper = vtk.vtkPolyDataMapper()
    cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
#     cylinderMapper.SetInputConnection(transformPD.GetOutputPort())
    cylinderActor = vtk.vtkActor()
    cylinderActor.SetUserTransform(transform)
    cylinderActor.GetProperty().SetColor(color)
    cylinderActor.SetMapper(cylinderMapper)
    STACK.append(cylinderActor)



def addpoints(mypoints, color=tomato):
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    for item in mypoints:
        id = points.InsertNextPoint(*item)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(id)
    point = vtk.vtkPolyData()
    point.SetPoints(points)
    point.SetVerts(vertices)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(point)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(2)
    actor.GetProperty().SetColor(color)
    STACK.append(actor)


def addspheres(spheres,color=(1,0,0)):
    mapper = list()
    _spheres = list()
    _actors =  list()
    for ind,item in enumerate(spheres):
        source = vtk.vtkSphereSource()
        source.SetPhiResolution(DEFAULT_RES)
        source.SetThetaResolution(DEFAULT_RES)
        source.SetCenter(item[0],item[1],item[2])
        source.SetRadius(item[3])
        _spheres.append(source)
        _actors.append(vtk.vtkActor())
        mapper.append(vtk.vtkPolyDataMapper())
        mapper[-1].SetInputConnection(_spheres[-1].GetOutputPort())
        _actors[-1].SetMapper(mapper[-1])
        _actors[-1].GetProperty().SetColor(color)
    STACK.extend(_actors)


def render(c):
    ren = vtk.vtkRenderer()
    for item in STACK:
        ren.AddActor(item)
    ren.SetBackground(0.1, 0.2, 0.4)
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    renWin.SetSize(200, 200)
    iren.Initialize()
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.5)
    renWin.Render()
    iren.Start()
    
    
     

    