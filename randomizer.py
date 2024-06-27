import os, glob, subprocess, re, random, string, math, shutil, decimal
from random import shuffle
import numpy as np
from math import sqrt
import pandas as pd
from os import listdir
from os.path import isfile, join

###
#1.0 - major definitions

##1.1 - assessment_generator
###1.1.1 - adding student names
###1.1.2 - creating page headers
###1.1.3 - writing assessment content
###1.1.4 - extra assessments (or if there is no student name file)
###1.1.5 - putting it all together, running LaTeX

##1.2 - content

##1.3 - question_builder
###1.3.1 - question type
###1.3.2 - assessment mode
###1.3.3 - grading guide mode
###1.3.4 - multiple choice type

##1.4 - question_randomizer

##1.5 - multiple_choice_randomizer

###
#2.0 - construction tools

##2.1 - question_preview

##2.2 - grading_guide

##2.3 - folder_check

##2.4 - tex_delete

###
#3.0 - randomization tools
#3.1 - simplify_commanumber
#3.2 - simplify_polynomial
#3.3 - simplify_sqrt
#3.4 - simplify_fraction
#3.5 - set_remove
#3.6 - gcd
#3.7 - lcm
#3.8 - sqrt_output



#1.0 - major definitions

##1.1 - assessment_generator
def assessment_generator(root, semester, extra_exams, course, exam_name, questions, single_file=True):
    
    #identifying the directory containing the assessment questions
    exam_dir = root + str(course) + '/' + str(exam_name) + '/'

    #adds the TeX preface, from a seperate file, for both assessment and solutions
    #this file, in the assessment's 'Archive' folder, should contain all the \includes and \definitions needed to run the tex
    preface = open(exam_dir + 'Archive/texpreface.tex', 'r')
    prefacesol = open(exam_dir + 'Archive/solutionspreface.tex', 'r')
    headersol = prefacesol.read()
    header = preface.read()

    #closes off the whole file, will be included at the end
    footer = r''' \end{document}'''

    #the main bodies of both assessment and solutions are list of characters, which gets merged at the end
    exam = []
    solutions = []
    
    #starting point for numbered assessments
    count = 10000

    ###1.1.1 - adding student names
    try:
        #student name file must be in the 'Archive' folder, with the name StudentList.csv
        students = pd.read_csv(root + course + '/' + exam_name + '/Archive/StudentList.csv')
        print('Student information file found')
        columnslist = students.columns        

        #Writing each students' assessment
        for whichstudent in range(len(students)):
            if single_file==False:
                exam=[]
                solutions=[]
            count += 1
            ###1.1.2 - creating page headers
            headerstr = []
            
            #Creating a header with a university logo image included, or not
            headerstr.append(r'\rhead{'+str(count)+'}'+r'\lhead{'+course+r'}\chead{'+exam_name+' - '+semester+'}')
            #headerstr.append(r'\rhead{'+str(count)+'}'+r'\lhead{\includegraphics[height=1em]{logo} \hspace{1mm} '+course+r'}\chead{'+exam_name+' - '+semester+'}')

            exam.append(''.join(headerstr))
            solutions.append(''.join(headerstr))
                      
            #to allow hosting images in the assessment file, a graphics path must be defined in the latex file
            exam.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')
            solutions.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')

            #beginning settings for the solutions file
            solutions.append(r'\begin{multicols}{2} \begin{enumerate}')

            # resetting page numbers for each individual assessment
            exam.append(r'\pagenumbering{arabic}')
            exam.append(r'\setcounter{page}{1}')

            # importing the assessment preamble, for each assessment
            examtop = open(exam_dir + 'Archive/assessmentpreface.tex', 'r')
            topper = examtop.read()
            
            #replacing header with student information
            studentinfostring = []
            for columntops in range(len(columnslist)):
                studentinfostring.append('\\noindent '+columnslist[columntops]+': ')
                if str(students[columnslist[columntops]][whichstudent]) == 'nan':
                    studentinfostring.append('$\\rule{6cm}{0.15mm}$ \\vspace{.3cm} \\\\')
                else:
                    studentinfostring.append(str(students[columnslist[columntops]][whichstudent])+' \\vspace{.3cm} \\\\')
            studentinfostring = (''.join(studentinfostring))
            
            removable = re.findall(r'startstudentinformation(.*?)endstudentinformation',topper,re.DOTALL)
            topper = topper.replace(removable[0], studentinfostring)
            topper = topper.replace('startstudentinformation', ' ')
            topper = topper.replace('endstudentinformation', ' ')
                
            exam.append(topper)

            #starting enumeration for each assessment
            exam.append(r'\begin{enumerate}')

            ###1.1.3 - Writing assessment content
            #sends the current assessment and solution strings, the list of questions, and the directory
            holder = content(exam, solutions, questions, exam_dir, mode='Exam')
            exam = holder[0]
            solutions = holder[1]

            #ending the enumeration for each assessment and solution
            #(begin is done earlier in this call)
            exam.append(r'\end{enumerate}')
            solutions.append(r'\end{enumerate}\end{multicols}\emptycleardoublepage')
            
            #making individual student assessments if single_file is false
            if single_file==False:
                fullbuild = header + ''.join(exam) + footer
                fullbuildsol = headersol + ''.join(solutions) + footer

                #running TeX, deleting useless files
                filename = []
                for columntops in range(len(columnslist)):
                    if str(students[columnslist[columntops]][whichstudent]) != 'nan':
                        filename.append(str(students[columnslist[columntops]][whichstudent]))
                        filename.append('-')
                filename = (''.join(filename))

                with open(exam_dir + 'Assessments/' + filename + '.tex', 'w') as f:
                    f.write(fullbuild)

                with open(exam_dir + 'Assessments/' + 'Solutions - ' + filename + '.tex', 'w') as f:
                    f.write(fullbuildsol)

                
                subprocess.call(['pdflatex', exam_dir + 'Assessments/' + filename + '.tex'], shell=False)
                try:
                    shutil.move(filename + '.pdf', exam_dir + 'Assessments/' + filename + '.pdf')
                except:
                    print('No pdf created. Try running the tex file to identify the error. File name:', filename)
                subprocess.call(['pdflatex', exam_dir + 'Assessments/' + 'Solutions - ' + filename + '.tex'], shell=False)
                try:
                    shutil.move('Solutions - ' + filename + '.pdf',exam_dir + 'Assessments/' + 'Solutions - ' + filename + '.pdf')
                except:
                    print('No pdf created. Try running the tex file to identify the error. File name:', filename)

                #deleting standard LaTeX garbage
                tex_delete(filename + '.aux')
                tex_delete(filename + '.log')
                tex_delete(filename + '.out')
                tex_delete('Solutions - ' + filename + '.aux')
                tex_delete('Solutions - ' + filename + '.log')
                tex_delete('Solutions - ' + filename + '.out')
        print('Names added successfully')
        
    #If no student information file is found, it does not break the code    
    except:
        pass
    
    ###1.1.4 - Extra assessments (or if there is no student name file)
    #Same exact sequence, header key phrases are turned into blanks
    for what in range(extra_exams):
        if single_file==False:
            exam=[]
            solutions=[]
        count += 1
        #common page headers, assessment and solutions
        headerstr = []
        headerstr.append(r'\rhead{'+str(count)+'}'+r'\lhead{'+course+r'}\chead{'+exam_name+' - '+semester+'}')

        exam.append(''.join(headerstr))
        solutions.append(''.join(headerstr))
        
        #to allow adding images to the assessment file, a graphics path must be defined in the LaTeX file
        exam.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')
        solutions.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')

        solutions.append(r'\begin{multicols}{2} \begin{enumerate}')

        #resetting page numbers for each individual assessment
        exam.append(r'\pagenumbering{arabic}')
        exam.append(r'\setcounter{page}{1}')

        #importing the assessment preamble, for each assessment
        examtop = open(exam_dir + 'Archive/assessmentpreface.tex', 'r')
        topper = examtop.read()
        topper = topper.replace('startstudentinformation', ' ')
        topper = topper.replace('endstudentinformation', ' ')

        exam.append(topper)

        exam.append(r'\begin{enumerate}')

        # setting and writing assessment content and solutions for each individual assessment
        holder = content(exam, solutions, questions, exam_dir, mode='Exam')
        exam = holder[0]
        solutions = holder[1]

        # ending the enumeration for each assessment and solution
        # (begin is done earlier in this call)
        exam.append(r'\end{enumerate}')
        solutions.append(r'\end{enumerate}\end{multicols}\emptycleardoublepage')
        
        # making assessment if single_file is false
        if single_file==False:
            fullbuild = header + ''.join(exam) + footer
            fullbuildsol = headersol + ''.join(solutions) + footer

            # running TeX, deleting useless files
            with open(exam_dir + 'Assessments/' + semester + ' - ' + exam_name + ' - ' + str(count) + '.tex', 'w') as f:
                f.write(fullbuild)

            with open(exam_dir + 'Assessments/Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.tex', 'w') as f:
                f.write(fullbuildsol)

            subprocess.call(['pdflatex', exam_dir + 'Assessments/' + semester + ' - ' + exam_name + ' - ' + str(count) + '.tex'], shell=False)
            try:
                shutil.move(semester + ' - ' + exam_name + ' - ' + str(count) + '.pdf', exam_dir + 'Assessments/' + semester + ' - ' + exam_name + ' - ' + str(count) + '.pdf')
            except:
                print('No pdf created. Try running the tex file to identify the error. File name:', filename)
            subprocess.call(['pdflatex', exam_dir + 'Assessments/Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.tex'], shell=False)
            try:
                shutil.move('Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.pdf',exam_dir + 'Assessments/Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.pdf')
            except:
                print('No pdf created. Try running the tex file to identify the error. File name:', filename)

            tex_delete(semester + ' - ' + exam_name + ' - ' + str(count) + '.aux')
            tex_delete(semester + ' - ' + exam_name + ' - ' + str(count) + '.log')
            tex_delete(semester + ' - ' + exam_name + ' - ' + str(count) + '.out')
            tex_delete('Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.aux')
            tex_delete('Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.log')
            tex_delete('Solutions - ' + semester + ' - ' + exam_name + ' - ' + str(count) + '.out')

    ###1.1.5 - Putting it all together, running LaTeX
    #building full TeX file from parts

    #running TeX if only one file is to be output
    if single_file==True:
        fullbuild = header + ''.join(exam) + footer
        fullbuildsol = headersol + ''.join(solutions) + footer
    
        with open(exam_dir + 'Assessments/' + semester + ' - ' + exam_name + '.tex', 'w') as f:
            f.write(fullbuild)
        with open(exam_dir + 'Assessments/' + semester + ' - ' + exam_name + ' - Solutions.tex', 'w') as f:
            f.write(fullbuildsol)

        #moving completed files to 'Assessments' folder
        subprocess.call(['pdflatex', exam_dir + 'Assessments/' + semester + ' - ' + exam_name + '.tex'], shell=False)
        try:
            shutil.move(semester + ' - ' + exam_name + '.pdf', exam_dir + 'Assessments/' + semester + ' - ' + exam_name + '.pdf')
        except:
            print('No pdf created. Try running the tex file to identify the error.')
        subprocess.call(['pdflatex', exam_dir + 'Assessments/' + semester + ' - ' + exam_name + ' - Solutions.tex'], shell=False)
        try:
            shutil.move(semester + ' - ' + exam_name + ' - Solutions.pdf', exam_dir + 'Assessments/' + semester + ' - ' + exam_name + ' - Solutions.pdf')
        except:
            print('No pdf created. Try running the tex file to identify the error.')

        #deleting standard LaTeX garbage
        tex_delete(semester + ' - ' + exam_name + '.aux')
        tex_delete(semester + ' - ' + exam_name + '.log')
        tex_delete(semester + ' - ' + exam_name + '.out')
        tex_delete(semester + ' - ' + exam_name + ' - Solutions.aux')
        tex_delete(semester + ' - ' + exam_name + ' - Solutions.log')
        tex_delete(semester + ' - ' + exam_name + ' - Solutions.out')
    
