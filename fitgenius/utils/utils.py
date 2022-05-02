
from guardian.shortcuts import assign_perm, remove_perm


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
