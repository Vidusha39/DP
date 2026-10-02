from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from teachers.models import Teacher


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create standard user
        self.username = 'testuser'
        self.old_password = 'OldPassword@123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.old_password,
            first_name='Sunil'
        )
        UserProfile.objects.create(user=self.user, role='TEACHER', phone='0771122334')

    def test_change_password_login_required(self):
        """Unauthenticated requests to change-password should redirect to login."""
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_change_password_view_get(self):
        """Logged in user can access change password page with proper fields."""
        self.client.login(username=self.username, password=self.old_password)
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/change_password.html')
        self.assertContains(response, 'මුරපදය වෙනස් කිරීම')
        self.assertContains(response, 'old_password')
        self.assertContains(response, 'new_password1')
        self.assertContains(response, 'new_password2')

    def test_change_password_success(self):
        """User can successfully change their password and remain authenticated."""
        self.client.login(username=self.username, password=self.old_password)
        new_password = 'NewSecretPassword@456'

        response = self.client.post(reverse('change_password'), {
            'old_password': self.old_password,
            'new_password1': new_password,
            'new_password2': new_password,
        }, follow=True)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, 'මුරපදය සාර්ථකව වෙනස් කරන ලදී')

        # Verify password in database
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(self.user.check_password(self.old_password))

        # Verify the user is still logged in after changing password
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_change_password_wrong_old_password(self):
        """Incorrect old password should produce an error and not change password."""
        self.client.login(username=self.username, password=self.old_password)
        new_password = 'NewSecretPassword@456'

        response = self.client.post(reverse('change_password'), {
            'old_password': 'IncorrectOldPassword',
            'new_password1': new_password,
            'new_password2': new_password,
        })

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.old_password))
        self.assertFalse(self.user.check_password(new_password))
        self.assertContains(response, 'පැරණි මුරපදය වැරදිය')

    def test_change_password_mismatched_new_passwords(self):
        """Mismatched new passwords should fail validation."""
        self.client.login(username=self.username, password=self.old_password)

        response = self.client.post(reverse('change_password'), {
            'old_password': self.old_password,
            'new_password1': 'NewSecretPassword@456',
            'new_password2': 'CompletelyDifferent@789',
        })

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.old_password))
        self.assertContains(response, 'එකිනෙකට නොගැළපේ')

    def test_navbar_contains_change_password_link_for_authenticated_users(self):
        """Navbar across pages should include the change password link for logged-in users."""
        self.client.login(username=self.username, password=self.old_password)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('change_password'))
        self.assertContains(response, '🔑 මුරපදය')

    def test_admin_dashboard_contains_change_password_button(self):
        """Admin dashboard displays change password option."""
        admin_user = User.objects.create_superuser(
            username='adminuser',
            password='AdminPassword@123',
            email='admin@test.com'
        )
        UserProfile.objects.create(user=admin_user, role='ADMIN', phone='0779999999')
        self.client.login(username='adminuser', password='AdminPassword@123')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('change_password'))

    def test_teacher_dashboard_contains_change_password_button(self):
        """Teacher dashboard displays change password option."""
        teacher_user = User.objects.create_user(
            username='teacheruser',
            password='TeacherPassword@123'
        )
        UserProfile.objects.create(user=teacher_user, role='TEACHER', phone='0778888888')
        Teacher.objects.create(
            user=teacher_user,
            title='MR',
            full_name_sinhala='කේ. ගුණසේකර',
            name_with_initials='කේ. ගුණසේකර',
            phone='0778888888'
        )
        self.client.login(username='teacheruser', password='TeacherPassword@123')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('change_password'))

    def test_newly_created_teacher_can_login_and_change_password(self):
        """End-to-end: Teacher created in system can log in and change their password."""
        # 1. Admin creates teacher
        admin_user = User.objects.create_superuser(
            username='principal_admin',
            password='AdminPassword@123'
        )
        UserProfile.objects.create(user=admin_user, role='ADMIN', phone='0770000000')
        self.client.login(username='principal_admin', password='AdminPassword@123')

        teacher_initial_pw = 'InitialTeacher@123'
        create_res = self.client.post(reverse('create_teacher'), {
            'username': 'newteacher2026',
            'password': teacher_initial_pw,
            'title': 'MISS',
            'full_name': 'නිලන්ති පෙරේරා',
            'name_initials': 'එන්. පෙරේරා',
            'phone': '0712345678',
            'whatsapp': '0712345678',
            'address': 'කොළඹ පාර',
            'qualifications': 'BA, Dip in Buddhism'
        }, follow=True)
        self.assertEqual(create_res.status_code, 200)
        self.assertTrue(User.objects.filter(username='newteacher2026').exists())

        # 2. Teacher logs in with initial password
        self.client.logout()
        login_res = self.client.post(reverse('login'), {
            'username': 'newteacher2026',
            'password': teacher_initial_pw
        }, follow=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertRedirects(login_res, reverse('dashboard'))

        # 3. Teacher navigates to change password and updates it
        teacher_new_pw = 'MyPersonalUpdatedPassword@999'
        change_res = self.client.post(reverse('change_password'), {
            'old_password': teacher_initial_pw,
            'new_password1': teacher_new_pw,
            'new_password2': teacher_new_pw,
        }, follow=True)
        self.assertEqual(change_res.status_code, 200)
        self.assertRedirects(change_res, reverse('dashboard'))

        # 4. Verify teacher can now log in with new password
        self.client.logout()
        new_login_res = self.client.post(reverse('login'), {
            'username': 'newteacher2026',
            'password': teacher_new_pw
        }, follow=True)
        self.assertEqual(new_login_res.status_code, 200)
        self.assertRedirects(new_login_res, reverse('dashboard'))