##1.2 - content
def content(exam, solutions, questions, exam_dir, mode):
    #builds full assessment content from the question lists
    #each question list ideally defines a page (assuming nothing spills over)   
    for page in questions:
        tempage = page[:]
        
        #checking for any lists from which a subset of questions will be chosen
        #cycles through the page list once, then flattens the choices into a single list of pages and questions
        for question in tempage:
            if type(question) is list:
                temquestion=question[:]
                grabnum=temquestion[0]
                temquestion.pop(0)
                qchoices=random.sample(temquestion, grabnum)
                for i in range(len(tempage)):
                    if tempage[i]==question:
                        for j in range(len(qchoices)):
                            tempage.insert(i+1,qchoices[j])
                tempage.remove(question)
                
        for question in tempage:
            #adds the randomization definitions to both assessment and solutions
            #sending question file to randomizer
            holder = question_randomizer(question, exam_dir)
            exam.append(holder)
            solutions.append(holder)

            #adds the question and solution content, as it appears in the assessment
            #sending to the question builder
            holder = question_builder(question, exam_dir, mode)
            exam.append(holder[0])
            solutions.append(holder[1])
        #new page at the end of ever subset of questions
        exam.append('\\newpage')
        
    return [exam, solutions]
    
##1.3 - question_builder
def question_builder(question, exam_dir, mode):
    #chooses a question at random from the set of questions in the question file 
    #returns the TeX question and solution
    
    ###1.3.1 - question type
    #if the question is of question format (file starts with letter 'q')
    if question[0] == 'q':
        file = open(exam_dir + question + '.tex', 'r')
        filetext = file.read()

        #finds the set of questions
        question_set = re.findall(r'startall(.*?)endall',filetext,re.DOTALL)
        
        #if present, grabs the 'pre' content
        pre_check = re.findall(r'startpre(.*?)endpre', filetext, re.DOTALL)
        pre_part = ' '
        if len(pre_check)>0:
            pre_part = pre_check[0]
        
        #if present, grabs the 'post' content
        post_check = re.findall(r'startpost(.*?)endpost', filetext, re.DOTALL)
        post_part = ' '
        if len(post_check)>0:
            post_part = post_check[0]
        
        ###1.3.2 - assessment mode
        #used for creation of assessments for students
        #randomly chooses one question and solution variant from those available, as text strings
        if mode=='Exam':
            cquest = question_set[np.random.randint(0,len(question_set))]
            #pulls out the question and solution variant text from the full string
            question_part = re.findall(r'startquestion(.*?)endquestion', cquest, re.DOTALL)[0]
            solution_part = re.findall(r'startsolution(.*?)endsolution', cquest, re.DOTALL)[0]
            
            #as returned, the question is merged with the 'pre' and 'post' content
            return [''.join([pre_part,question_part,post_part]), solution_part]
        
        ###1.3.3 - grading guide mode
        if mode=='Grading Guide':
            #Grading guide mode returns all the variations of a single question
            #randomization only happens once, for the sake of simplicity
            
            #if runquestion==0, the question isn't included, it is if it is equal to 1
            #this is used to remove three types of question files:
            #qblankpage is just a blank page for printing parity
            #question files that end with the string 'pre' and 'post' are reserved phrases,
            #useful for randomizing questions with multiple parts
            #ie. files 'q4pre', 'q4post', 'q4a', 'q4b', only the last two would be included in the grading guide            
            runquestion=0
            if len(question)<4:
                runquestion=1
            if len(question)>=4:
                if str(question[-4]+question[-3]+question[-2]+question[-1])!='post' and str(question[-3]+question[-2]+question[-1])!='pre' and question!='qblankpage':
                    runquestion=1
                    
            #if the question is included in the grading guide:
            #instead of choosing one variant of the problem, it grabs them all and enumerates
            if runquestion==1:
                allthedamntext = ['{\\Large{\\bf Question (number)}} - ' + str(question) + '\\\\ ']
                allthedamnsols = []
                for eachvers in range(len(question_set)):
                    cquest = question_set[eachvers]
                    question_part = re.findall(r'startquestion(.*?)endquestion', cquest, re.DOTALL)[0]
                    solution_part = re.findall(r'startsolution(.*?)endsolution', cquest, re.DOTALL)[0]
                    allthedamntext.append('$ $ \\\\ {\\bf Version ' + str(eachvers+1) + '} \\\\')
                    has_comments = re.findall(r'startcomments(.*?)endcomments', cquest, re.DOTALL)
                    if len(has_comments)>0:
                        allthedamntext.append(has_comments[0])
                    allthedamntext.append('\\begin{enumerate}[resume]')
                    allthedamntext.append(pre_part)
                    allthedamntext.append(question_part)
                    allthedamntext.append(post_part)
                    allthedamntext.append(' \\end{enumerate}')
                    allthedamnsols.append(solution_part)
                allthedamntext.append('\\newpage')
                return [''.join(allthedamntext),''.join(allthedamnsols)]
            return ['','']
                
    ###1.3.4 - multiple choice type
    #behaves like question type, but sends work to different places
    if question[0] == 'm':
        file = open(exam_dir + question + '.tex','r')
        filetext = file.read()
        question_set = re.findall(r'startall(.*?)endall', filetext, re.DOTALL)
        
        pre_check = re.findall(r'startpre(.*?)endpre', filetext, re.DOTALL)
        pre_part = ' '
        if len(pre_check)>0:
            pre_part = pre_check[0]
        post_check = re.findall(r'startpost(.*?)endpost', filetext, re.DOTALL)
        post_part = ' '
        if len(post_check)>0:
            post_part = post_check[0]
        
        if mode=='Exam':
            #randomly chooses the question variant
            cquest = question_set[np.random.randint(0,len(question_set))]

            #pulls out the question and set of solution options from the full set
            question_part = re.findall(r'startquestion(.*?)endquestion', cquest, re.DOTALL)[0]
            answer_list = re.findall(r'startsolset(.*?)endsolset', cquest, re.DOTALL)

            #randomizing the order of the list of choices
            holder = multiple_choice_randomizer(answer_list)
            question_part = ''.join([pre_part,question_part,post_part]) + ''.join(holder[0])

            #Writing the answers as an enumerated list
            total_answer = '\\item ' + str(holder[1])

            return [question_part, total_answer]
        
        if mode=='Grading Guide':
            allthedamntext = ['{\\Large{\\bf Question (number)}} - ' + str(question) + ' \\\\']
            allthedamnsols = []
            for eachvers in range(len(question_set)):
                cquest = question_set[eachvers]
                question_part = re.findall(r'startquestion(.*?)endquestion', cquest, re.DOTALL)[0]
                answer_list = re.findall(r'startsolset(.*?)endsolset', cquest, re.DOTALL)
                holder = multiple_choice_randomizer(answer_list)
                allthedamntext.append('$ $ \\\\ {\\bf Version ' + str(eachvers+1) + '} \\\\')
                has_comments = re.findall(r'startcomments(.*?)endcomments', cquest, re.DOTALL)
                if len(has_comments)>0:
                    allthedamntext.append(has_comments[0])
                allthedamntext.append('\\begin{enumerate}[resume]')
                allthedamntext.append(pre_part)
                allthedamntext.append(question_part)
                allthedamntext.append(post_part)
                allthedamntext.append(''.join(holder[0]))
                allthedamntext.append('\\end{enumerate}')
                allthedamnsols.append('\\item ' + str(holder[1]))
            allthedamntext.append('\\newpage')
            return [''.join(allthedamntext),''.join(allthedamnsols)]

