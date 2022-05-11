from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import assign_perm, remove_perm

User = get_user_model()

# assigns user's permission based on user's group
def assign_user_permission(user):
    manager_qs = user.groups.filter(name='manager')

    if manager_qs.exists():
        """Assign manager permission"""
        assign_perm('change_company', user, user.company)
        assign_perm('view_company', user, user.company)
        user.is_manager = True
        # user.save()

    agent_qs = user.groups.filter(name='agent')
    if agent_qs.exists():
        """Assign agent permission"""
        assign_perm('view_company', user, user.company)
        # user.is_manager = False
        # user.save()


# removes user permission when group is changed
def remove_user_permission(user):
    if not user.groups.filter(name='manager').exists():
        """Remove manager permission"""
        remove_perm('change_company', user, user.company)
        remove_perm('view_company', user, user.company)

    if not user.groups.filter(name='agent').exists():
        """Remove agent permission"""
        remove_perm('view_company', user, user.company)


# removes user permission to company when user's company is chanaged
def remove_user_perm_on_company_change(user, old_company):
    remove_perm('change_company', user, old_company)
    remove_perm('view_company', user, old_company)


class PortalRestrictionMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.user_type == User.MANAGER:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class AjaxTemplateMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.is_ajax():
            self.template_name = self.ajax_template_name
        return super().dispatch(request, *args, **kwargs)
