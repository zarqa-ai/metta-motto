from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
       name="metta-motto",
       version="0.0.1",  # Update as appropriate
       description="Integration of MeTTa and LLMs for prompt templates, guidance, and chaining as well as composition with other agents.",
       long_description=long_description,
       long_description_content_type="text/markdown",
       url="https://github.com/zarqa/metta-motto",
       packages=find_packages(),
       python_requires='>=3.8',
       install_requires=[
        # List your project's dependencies here.
        'hyperon'
        ]
   )