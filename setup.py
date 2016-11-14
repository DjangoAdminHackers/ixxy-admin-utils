import setuptools
from ixxy_admin_utils.version import Version


setuptools.setup(
    name='ixxy-admin-utils',
    version=Version('0.0.1').number,
    description='Ixxy Admin Utils',
    long_description=open('README.md').read().strip(),
    author='Andy Baker',
    author_email='andy@andybak.net',
    py_modules=['ixxy_admin_utils'],
    install_requires=[],
    license='MIT License',
    zip_safe=False,
    keywords='django admin',
    classifiers=['Packages'],
    packages=setuptools.find_packages(),
    package_data={
        '': ['*.txt', '*.html', '*.css', '*.js', '*.png', '*.gif', '*.png', '*.jpg'],
    },
)
