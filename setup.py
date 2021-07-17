from setuptools import setup, find_packages
setup(
    name="gnome_random_wallpaper",
    version="0.1",
    packages=find_packages(),
    package_data={
        "": ['config.yaml']
    },
    python_requires='>=3.6',
    install_requires=[
        'certifi==2021.5.30',
        'charset-normalizer==2.0.3',
        'idna==3.2',
        'Pillow==8.3.1',
        'PyYAML==5.4.1',
        'requests==2.26.0',
        'urllib3==1.26.6',
    ],
    author='Marcus Bowman',
    author_email='miliarch.mb@gmail.com',
    description='A simple program that sets random wallpaper images as desktop backgrounds in Gnome based window managers.',
    license='MIT',
    keywords='gnome cinnamon random wallpaper desktop background unsplash',
    url='https://github.com/miliarch/gnome_random_wallpaper',
    project_urls={
        'Source Code': 'https://github.com/miliarch/gnome_random_wallpaper',
    },
    entry_points={
        'console_scripts': ['grw=gnome_random_wallpaper.gnome_random_wallpaper:main']
    }
)
