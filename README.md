## Installation Instructions:

* Download and install Python with Jupyter (we recommend Anaconda: https://www.anaconda.com/download)
* Download and install a LaTeX compiler.
* Download the Randomizer zip file here.
* Unzip the Randomizer file into the Python (or Anaconda) folder.
* To open the randomizer, open Anaconda and select Jupyter Notebook. Navigate your folders to the Randomizer folder.
* See (ArXiv link) or (paper link) for a detailed instruction guide on using the randomizer.

## Creating an Assessment

* Open the Example_course.ipynb and MATH 1001.ipynb files in Jupyter notebook for examples on creating assessments.
* We recommend using a unique Python Notebook files for each course. Copying, pasting, and editing an existing file is a fine way to do this.
* The Example_course file details the exact setup necessary for creating assessments.
* If you are new to Python: clicking 'Run' with a cell selected will implement that data.

## Creating a Question File

* In the Randomizer folder, subfolders Sample Course/Sample Assessment, there are files 'q - QUESTION GUIDE' and 'm - QUESTION GUIDE' (for multiple choice specifically) that extensively detail the process of creating question files.
* All other question files (tex files starting with 'q' or 'm') are specifically chosen to highlight processes for creating questions. Feel free to check them out, and play around with them.
* Again, it's not always best to start from scratch. The easiest way to create a new question is to copy and paste an old file that using similar randomization, and edit it to do what you want.
* Do not reuse variables in a single question file, but it will not cause problems between question files.

**Note that the randomizer is a flexible tool.** If the example files don't look like the assessments you like to create, feel free to make changes. In each assessment folder there's an Archive subfolder containing the assessment preface materials (assessment cover page tex stuff), tex preamble (packages, document class, definitions, ...), and feel free to (cautiously) edit the randomizer.py file to change the way the randomizer itself runs.
