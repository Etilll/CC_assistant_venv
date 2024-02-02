from setuptools import setup, find_namespace_packages

setup(name='CC_assistant',
      version='0.0.1',
      description='Contact manager, note manager, and a file sorter - all in one programm!',
      author='CodeCrafters',
      author_email='andrii.strygun@gmail.com',
      license='MIT',
      packages= find_namespace_packages(),
    classifiers = [
        "Programming Language :: Python :: 3.11.4",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Windows",
        ],
        install_requires=['prompt_toolkit'],
      entry_points={'console_scripts': ['start_assistant = CodeCrafters_assistant.main:starter']})