##1.4 - question_randomizer
def question_randomizer(question, exam_dir):
    #handles the randomization for each question, for each variable defined
    #inputs: question - string, file name of a LaTeX question type
    #inputs: exam_dir - string, path to the LaTeX question type
    #output: string of randomized variables for the LaTeX question
    
    #variable names with numbers are to avoid defined variables being used twice from the question file,
    #python allows numbers in variables, latex does not
    
    file101=open(exam_dir + question + '.tex', 'r')
    filetext101=file101.read()
    
    #the list of variables
    randletters101=re.findall(r'startdef (.*?)=',filetext101)
    #the list of required randomizations
    randvalue101=re.findall(r'=(.*?)enddef',filetext101)
    
    #makes one mastercopy of the variable names and randomized values, as TeX
    varlist101=[]
    for letsord101 in range(len(randletters101)):
        varlist101.append('\\def \\')
        
        variablename101=randletters101[letsord101].replace(" ", "")
        varlist101.append(variablename101)
        varlist101.append('{')
        varit101=eval(randvalue101[letsord101])
        
        #defines the variable name and the randomization that has occured in the python, so the variable exists
        #exceptions added; all commands that shouldn't be stored by python should start with 'simplify'
        if randvalue101[letsord101].replace(" ","").startswith('simplify')==False:
            exec("%s = %s" % (variablename101,varit101))
        
        varlist101.append(str(varit101))
        varlist101.append('}')
        
    return ''.join(varlist101)

