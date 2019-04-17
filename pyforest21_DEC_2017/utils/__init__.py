from __future__ import print_function
from pyforest.actions import AbstractAction
from pyforest.events import AbstractEvent
from pyforest.resources import AbstractResource

# ---------- Building Qhull for Pyforest --------------
# TODO: Installation process should be checked !
#try:
#    from pyforest.utils.qhull import ConvexHull
#except ImportError:
#    # Build qhull
#    from Cython.Build import cythonize
#    import os, glob, subprocess, shutil, time
#    current_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
#    cythonize(os.path.join(current_path, '_qhull/qhull.pyx'))
#    os.chdir(current_path)
#    subprocess.call(['python', os.path.join(current_path, '_qhull/setup.py'), 'build'])
#    qhull_so = list(glob.glob(os.path.join(current_path, 'build/*/qhull.so')))[0]
#    try:
#        shutil.copyfile(qhull_so, os.path.join(current_path, 'qhull.so'))
#    except (IOError, OSError):
#        pass
#    # TODO: These are Unix-specific commands, they should be avoided in the future
#    subprocess.call(['rm','-r', os.path.join(current_path, 'build')])
#    subprocess.call(['chmod','+x', os.path.join(current_path, 'qhull.so')])
#    time.sleep(1)
#
## Try import qhull after compilation...
#try:
#    # TODO: this step is still not working properly...
#    from pyforest.utils.qhull import ConvexHull
#except ImportError:
#    print("Qhull module couldn't be compiled. Check your environment ")
# ------------------------------------------------------



# set seed here if needed
def setup_value(obj, kwargs, fieldname, value=None):
    if fieldname in kwargs:
        setattr(obj, fieldname, kwargs[fieldname])
    else:
        setattr(obj, fieldname, value)


def load_inits(item):
    '''
    Loads initial values when model is created.
    '''

    if isinstance(item, (AbstractEvent, AbstractAction,
                         AbstractResource)):
        return [item]
    elif hasattr(item, '__iter__'):
        check = all([True if isinstance(x, (AbstractEvent,
                                            AbstractAction,
                                            AbstractResource))
                     else False for x in item])
        if check:
            return item
        else:
            return []
    else:
        return []
