#### import the simple module from the paraview
paraview_exists = False
try:
    from paraview.simple import *
    paraview_exists = True
except ImportError:
    pass
#### disable automatic camera reset on 'Show'


if paraview_exists:
    paraview.simple._DisableFirstRenderCameraReset()
    import random
    res = []
    for i in range(10):
        # create a new 'Cone'
        cone1 = Cone()
        # Properties modified on cone1
        cone1.Radius = random.randint(1, 10)
        cone1.Height = random.randint(5, 15)
        cone1.Center = [random.randint(0,20), random.randint(0,30), 0.0]
        cone1.Direction = [0.0, 0.0, 1.0]
        cone1.Resolution = 100
        renderView1 = GetActiveViewOrCreate('RenderView')
        cone1Display = GetDisplayProperties(cone1, view=renderView1)
        cone1Display.DiffuseColor = [random.random(), random.random(), 0.0]
        res.append(cone1)

