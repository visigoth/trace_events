import re
from os import path
import setuptools


# Version Number
package_name = 'trace_events'
package_path = path.join('src', package_name, '__init__.py')
with open(package_path, 'r') as file:
    content = file.read()

author, author_email, version = [
    re.search(f"^__{v}__[\ \t]*=[\ \t]*'([^']+)'",
              content, re.MULTILINE).group(1)
    for v
    in ['author', 'author_email', 'version']]

# Readme
with open('README.md', 'r') as file:
    long_description = file.read()


# Run
setuptools.setup(
    name='trace-events',
    version=version,
    author=author,
    author_email=author_email,
    description='Python event tracing using the Trace Event Format supported by Chromium browsers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JonathanHiggs/trace_events',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/JonathanHiggs/trace_events',
        'Bug Tracker': 'https://github.com/JonathanHiggs/trace_events/issues'
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Debuggers'
    ],
    keywords='trace tracing event profile profiler',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.8')
