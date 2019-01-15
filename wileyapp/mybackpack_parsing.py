
# coding: utf-8

# In[19]:

from __future__ import division
import re

# In[20]:

import json

# In[97]:

# plotting-specific

def repeat(category):
    dic = {
        'hw': 1,
        'homework': 1,
        'assessment': 3,
        'test': 3,
        'exam': 8,
        'quiz': 2,
        'project': 8,
        'paper': 10,
        'in-class': 1,
        'discussion': 1,
        'presentation': 8,
        'lab': 3,
        'participation': 1,
        'performance': 1,
        'practice': 1
    }
    try:
        return dic[category]
    except:
        return 1

def ridge(category, data, scale=20):
    return list(zip([category]*len(data), scale*data))


def is_assignment(string):
    if len(list(re.finditer('\t', string))) == 6:
        return True
    else:
        return False


# In[124]:

def is_coursename(string):
    if len(list(re.finditer('\tTeacher: ', string))) == 1:
        return True
    else:
        return False

# In[98]:

def grade2obj(assignment):
    #assignment = 'Homework 12 - Pg 849 (9-21,53-59,61-71) odd\tHomework\tY\t100.00\t12/5/2018\t12/6/2018\t \n'
    obj = {}
    # first check if it's actually an assignment
    # the best way would be to check if it has exactly 6 tabs
    if not(is_assignment(assignment)):
        return None
    assignment = assignment.split('\t')[:-1]
    # cast as datatypes if needed
    # we know that indices 2 and 3 should be ints
    if assignment[2] in ['Y','N']:
        assignment[2] = 100 if assignment[2] == 'Y' else 0
    else:
        assignment[2] = int(float(assignment[2]))
    assignment[3] = int(float(assignment[3]))
    return assignment


# In[142]:

def course2obj(string, is_file=True):
    if is_file:
        with open(fname) as f:
            content = f.readlines()
    else:
        content = string[:]
    totals = [0,0]
    assignments = []
    for assignment in content:
        try:
            if grade2obj(assignment) != None:
                assignments.append(grade2obj(assignment))
            continue
        except:
            print("failed on {}".format(assignment))
    return assignments

def calculate_grade(assignments):
    earned = 0
    possible = 0
    for assignment in assignments:
        earned += assignment[2]
        possible += assignment[3]
    return round(100*earned/possible, 4)

def calculate_means(assignments):
    earned = []
    possible = []
    types = []
    for assignment in assignments:
        if not(assignment[1] in types):
            types.append(assignment[1])
            earned.append(assignment[2])
            possible.append(assignment[3])
        else:
            index = types.index(assignment[1])
            earned[index] += assignment[2]
            possible[index] += assignment[3]

    grades = []
    for index, (tp, earn, possible) in enumerate(zip(types, earned,possible)):
        grades.append({'id': index, 'type': tp, 'grade': round(100*earn/possible, 4)})
    return grades

def grade2GPA(number):
    last_digit = number % 10
    if last_digit >= 7:
        GPA = 1.33
    elif last_digit >= 3:
        GPA = 1.00
    else:
        GPA = 0.67
    first_digit = (number - last_digit)/10
    GPA += first_digit - 6
    return GPA

def calculate_GPA(courses_obj):
    boosts = {
        'Honors':0.5,
        'AP':1.0,
        'Post-AP':1.0,
        'Select':0.5,
        'Advanced':1.0
    }
    GPA = 0
    for course_obj in courses_obj:
        GPA += grade2GPA(calculate_grade(course_obj['assignments']))
        GPA += sum([boosts[x] for x in boosts.keys() if (x in course_obj['course_name'].split())])
    return GPA/(len(courses_obj))

def get_categories(assignments):
    categories = []
    for assignment in assignments:
        if not(assignment[1] in categories):
            categories.append(assignment[1])
    return categories

def format_date(bad_date):
    month, day, year = bad_date.split('/')
    return year + '-' + month + '-' + day

def format_dates(assignments):
    return [[x[0],x[1],x[2],x[3],x[4],format_date(x[5])] for x in assignments]

# In[171]:

def text2obj(contents):
    obj = []
    if type(contents) == type('string'):
        contents = contents.split('\n')
    # go through contents
    # find the indices for which a course begins
    # then run course2obj in between those indices (checking for start and end cases)
    coursename_indices = []
    assignment_indices = []
    for index, line in enumerate(contents):
        if is_coursename(line):
            coursename_indices.append(index)
        if is_assignment(line):
            assignment_indices.append(index)
    for index, coursename_index in enumerate(coursename_indices):
        # extract coursename, grade-to-date, teacher name
        course_header = contents[coursename_index]
        course_header = course_header.split('\t')
        coursename = course_header[0]
        grade_to_date = course_header[1]
        grade_to_date = grade_to_date[grade_to_date.index(': ')+2:]
        if grade_to_date == ' ':
            grade_to_date = None
        teacher = course_header[2]
        teacher = teacher[teacher.index(': ')+2:]
        if teacher[-1] == '\n':
            teacher = teacher[:-1]
        # go through until it's the next coursename_index
        if index != len(coursename_indices)-1:
            curr_assignments = [contents[x] for x in assignment_indices if (x > coursename_index and x < coursename_indices[index+1])]
        else:
            curr_assignments = [contents[x] for x in assignment_indices if (x > coursename_index)]
        assignments_array = course2obj(curr_assignments, False)
        obj.append({'id': str(index),
                    'course_name': coursename,
                    'grade_to_date':grade_to_date,
                    'teacher':teacher,
                    'assignments': format_dates(assignments_array),
                    'calculated_grade':calculate_grade(assignments_array),
                    'means': calculate_means(assignments_array)})
    return obj

if __name__ == '__main__':
    # In[172]:

    obj = text2obj(a)


    # Now that it works robustly on processing any text from the MyBackpack Daily Assignments page, we can continue designing a class that helps us perform operations on this object. This'll go in a different ipynb file.

    # In[181]:

    with open('untitled4.txt') as f:
        b = f.read()


    # In[182]:

    b = b.split('\n')


    # In[183]:

    obj2 = text2obj(b)


    # In[184]:

    obj2


    # In[ ]:



