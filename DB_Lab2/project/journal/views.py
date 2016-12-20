from django.shortcuts import render, reverse, redirect
from django.http import Http404, HttpResponseRedirect
from DatabaseManager import DB
from forms import CreateJournalForm, UpdateJournalForm
from django.views import generic

db = DB()


class ListJournalsView(generic.ListView):
    template_name = 'journal/index.html'
    paginate_by = 10
    context_object_name = 'journal_list'

    def get_queryset(self):
        return db.getJournalList(limit=0)


class JournalDetailView(generic.View):
    form_class = UpdateJournalForm
    template_name = 'journal/view.html'

    def get(self, request, *args, **kwargs):
        journal_id = kwargs['journal_id']
        journal = db.getJournal(journal_id)
        if not journal:
            raise Http404('No such mark')
        initial = journal.copy()
        initial['student_id'] = journal['student_id']['_id'],
        initial['group_id'] = journal['group_id']['_id'],
        initial['teacher_id'] = journal['teacher_id']['_id'],
        initial['subject_id'] = journal['subject_id']['_id'],
        form = self.form_class(initial=initial)
        return render(request, self.template_name, {'journal': journal, 'form': form})

    def post(self, request, *args, **kwargs):
        journal_id = kwargs['journal_id']
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            success = db.updateJournal(data)
            if not success:
                raise Http404('No such mark')
            return HttpResponseRedirect(reverse('issues:view', args=(journal_id,)))

        journal = db.getJournal(journal_id)
        if not journal:
            raise Http404('No such mark')
            return render(request, self.template_name, {'journal': journal, 'form': form})


def remove(request, id):
    db.removeJournal(id)
    return redirect('/')


def edit(request, id):
    if request.method == 'POST':
        form = CreateJournalForm(request.POST)
        if form.is_valid():
            new_journal = {'mark_letter': form.cleaned_data['mark_letter'],
                           'mark_numeric': form.cleaned_data['mark_numeric'],
                           'group_id': form.cleaned_data['group'],
                           'teacher_id': form.cleaned_data['teacher'],
                           'subject_id': form.cleaned_data['subject'],
                           'student_id': form.cleaned_data['student']}
            db.saveJournal(new_journal)
            return redirect('/journal')
    else:
        form = CreateJournalForm()
    return render(request, 'journal/create.html', {'form': form})


def add(request):
    if request.method == 'POST':
        form = CreateJournalForm(request.POST)
        if form.is_valid():
            new_journal = {'mark_letter': form.cleaned_data['mark_letter'],
                           'mark_numeric': form.cleaned_data['mark_numeric'],
                           'group_id': form.cleaned_data['group'],
                           'teacher_id': form.cleaned_data['teacher'],
                           'subject_id': form.cleaned_data['subject'],
                           'student_id': form.cleaned_data['student']}
            db.saveJournal(new_journal)
            return redirect('/journal')
    else:
        form = CreateJournalForm()
    return render(request, 'journal/create.html', {'form': form})


def top_students(request):
    students = db.getTopStudentsAggregate()
    return render(request, 'journal/top.html', {'students': students})


def avarage(request):
    students = db.mapAvarageMarks()
    return render(request, 'journal/avarage.html', {'students': students})


def scholarship(request):
    students = db.mapMostHighGrades()
    print(students)
    return render(request, 'journal/highgrades.html', {'students': students})



