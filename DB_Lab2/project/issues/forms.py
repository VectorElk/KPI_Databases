from django import forms

from .models import IssuePriority, IssueStatus, User


class UpdateIssueForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)
    priority = forms.ChoiceField(label='Priority', choices=IssuePriority.get_choices())
    status = forms.ChoiceField(label='Status', choices=IssueStatus.get_choices())
    assigned_to = forms.ChoiceField(label='Assigned to', choices=User.get_choices(), required=False)


class CreateIssueForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)
    priority = forms.ChoiceField(label='Priority', choices=IssuePriority.get_choices())
    status = forms.ChoiceField(label='Status', choices=IssueStatus.get_choices())
    created_by = forms.ChoiceField(label='Created by', choices=User.get_choices(allow_empty=False))
    assigned_to = forms.ChoiceField(label='Assigned to', choices=User.get_choices(), required=False)


class FilterIssuesForm(forms.Form):
    reporter_is_blocked = forms.TypedChoiceField(
        label='Reported by blocked',
        empty_value=None,
        coerce=lambda x: x == 'True',
        choices=((None, 'maybe'), (True, 'yes'), (False, 'no')),
        required=False
    )
    min_date = forms.DateTimeField(label='Start date', required=False)
    max_date = forms.DateTimeField(label='End date', required=False)
    keywords = forms.CharField(label='Keywords', max_length=128, required=False)

