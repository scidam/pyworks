import vtk
 
# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
 
# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
 
# create source
source = vtk.vtkPlaneSource()
source.SetCenter(0,0,0)
source.SetNormal(0,0,1)
source.SetResolution(10,10)

cylinderActor.GetProperty().SetColor(color)

 
# mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(source.GetOutputPort())
 
 
 
axes = vtk.vtkAxesActor()

 
# actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)


 
#transform = vtk.vtkTransform()
#transform.RotateZ(-90)
#transform.RotateX(90)
#actor.SetUserTransform(transform)

 
# assign actor to the renderer
ren.AddActor(actor)
ren.AddActor(axes) 
# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()