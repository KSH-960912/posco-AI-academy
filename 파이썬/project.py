#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

student_list = []
if len(sys.argv) == 1:  # 만약 인수가 없다면 디폴트값을 설정한다
    sys.argv.append('students.txt')
f = open(sys.argv[1], 'r')
for i in range(5):
    data = f.readline().rstrip()
    data = data.split()
    data[1] = data[1] + ' ' + data[2]
    del data[2]
    student_list.append(data)
f.close()

def grade(average):
    if average >= 90:
        return 'A'
    elif 80 <= average < 90:
        return 'B'
    elif 70 <= average < 80:
        return 'C'
    elif 60 <= average < 70:
        return 'D'
    else:
        return 'F'

def add_student():
    student_id = input("Student ID: ")
    for student in student_list:
        if student[0] == student_id:
            print("ALREADY EXISTS.")
            print()
            return
    name = input("Name: ")
    midterm = input("Midterm Score: ")
    final = input("Final Score: ")
    average = (int(midterm) + int(final)) / 2
    Grade = grade(average)
    student_list.append([student_id, name, midterm, final, average, Grade])
    print("Student added.")
    print()

def remove_student():
    if not student_list:
        print("List is empty.")
        print()
    else:
        student_id = input("Student ID: ")
        for student in student_list:
            if student[0] == student_id:
                student_list.remove(student)
                print("Student removed.")
                print()
                break
        else:
            print("NO SUCH PERSON")
            print()

def print_info():
    print('Student' + '\t\t', 'Name' + '\t\t', 'Midterm', 'Final' + '\t', 'Average', 'Grade')
    print('-----------------------------------------------------------------\n')

def student_info(i):
    print(i[0] + '\t', i[1] + '\t', i[2] + '\t', i[3] + '\t', str((int(i[2]) + int(i[3])) / 2) + '\t',
          grade((int(i[2]) + int(i[3])) / 2) + '\t')
print_info()
for i in student_list:
     student_info(i)
while True:
    command = input('# ')
    if command.lower() == 'show':
        print_info()
        sorted_student_list = sorted(student_list, key=lambda x: (int(x[2]) + int(x[3])) / 2, reverse=True)
        for i in sorted_student_list:
            student_info(i)
        print()
        continue
    elif command.lower() == 'search':
        search = input('Student ID : ')
        res = ''
        for i in student_list:
            if i[0] == search:
                print_info()
                student_info(i)
                print()
                res = i[0]
        if res != search:
            print('NO SUCH PERSON.\n')
        continue
    elif command.lower() == 'changescore':
        search = input('Student ID: ')
        change_student_grade_idx = -1
        for idx, i in enumerate(student_list):
            if i[0] == search:
                change_student_grade_idx = idx
                break
        if change_student_grade_idx == -1:
            print('NO SUCH PERSON\n')
            continue
        Final_or_Mid = input('Mid/Final? ')
        if Final_or_Mid == 'final':
            change_score = input('Input new score : ')
            if not 0 <= int(change_score) <= 100:
                print("")
                continue
            student_list[change_student_grade_idx][3] = change_score
            print("Score changed.")

        elif Final_or_Mid == 'mid':
            change_score = input('input new score :')
            if not 0 <= int(change_score) <= 100:
                print("")
                continue
            student_list[change_student_grade_idx][2] = change_score
            print("Score changed.")
        else:
            print("")
            continue
    elif command.lower() == 'searchgrade':
        student = []
        searchgrade = input('Grade to search : ')
        for i in student_list:
            if grade((int(i[2]) + int(i[3])) / 2) == searchgrade:
                student.append(i)
                res = grade((int(i[2]) + int(i[3])) / 2)
        try:
            if res != searchgrade:
                print('NO RESULTS.')
                print()
            elif res == searchgrade:
                print_info()
                for i in student:
                    student_info(i)
        except:
            print('NO RESULTS.')
            print()
    elif command.lower() == 'add':
        add_student()
        continue
    elif command.lower() == 'remove':
        remove_student()
        continue
    elif command.lower() == 'quit':
        q = input("Save data?[yes/no] ")
        if q.lower() == "yes":
            filename = input("Enter filename: ")
            sorted_student_list = sorted(student_list, key=lambda x: (int(x[2]) + int(x[3])) / 2, reverse=True)
            with open(filename, "w") as f:
                for student in sorted_student_list:
                    f.write(f"{student[0]}\t{student[1]}\t{student[2]}\t{student[3]}\t{(int(student[2]) + int(student[3])) / 2}\t{grade((int(student[2]) + int(student[3])) / 2)}\n")
        if q.lower() == 'no':
            break
        break

