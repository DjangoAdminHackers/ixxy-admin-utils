from admin_tools.dashboard.modules import LinkList
from django.urls import reverse
from linkcheck.views import get_status_message


class PermCheckingLinkList(LinkList):

    def __init__(self, title=None, **kwargs):
        self.required_perms = kwargs.pop('required_perms', [])
        super(PermCheckingLinkList, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        super(PermCheckingLinkList, self).init_with_context(context)
        if self.required_perms:
            user = context['request'].user
            if not user.is_superuser and not user.has_perms(self.required_perms):
                self.children = None
                self.pre_content = None
                self.post_content = None


class GroupCheckingLinkList(LinkList):

    def __init__(self, title=None, **kwargs):
        self.required_group = kwargs.pop('required_group', None)
        super(GroupCheckingLinkList, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        super(GroupCheckingLinkList, self).init_with_context(context)
        if self.required_group:
            user = context['request'].user
            if not user.is_superuser and not context['request'].user.groups.filter(name=self.required_group):
                self.children = None
                self.pre_content = None
                self.post_content = None


linkcheck_perm_checking_dashboard_module = PermCheckingLinkList(
    title="Linkchecker",
    pre_content=get_status_message,
    children=(
        {'title': 'Valid links', 'url': reverse('linkcheck_report') + '?filters=show_valid'},
        {'title': 'Broken links', 'url': reverse('linkcheck_report')},
        {'title': 'Untested links', 'url': reverse('linkcheck_report') + '?filters=show_unchecked'},
        {'title': 'Ignored links', 'url': reverse('linkcheck_report') + '?filters=ignored'},
    ),
    required_perms=['linkcheck.change_link'],
)