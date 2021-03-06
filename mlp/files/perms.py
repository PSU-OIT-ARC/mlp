import os
from permissions import permission
from django.db.models import Q
from mlp.users.models import User
from mlp.groups.enums import UserRole
from mlp.groups.models import Group, Roster, GroupFile
from mlp.groups.perms import is_lead_student
from mlp.users.perms import has_admin_access
from .enums import FileType
from .models import File

@permission
def can_upload_file(user):
    # only teachers and staff can upload files
    return has_admin_access(user)

@permission(model=Group)
def can_upload_to_group(user, group):
    return has_admin_access(user) or is_lead_student(user,group)

@permission(model=File)
def can_edit_file(user, file):
    return has_admin_access(user) or file.uploaded_by == user

@permission(model=File)
def can_list_file(user, file):
    return can_list_all_files(user) or file.uploaded_by == user

@permission
def can_list_all_files(user):
    return has_admin_access(user)

@permission(model=File)
def can_view_file(user, file):
    return user.is_authenticated()

@permission(model=File)
def can_download_file(user, file):
    return can_edit_file(user, file) or file.type == FileType.TEXT
