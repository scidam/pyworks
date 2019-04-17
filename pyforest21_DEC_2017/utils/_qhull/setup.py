
from __future__ import division, print_function, absolute_import

from os.path import join, dirname
import glob


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration, get_numpy_include_dirs
    from numpy.distutils.misc_util import get_info as get_misc_info
    from numpy.distutils.system_info import get_info as get_sys_info
    from distutils.sysconfig import get_python_inc
    config = Configuration(None, parent_package, top_path)
#    config.add_data_dir('tests')
    # qhull
    qhull_src = list(glob.glob(join(dirname(__file__), 'qhull',
                                    'src', '*.c')))

    inc_dirs = [get_python_inc()]
    if inc_dirs[0] != get_python_inc(plat_specific=1):
        inc_dirs.append(get_python_inc(plat_specific=1))
    inc_dirs.append(get_numpy_include_dirs())

    cfg = dict(get_sys_info('lapack_opt'))
    cfg.setdefault('include_dirs', []).extend(inc_dirs)

    def get_qhull_misc_config(ext, build_dir):
        # Generate a header file containing defines
        config_cmd = config.get_config_cmd()
        defines = []
        if config_cmd.check_func('open_memstream', decl=True, call=True):
            defines.append(('HAVE_OPEN_MEMSTREAM', '1'))
        target = join(dirname(__file__), 'qhull_misc_config.h')
        with open(target, 'w') as f:
            for name, value in defines:
                f.write('#define {0} {1}\n'.format(name, value))
    
    config.add_extension('qhull',
                         sources=['qhull.c'] + qhull_src + [get_qhull_misc_config],
                         **cfg)
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(maintainer="SciPy Developers",
          author="Anne Archibald",
          maintainer_email="scipy-dev@scipy.org",
          description="Spatial algorithms and data structures",
          url="https://www.scipy.org",
          license="SciPy License (BSD Style)",
          **configuration(top_path='').todict()
          )
