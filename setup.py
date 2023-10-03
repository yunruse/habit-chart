from setuptools import setup

APP = ['habit-chart.py']
DATA_FILES = ['sfx-all.mp3', 'sfx-habit.mp3']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps', 'yaml'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
