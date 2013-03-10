from distutils.core import setup

setup(name='python-pleskapi',
      version='0.1.2',
      description='Make easy requests to Parallels Plesk Panel API',
      author='Sandro Mello',
      author_email='sandromll@gmail.com',
      url='https://github.com/sandromello/pypleskapi',
      license='GNU General Public License',
      packages=['pleskapi'],
      keywords='plesk api rpc',
      package_dir={'pleskapi': 'lib/pleskapi'},
      long_description=open('README.rst').read() + '\n\n' +
      open('HISTORY.rst').read()
     )