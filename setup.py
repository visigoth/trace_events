import setuptools

from trace_events import __author__ as author, __author_email__ as author_email, __version__ as version

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name = 'trace_events',
    version = version,
    author = author,
    author_email = author_email,
    description = 'Python event tracing using the Trace Event Format supported by Chromium browsers',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/JonathanHiggs/trace_events',
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires = '>=3.9'
)