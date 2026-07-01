from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from main_app.models import Report


User = get_user_model()


# =============================================================================
# MODUL 1: PENGUJIAN OTORISASI & MANAJEMEN SESI
# =============================================================================

class AuthenticationTests(APITestCase):
    """
    Kelas pengujian untuk modul Otorisasi & Manajemen Sesi.

    Menguji mekanisme login JWT dan pembatasan akses endpoint berdasarkan
    peran pengguna.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_test',
            password='Password123!',
            is_admin=False,
        )

        self.admin = User.objects.create_user(
            username='admin_test',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

    def test_AUTH_01_login_warga_dengan_kredensial_valid(self):
        """
        AUTH-01:
        Warga login menggunakan username dan password yang benar.
        Sistem harus mengembalikan HTTP 200 serta token access dan refresh.
        """
        url = reverse('token_obtain_pair')

        payload = {
            'username': 'warga_test',
            'password': 'Password123!',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_AUTH_02_login_warga_dengan_password_salah(self):
        """
        AUTH-02:
        Warga login menggunakan password yang salah.
        Sistem harus menolak login dan tidak boleh menerbitkan token access.
        """
        url = reverse('token_obtain_pair')

        payload = {
            'username': 'warga_test',
            'password': 'passwordSALAH',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_AUTH_03_warga_tidak_bisa_akses_halaman_admin(self):
        """
        AUTH-03:
        Warga biasa mencoba mengakses halaman dashboard admin.

        Hasil yang diharapkan:
        - HTTP 403 Forbidden, atau
        - HTTP 302 Redirect.

        Pada project ini, citizen yang sudah login dan membuka /dashboard/
        akan ditolak dengan 403 Forbidden.
        """
        login_berhasil = self.client.login(
            username='warga_test',
            password='Password123!'
        )

        self.assertTrue(login_berhasil)

        response = self.client.get('/dashboard/')

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_302_FOUND]
        )