##1.5 - multiple_choice_randomizer
def multiple_choice_randomizer(answer_list):
    #takes the list of possible answers, returns tex for the itemized list and the ordered value of the answer
    #length of the list of guesses is arbitrary, can be up to 26
    
    #creates a string from the alphabet, to find the solution
    alphabet = string.ascii_lowercase
    
    text_string=[]
    
    answer_list = answer_list[0]
    
    number_columns = int(re.findall(r'begincolumn (.*?) endcolumn', answer_list)[0])
    width_columns = re.findall(r'beginwidth (.*?) endwidth', answer_list)[0]
    
    options = re.findall(r'sola(.*?)solb', answer_list, re.DOTALL)
    
    #Search for first/last fixed positions and remove them from the randomization
    for i in range(len(options)):
        if 'always_first' in options[i]:
            first = [options[i].replace("always_first",""),i]
            options[i] = first[0]
        elif 'always_last' in options[i]:
            last = [options[i].replace("always_last",""),i]
            options[i] = last[0]

    # shuffles a list of the numbers from 0 to the number of possible answers
    randorder = [i for i in range(len(options))]
    shuffle(randorder)
    shuffle(randorder)
    shuffle(randorder)

    #puts first thing first
    try:
        randorder.insert(0, randorder.pop(randorder.index(first[1])))
    except:
        pass

    #puts last thing last
    try:
        randorder.insert(len(randorder)-1, randorder.pop(randorder.index(last[1])))
    except:
        pass
    
    text_string.append(r'\begin{minipage}[t]{')
    text_string.append(str(width_columns))
    text_string.append(r'\linewidth}')
    
    if number_columns!=1:
        text_string.append(r'\begin{multicols}{')
        text_string.append(str(number_columns))
        text_string.append('}')
    text_string.append(r'\begin{itemize}')

    #math necessary to have the letters arrange on the page as one would expect
    letters = list(range(len(options)))
    number_rows = math.ceil(len(letters)/number_columns)
    while len(letters) < number_rows*number_columns:
        letters.append('')
    letters = np.reshape(a=letters, newshape=(number_rows, number_columns))
    letters = np.transpose(letters)
    letters = np.reshape(a=letters, newshape=(number_rows*number_columns,1))
    letters = np.ndarray.tolist(letters)
    
    #pulls each possible answer from the list in the aforementioned random order, attaches an item call
    #correct answer must be the first in the list, pulls out the letter associated with that value
    count = 0
    for i in range(number_rows*number_columns):
        if letters[i][0] == '':
            text_string.append(r'\item[] ')
        else:
            text_string.append(r'\item[(')
            text_string.append(alphabet[int(letters[i][0])])
            text_string.append(r')] ')
            text_string.append(options[randorder[count]])
            if randorder[count]==0:
                answer = alphabet[int(letters[i][0])]
            count+=1
    
    #ends enumeration and adds space after the question
    text_string.append(r'\end{itemize}') 
    if number_columns != 1:
        text_string.append(r'\end{multicols}') 
    text_string.append(r'\end{minipage} \vfill ')
    
    return [text_string, answer]
    
    
    
    
