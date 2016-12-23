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
    student = forms.ChoiceField(label='Student', choices=db.getStudentList())
    subject = forms.ChoiceField(label='Subject', choices=db.getSubjectList())
    group = forms.ChoiceField(label='Group', choices=db.getGroupList())


class CreateTeacherForm(forms.Form):
    teacher_name = forms.CharField(label="Name")
    teacher_phone = forms.CharField(label="Phone")


class MarkFilterForm(forms.Form):
    mark_min = forms.IntegerField(label='Mark minimal', required=True)
    mark_max = forms.IntegerField(label='Mark maximal', required=True)