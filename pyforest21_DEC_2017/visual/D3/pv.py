
import os
from paraview.simple import *
from pyforest.visual.D3 import Abstract3DScene
from pyforest.objects.data import ObjectDataStorage

class  ParaviewSimple3DScene(Abstract3DScene):
    '''# TODO: Used to generate array of objects via Paraview, Docs needed
    '''

    def __init__(self, model, *args, **kwargs):
        super(ParaviewSimple3DScene, self).__init__(*args, **kwargs)
        self.pipeline = []
        self.model = model
        self._params = ObjectDataStorage()
        cpath = os.path.dirname(os.path.abspath(__file__))
        self._params.autodiscover(path=os.path.join(cpath, '../settings'))
        self.ylen = self.model.bbox[1][1] - self.model.bbox[1][0]
        self.xlen = self.model.bbox[0][1] - self.model.bbox[0][0]

    def _get_display(self, geometry):
        renderView = GetActiveViewOrCreate('RenderView')
        return Show(geometry, renderView)

    def plot_base(self):
        height = self._params.get_parameter('none', 'GROUND_BOX_HEIGHT')
        base = Box()
        base.XLength = self.xlen
        base.YLength = self.ylen
        base.ZLength = height
        baseDisplay = self._get_display(base)
        baseDisplay.DiffuseColor = self._params.get_parameter('none',
                                                              'GROUND_BOX_COLOR')
        self.pipeline.append(base)

    def plot_objects(self):
        for item in self.model.objects:
            pass

    def plot_resources(self):
        pass

    def plot_relief(self):
        raise NotImplementedError

    def plot_model(self):
        for key, value in GetSources().items():
            Delete(value)
            print 'Deleted:', key, value
        self.plot_base()
        renderView = GetActiveViewOrCreate('RenderView')
        self._add_trees()
        Interact(view=renderView)

    def _get_crown_radius(self, tree):
        return 0

    def _add_trees(self):
        for item in self.model.objects.select_by_type('tree'):
            self.add_tree(item)

    def add_tree(self, tree):
        '''Adds a tree object to the current pipeline
        '''
        # ---------------- Load initials --------
        stem_factor = self._params.get_parameter(tree.species,
                                                 'TREE_STEM_CROWN_CENTER')
        stem_resolution = self._params.get_parameter(tree.species,
                                                     'TREE_STEM_RESOLUTION')
        crown_resolution = self._params.get_parameter(tree.species,
                                                     'TREE_CROWN_RESOLUTION')
        stem_height = tree.height * stem_factor

        crown_shape = self._params.get_parameter(tree.species,
                                                 'TREE_CROWN_SHAPE')
        crown_minrad  = self._params.get_parameter(tree.species,
                                                   'TREE_CROWN_MIN_RADIUS')
        crown_transform = self._params.get_parameter(tree.species,
                                                     'TREE_CROWN_STEM_FACTOR')

        crown_color = self._params.get_parameter(tree.species,
                                                 'TREE_CROWN_COLOR')
        stem_color = self._params.get_parameter(tree.species,
                                                'TREE_STEM_COLOR')
        # ----------------------------------------
        renderView = GetActiveViewOrCreate('RenderView')

        # ------- Create tree stem ---------------
        stem = Cone()
        stem.Resolution = stem_resolution
        stem.Radius = tree.dbh / 100.0 if tree.dbh > tree.ddh else tree.ddh / 100.0
        stem.Height = stem_height
        stem.Direction = [0.0, 0.0, 1.0]
        stem.Center = [tree.x - self.xlen/2.0, tree.y - self.ylen/2.0, (tree.z or 0) + stem_height / 2.0]
        # ----------------------------------------
        self._get_display(stem)
        # ------- Create crown ----- -------------
        if crown_shape == 'sphere':
            crown = Sphere()
            # Properties modified on sphere1
            crown.Radius = crown_minrad if crown_minrad > self._get_crown_radius(tree) else self._get_crown_radius(tree)
            crown.Center = [tree.x - self.xlen/2.0, tree.y - self.ylen/2.0, stem_height]
            crown.ThetaResolution = crown_resolution
            crown.PhiResolution = crown_resolution
        elif crwon_shape == 'cylinder':
            # TODO: Implementation needed
            pass
        elif crown_shape == 'cone':
            # TODO: Implementation needed
            pass
        # ----------------------------------------
#         print "Crown is", crown.Radius, crown.Center
#       # create a new 'Transform'
        transformed_crown = Transform(Input=crown)
        transformed_crown.Transform = 'Transform'
        transformed_crown.Transform.Scale = [1, 1, crown_transform]
        transformed_crown.Transform.Translate = [0.0, 0.0, -1.5 * crown_transform * crown.Radius]
        tree_object = GroupDatasets(Input=[stem, transformed_crown])
        tree_objectDisplay = Show(tree_object, renderView)
        ColorBy(tree_objectDisplay, ('FIELD', 'vtkBlockColors'))
        vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')
        vtkBlockColorsLUT.InterpretValuesAsCategories = 1
#         vtkBlockColorsLUT.NumberOfTableValues = 2
        vtkBlockColorsLUT.Annotations = ['0', '0', '1', '1']
        vtkBlockColorsLUT.ActiveAnnotatedValues = ['0', '1']
        vtkBlockColorsLUT.IndexedColors = stem_color + crown_color

        
#         TreeDisplay = Show(tree_object, renderView)
#         # trace defaults for the display properties.
#         TreeDisplay.ColorArrayName = [None, '']
# #         groupDatasets1Display.DiffuseColor = [1.0, 0.3333333333333333, 0.4980392156862745]
# #         TreeDisplay.GlyphType = 'Arrow'
#         TreeDisplay.SetScaleArray = [None, '']
#         TreeDisplay.ScaleTransferFunction = 'PiecewiseFunction'
#         TreeDisplay.OpacityArray = [None, '']
#         TreeDisplay.OpacityTransferFunction = 'PiecewiseFunction'
#         TreeDisplay.ScaleTransferFunction = 'PiecewiseFunction'
#         TreeDisplay.OpacityArray = [None, '']
#         TreeDisplay.OpacityTransferFunction = 'PiecewiseFunction'
#         ColorBy(TreeDisplay, ('FIELD', 'vtkBlockColors'))
#         TreeDisplay.SetScalarBarVisibility(renderView, False)
#         vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')
#         vtkBlockColorsLUT.IndexedColors = [1.0, 0.6666666666666666, 0.0, 1.0, 0.0, 0.0]
#         vtkBlockColorsLUT.IndexedColors = stem_color + crown_color
#         print stem_color + crown_color
#         self.pipeline.append(tree_object)

    def add_shrub(self, shrub):
        pass

    def add_seeds(self):
        raise NotImplementedError