#2.0 - construction tools    
   
##2.1 - question_preview    
def question_preview(root, question, number, course, exam_name, user):
    #used to check a single question without needing to build a whole assessment
    #useful when writing questions

    #tex preface starting the file
    exam_dir = root + str(course) + '/' + str(exam_name) + '/'
    preface = open(exam_dir+'Archive/texpreface.tex', 'r')
    header = preface.read()
    
    #closes off the whole file
    footer = r''' \end{document}'''
    
    #the main body
    exam = []
    solutions = []
    
    exam.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')
    
    #one question repeatedly
    solutions.append('\\begin{enumerate}')       
    exam.append('{\\bf Question:} \\begin{enumerate}')
        
    #setting and writing assessment content and solutions for each individual assessment
    #creates an assessment that is just one question, numerous times
    exam_dir = root + str(course) + '/' + str(exam_name) + '/'
    holder = content(exam, solutions, [[question]*number], exam_dir, mode='Exam')
    exam = holder[0]
    solutions = holder[1]

    #ending the enumeration for each assessment and solution 
    exam.append('\\end{enumerate} {\\bf Solutions:}')
    solutions.append('\\end{enumerate}')
    
    #building full TeX file from parts
    fullbuild = header + ''.join(exam) + ''.join(solutions) + footer
    
    #running TeX, deleting useless files
    fntex = 'Question Practice - ' + str(user) + '.tex'
    fnpdf = 'Question Practice - ' + str(user) + '.pdf'
    with open(root + fntex,'w') as f:
         f.write(fullbuild)
            
    subprocess.call(['pdflatex', root + fntex], shell=False)
    try:
        shutil.move(fnpdf, root + fnpdf)
    except:
        print('No pdf created. Try running the tex file to identify the error.')
    
    tex_delete('Question Practice - ' + str(user) + '.aux')
    tex_delete('Question Practice - ' + str(user) + '.log')
    tex_delete('Question Practice - ' + str(user) + '.out')

