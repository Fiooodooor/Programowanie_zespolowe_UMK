from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from pznsi.models import User, Environment, Project, ProjectCategory


class ApiTests(TestCase):
    fixtures = ['category_data']

    def setUp(self):
        User.objects.create_superuser('admin', 'ad@w.pl', 'admin')
        test = User.objects.create_user('test', 'ad@w.pl', 'test')
        test2 = User.objects.create_user('test2', 'ad@w.pl', 'test')
        User.objects.create_user('test3', 'ad@w.pl', 'test')
        test_envi = Environment.objects.create(environment_name='test_envi',
                                               owner=test)
        Project.objects.create(project_name='test_pro',
                               owner=test2,
                               project_category=ProjectCategory.objects.get(id=1),
                               project_content='kontent',
                               environment=test_envi)

    def test_adding_project_permissions_as_project_owner(self):
        client = APIClient()
        user = User.objects.get(username='test2')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        project = Project.objects.get(id=1)
        response = client.post('/api/projects/1/add_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_project_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertTrue(test_user.has_perm('view_project_instance', project))

    def test_adding_project_permissions_as_super_user(self):
        client = APIClient()
        user = User.objects.get(username='admin')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        project = Project.objects.get(id=1)
        response = client.post('/api/projects/1/add_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_project_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertTrue(test_user.has_perm('view_project_instance', project))

    def test_adding_project_permissions_as_not_permitted_user(self):
        client = APIClient()
        user = User.objects.get(username='test3')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        project = Project.objects.get(id=1)
        response = client.post('/api/projects/1/add_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_project_instance']}, format='json')
        self.assertEqual(404, response.status_code)
        self.assertFalse(test_user.has_perm('view_project_instance', project))

    def test_adding_project_permissions_as_environment_owner(self):
        client = APIClient()
        user = User.objects.get(username='test')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        environment = Environment.objects.get(id=1)
        response = client.post('/api/projects/1/add_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_project_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertTrue(test_user.has_perm('view_environment_instance', environment))

    def test_adding_environment_permissions_as_environment_owner(self):
        client = APIClient()
        user = User.objects.get(username='test')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        environment = Environment.objects.get(id=1)
        response = client.post('/api/environments/1/add_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_environment_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertTrue(test_user.has_perm('view_environment_instance', environment))

    def test_adding_environment_permissions_as_not_permitted_user(self):
        client = APIClient()
        user = User.objects.get(username='test2')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        environment = Environment.objects.get(id=1)
        response = client.post('/api/environments/1/add_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_environment_instance']}, format='json')
        self.assertEqual(403, response.status_code)
        self.assertFalse(test_user.has_perm('view_environment_instance', environment))

    def test_removing_environment_permissions_as_environment_owner(self):
        client = APIClient()
        user = User.objects.get(username='test')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        test_user.groups.add(Group.objects.get(name='1_environment_viewers'))
        test_user.groups.add(Group.objects.get(name='1_environment_editors'))
        environment = Environment.objects.get(id=1)
        response = client.post('/api/environments/1/remove_permissions/',
                               {'user_id': test_user.id, 'permissions': ['edit_environment_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertFalse(test_user.has_perm('edit_environment_instance', environment))

    def test_removing_environment_permissions_as_not_permitted_user(self):
        client = APIClient()
        user = User.objects.get(username='test2')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        test_user.groups.add(Group.objects.get(name='1_environment_viewers'))
        test_user.groups.add(Group.objects.get(name='1_environment_editors'))
        environment = Environment.objects.get(id=1)
        response = client.post('/api/environments/1/remove_permissions/',
                               {'user_id': test_user.id, 'permissions': ['edit_environment_instance']}, format='json')
        self.assertEqual(403, response.status_code)
        self.assertTrue(test_user.has_perm('edit_environment_instance', environment))

    def test_removing_project_permissions_as_project_owner(self):
        client = APIClient()
        user = User.objects.get(username='test2')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        test_user.groups.add(Group.objects.get(name='1_project_viewers'))
        project = Project.objects.get(id=1)
        response = client.post('/api/projects/1/remove_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_project_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertFalse(test_user.has_perm('view_project_instance', project))

    def test_removing_project_permissions_as_super_user(self):
        client = APIClient()
        user = User.objects.get(username='admin')
        client.force_authenticate(user=user)
        test_user = User.objects.get(username='test3')
        test_user.groups.add(Group.objects.get(name='1_project_viewers'))
        project = Project.objects.get(id=1)
        response = client.post('/api/projects/1/remove_permissions/',
                               {'user_id': test_user.id, 'permissions': ['view_project_instance']}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertFalse(test_user.has_perm('view_project_instance', project))
