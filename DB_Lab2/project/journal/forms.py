from django import forms
from DatabaseManager import DB

db = DB()


class UpdateJournalForm(forms.Form):
    mark_numeric = forms.IntegerField(label='Mark')
    mark_letter = forms.CharField(label='Mark alphabetical')
    teacher = forms.ChoiceField(label='Teacher', choices=db.getTeacherList())
    student = forms.ChoiceField(label='Student', choices=db.getStudentList())
    subject = forms.ChoiceField(label='Subject', choices=db.getSubjectList())
    group = forms.ChoiceField(label='Group', choices=db.getGroupList())


class CreateJournalForm(forms.Form):
    mark_numeric = forms.IntegerField(label='Mark')
    mark_letter = forms.CharField(label='Mark alphabetical')
    teacher = forms.ChoiceField(label='Teacher', choices=db.getTeacherList())