##2.2 - grading_guide    
def grading_guide(root, semester, course, exam_name, questions):
    #For all questions in an assessment, creates a file with each possible variant visible

    #tex preface starting the file
    exam_dir = root + str(course) + '/' + str(exam_name) + '/'
    preface = open(exam_dir + 'Archive/texpreface.tex', 'r')
    header = preface.read()
    
    #closes off the whole file
    footer = r''' \end{document}'''
    
    #the main body
    exam = []
    exam.append('\\lhead{\Large ')
    exam.append(course)
    exam.append(' - ')
    exam.append(exam_name)
    exam.append(' - Grading guide}')
    solutions = []
    
    #to allow images in the assessment file, a graphics path must be defined in the latex file
    exam.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')
    solutions.append(r'\graphicspath{{' + root + course + r'/' + exam_name + r'/}}')
    
    solutions.append('\\begin{enumerate}')       
    #exam.append('\\begin{enumerate}')
        
    #setting and writing assessment content and solutions for each individual assessment
    exam_dir = root + str(course) + '/' + str(exam_name) + '/'
    holder = content(exam, solutions, questions, exam_dir, mode='Grading Guide')
    exam = holder[0]
    solutions = holder[1]

    #ending the enumeration for each assessment and solution 
    #(begin is done earlier in this call)
    exam.append('{\\bf Solutions:}')
    solutions.append('\\end{enumerate}')
    
    #building full TeX file from parts
    fullbuild = header + ''.join(exam) + ''.join(solutions) + footer
    
    #running TeX, deleting useless files
    fntex = 'Grading guide - ' + course + ' - ' + exam_name + '.tex'
    fnpdf = 'Grading guide - ' + course + ' - ' + exam_name + '.pdf'
    with open(root + fntex,'w') as f:
         f.write(fullbuild)
            
    subprocess.call(['pdflatex', root + fntex], shell=False)
    shutil.move(fntex, exam_dir + 'Archive/' + fntex)
    try:
        shutil.move(fnpdf, exam_dir + 'Archive/' + fnpdf)
    except:
        print('No pdf created for grading guide. Try running the tex file to identify the error.')
    
    tex_delete('Grading guide - ' + course + ' - ' + exam_name + '.aux')
    tex_delete('Grading guide - ' + course + ' - ' + exam_name + '.log')
    tex_delete('Grading guide - ' + course + ' - ' + exam_name + '.out')
    
