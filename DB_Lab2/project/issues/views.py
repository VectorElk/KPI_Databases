from datetime import datetime
import json
import os

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import require_POST

from .models import Issue, User, IssuePriority, IssueStatus
from .forms import UpdateIssueForm, CreateIssueForm, FilterIssuesForm


def list_issues(request):
    filter = FilterIssuesForm(request.GET if request.GET else None)
    if filter.is_valid():
        issues_list = Issue.get_filtered(**filter.cleaned_data)
    else:
        issues_list = Issue.get_all()
    return render(request, 'issues/index.html', {'issues_list': issues_list, 'filter': filter})


def view_user(request, user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise Http404('No such user')
    return render(request, 'issues/user.html', {'user': user})


def issue_view(request, issue_id):
    issue = Issue.get_by_id(issue_id)
    if not issue:
        raise Http404('No such issue')
    if request.method == 'POST':
        form = UpdateIssueForm(request.POST)
        if form.is_valid():
            issue.title = form.cleaned_data['title']
            issue.description = form.cleaned_data['description']
            issue.priority = IssuePriority.get_by_id(form.cleaned_data['priority'])
            issue.status = IssueStatus.get_by_id(form.cleaned_data['status'])
            new_assigned_id = form.cleaned_data['assigned_to']
            issue.assigned_to = User.get_by_id(new_assigned_id) if new_assigned_id else None
            issue.update_time = timezone.now()
            issue.save()
            return HttpResponseRedirect(reverse('issues:view', args=(issue.id,)))
    else:
        form = UpdateIssueForm(initial={
            'title': issue.title,
            'description': issue.description,
            'priority': issue.priority.id,
            'status': issue.status.id,
            'assigned_to': issue.assigned_to.id if issue.assigned_to else None,
        })
    return render(request, 'issues/view.html', {'issue': issue, 'form': form})


def issue_create(request):
    if request.method == 'POST':
        form = CreateIssueForm(request.POST)
        if form.is_valid():
            created_id = form.cleaned_data['created_by']
            assigned_id = form.cleaned_data['assigned_to']
            assigned_to = User.get_by_id(assigned_id) if assigned_id else None
            status_id = form.cleaned_data['status']
            priority_id = form.cleaned_data['priority']

            issue = Issue(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                create_time=timezone.now(),
                priority=IssuePriority.get_by_id(priority_id),
                status=IssueStatus.get_by_id(status_id),
                created_by=User.get_by_id(created_id),
                assigned_to=assigned_to
            )
            issue.save()

            return HttpResponseRedirect(reverse('issues:view', args=(issue.id,)))
    else:
        form = CreateIssueForm()
    return render(request, 'issues/create.html', {'form': form})


@require_POST
def issue_delete(request, issue_id):
    Issue.delete(issue_id)
    return redirect('issues:index')


@require_POST
def reload_db(request):
    app_dir = os.path.dirname(__file__)
    with open(os.path.join(app_dir, 'data.json')) as f:
        raw_data = json.load(f)
        priorities = [
            IssuePriority(
                u['text'],
                u['priority_value']
            )
            for u in raw_data['priorities']
        ]
        IssuePriority.delete()
        IssuePriority.bulk_create(priorities)
        statuses = [
            IssueStatus(
                u['text'],
                u['icon']
            )
            for u in raw_data['statuses']
        ]
        IssueStatus.delete()
        IssueStatus.bulk_create(statuses)
        users = [
            User(
                u['username'],
                u['email'],
                u['password'],
                datetime.utcfromtimestamp(int(u['create_time'])),
                bool(u.get('blocked', False))
            )
            for u in raw_data['users']
        ]
        User.delete()
        User.bulk_create(users)

    return redirect('issues:index')
