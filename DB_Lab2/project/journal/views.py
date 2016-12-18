from django.shortcuts import render, redirect
from DatabaseManager import DB

db = DB()

def main(request):
    journal = db.getJournalList()
    return render(request, 'journal/index.html', {'journal': journal})


def remove(request, id):
    db.removeJournal(id)
    return redirect('/')


def edit(request, id):
    db.updateJournal(id)
    if request.method == 'GET':
        student = db.getStudentList()
        teacher = db.getTeacherList()
        subject = db.getSubjectList()
        group = db.getGroupList()
        return render(request, 'create.html',
                      {'student': student, 'teacher': teacher, 'subject': subject, 'group': group})
    elif request.method == 'POST':
        db.updateJournal({'journal': id, 'student': request.POST['student'], 'teacher': request.POST['teacher'],
                          'subject': request.POST['subject'], 'group': request.POST['group'],
                          'mark_numeric': request.POST['mark_numeric'], 'mark_letter': request.POST['mark_letter']})
        return redirect('/')


def add(request):
    if request.method == 'GET':
        students = db.getStudentList()
        teachers = db.getTeacherList()
        subjects = db.getSubjectList()
        groups = db.getGroupList()
        return render(request, 'add_page.html', {'students': students, 'teachers': teachers,
                                                 'subjects': subjects, 'groups': groups})
    elif request.method == 'POST':
        db.saveJournal({'driver': request.POST['driver'], 'customer': request.POST['customer'],
                        'address_from': request.POST['address_from'], 'y_from': request.POST['y_from'],
                        'address_to': request.POST['address_to'], 'y_to': request.POST['y_to'],
                        'data': request.POST['data']})
        return redirect('/')


def topdrivers(request):
    students = db.getTopStudentsAggregate()
    return render(request, 'top.html', {'students': students})


