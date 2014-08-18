from model_mommy.mommy import make
import os, sys, shutil, mimetypes, math, tempfile, threading, mock
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.unittest import skipIf
from mlp.users.models import User
from mlp.tags.models import Tag
from mlp.files.models import File
from mlp.files.enums import FileType, FileStatus
from .models import Class, Roster, ClassFile, SignedUp
from .perms import decorators
from .enums import UserRole

def create_classes(self):
    """
    Create new classes
    """
    c = Class(crn=12345, name="class 101", description="this is a description")
    c.save()
    self.classes = c

    r = Roster(user=self.user, _class=c, role=UserRole.ADMIN)
    r.save()
    self.roster = r

def create_users(self):
    """
    Create users
    """
    u = User(first_name="user", last_name="jones", email="user@pdx.edu", is_staff=True)
    u.set_password("foobar")
    u.save()
    self.user = u

    a = User(first_name="admin", last_name="jones", email="admin@pdx.edu", is_staff=True)
    a.set_password("foobar")
    a.save()
    self.admin = a

def create_class_files(self):
    """
    Create class files
    """
    cf = ClassFile(_class=self.classes, file=self.file)
    cf.save()
    self.class_file = cf

def create_files(self):
    """
    Create files
    """
    f = open(os.path.join(settings.MEDIA_ROOT, "test.txt"), "w")
    f.write("this is a test file")
    f.close()

    f = File(
        name="Kittens",
        description="Kittens and stuff",
        file="test.txt",
        type=FileType.VIDEO,
        status=FileStatus.READY,
        uploaded_by=self.user,
        tmp_path="kittens",
    )
    f.save()
    self.file = f

class ClassTest(TestCase):
    """
    Test a class model
    """
    def setUp(self):
        super(ClassTest, self).setUp()
        create_users(self)
        create_classes(self)
        create_files(self)
        self.client.login(email=self.user.email, password="foobar")

    def test_list_view(self):
        response = self.client.get(reverse('classes-list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        response = self.client.get(reverse('classes-detail', args=(self.classes.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_enroll(self):
        response = self.client.get(reverse('classes-enroll', args=(self.classes.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_file_list(self):
        response = self.client.get(reverse('classes-file_list', args=(self.classes.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_file_add(self):
        response = self.client.get(reverse('classes-file_add', args=(self.classes.pk, self.file.pk,)))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classes-file_add', args=(self.classes.pk, self.file.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_file_remove(self):
        create_class_files(self)
        pre_count = ClassFile.objects.count()
        response = self.client.get(reverse('classes-file_remove', args=(self.classes.pk, self.file.pk,)))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classes-file_remove', args=(self.classes.pk, self.file.pk,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(pre_count-1, ClassFile.objects.count())

    def test_edit_get(self):
        response = self.client.get(reverse('classes-edit', args=(self.classes.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        data = {
            "name": "class2",
            "crn": 12345,
            "description": "desc",
        }
        response = self.client.post(reverse('classes-edit', args=(self.classes.pk,)), data)
        self.assertEqual(response.status_code, 302)

    def test_create(self):
        data = {
            "name": "class2",
            "crn": 12345,
            "description": "desc",
        }
        response = self.client.post(reverse('classes-create'), data)
        self.assertEqual(response.status_code, 302)

    def test_delete(self):
        response = self.client.get(reverse('classes-delete', args=(self.classes.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_make_instructor(self):
        response = self.client.get(reverse('classes-make_instructor', args=(self.classes.pk, self.user.pk)))
        self.assertEqual(response.status_code, 302)

class RosterTest(TestCase):
    """
    Test a roster
    """
    def setUp(self):
        super(RosterTest, self).setUp()
        create_users(self)
        create_classes(self)
        create_files(self)
        self.client.login(email=self.user.email, password="foobar")

    def test_roster_add(self):
        response = self.client.get(reverse('roster-add', args=(self.classes.pk, self.user.pk,)))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('roster-add', args=(self.classes.pk, self.admin.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_roster_remove(self):
        response = self.client.get(reverse('roster-remove', args=(self.classes.pk, self.user.pk,)))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('roster-remove', args=(self.classes.pk, self.user.pk,)))
        self.assertEqual(response.status_code, 302)

class SignedUpTest(TestCase):
    def setUp(self):
        super(SignedUpTest, self).setUp()
        create_users(self)
        create_classes(self)
        create_files(self)
        create_class_files(self)
        self.client.login(email=self.user.email, password="foobar")

    def test_signed_up_add(self):
        response = self.client.get(reverse('signed_up-add', args=(self.classes.pk, self.user.pk,)))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('signed_up-add', args=(self.classes.pk, self.user.pk,)))
        self.assertEqual(response.status_code, 302)