##2.3 - folder check    
def folder_check(root, course, exam):
    exam_dir = root + str(course) + '/' + str(exam) + '/'
    semester='End of Days'
    
    #finds all tex files in the assessment folder, makes a grading guide file with all of those
    questionfiles = [f[:-4] for f in listdir(exam_dir) if (isfile(join(exam_dir, f)) and (f[-4:]=='.tex') and f[-13:]!='blankpage.tex')]

    grading_guide(root, semester, course, exam, [questionfiles])

    
##2.4 - tex delete
def tex_delete(file):
    #used to delete the unnecessary .tex files, if they exist
    try:
        os.unlink(file)
    except:
        pass


#3.0 - randomization tools

##3.1 - simplify_commanumber
def simplify_commanumber(value):
    #returns a comma seperated number
    return "{:,}".format(value)

##3.2 - simplify_polynomial
def simplify_polynomial(var,coefflist):
    #Writes a polynomial as a mathematician would expect
    #If leading coefficient is zero, includes first sign
    polystring=[]
    n=len(coefflist)
    
    i=0
    while i<n:
        if coefflist[i]!=0:
            if coefflist[i] not in [-1,1]:
                if coefflist[i]>0:
                    if i!=0:
                        polystring.append('+')
                    polystring.append(str(coefflist[i]))
                if coefflist[i]<0:
                    polystring.append(str(coefflist[i]))
            if coefflist[i]==-1:
                polystring.append('-')
                if i==n-1:
                    polystring.append('1')
            if coefflist[i]==1:
                if i!=0:
                    polystring.append('+')
                if i==n-1:
                    polystring.append('1')
            if i!=n-1:
                polystring.append(var)
                polystring.append('^{')
                if i!=n-2:
                    polystring.append(str(n-i-1))
                polystring.append('}')
        i=i+1
    return ''.join(polystring)

