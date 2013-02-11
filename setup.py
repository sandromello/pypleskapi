from distutils.core import setup

setup(name='pypleskapi',
      version='0.1',
      description='Make easy requests to Parallels Plesk Panel API',
      author='Sandro Mello',
      author_email='sandromll@gmail.com',
      url='https://github.com/sandromello/pypleskapi',
      packages=['pleskapi'],
      keywords='plesk api rpc',
      package_dir={'': 'lib'}
     )