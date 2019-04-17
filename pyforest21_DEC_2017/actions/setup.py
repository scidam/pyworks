from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

ext_modules = [
    Extension("cdeath",
              sources=["cdeath.pyx"],
#               extra_compile_args = ["-fopenmp" ],
#               extra_link_args=['-fopenmp']
    )
]

setup(
    ext_modules = cythonize(ext_modules)
)