##3.3 - simplify_sqrt
def simplify_sqrt(n):
    #modified from code found online
    #Simplifies square roots

    root = int(sqrt(n))

    for factor_root in range(root, 1, -1):
        factor = factor_root * factor_root
        if n % factor == 0:
            reduced = n // factor
            if reduced==1:
                return "%d" % factor_root
            return "%d \\sqrt{%d}" % (factor_root, reduced)
    if n==1:
        return "1"
    return "\\sqrt{%d}" % n

##3.4 - simplify_fraction
def simplify_fraction(numer, denom):
    #Returns LaTeX-style simplified fractions
    #Note that this is a regular style fraction
    #use \displaystyle if desired
    if denom == 0:
        print('Division by 0')
        return "FAILED; DIVISION BY ZERO"

    # Remove greatest common divisor:
    common_divisor = gcd(numer, denom)
    (reduced_num, reduced_den) = (numer / common_divisor, denom / common_divisor)

    if reduced_den == 1:
        return "%d" % (reduced_num)
    else:
        return "\\frac{%d}{%d}" % (reduced_num, reduced_den)

##3.5 - set_remove
def set_remove(goodset,badset):
    #Returns a list from goodset with the elements of badset removed
    #Elements not in the good set are ignored
    goodset = list(goodset)
    badset = list(badset)
    
    for i in badset:
        try:
            goodset.remove(i)
        except:
            pass
    return goodset

##3.6 - gcd
def gcd(a,b):
    #Euclid's algorithm
    while b:
        a, b = b, a % b
    return a

##3.7 - lcm
def lcm(a,b):
    g = gcd(a,b)
    return abs(round((a*b)/g))

##3.8 - sqrt_output
def sqrt_output(n):
    #Similar to the previous square root code, 
    #but written so that the values are known by the randomizer, and can be manipulated
    root = int(sqrt(n))

    for factor_root in range(root, 1, -1):
        factor = factor_root * factor_root
        if n % factor == 0:
            reduced = n // factor
            return [factor_root, reduced]
    return [1,n]








