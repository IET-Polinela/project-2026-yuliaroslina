from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from main_app.models import Report


User = get_user_model()


# =============================================================================
# MODUL 4: PENGUJIAN FUNGSIONALITAS DASAR & VALIDASI INPUT
# =============================================================================

class CRUDAndValidationTests(APITestCase):
    """
    Kelas pengujian untuk fungsionalitas dasar dan validasi input.

    Menguji pembuatan laporan baru, validasi field wajib,
    dan keamanan dari input HTML/script.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_crud',
            password='TestPass123!',
            is_admin=False,
            is_member=True
        )

        self.client.force_authenticate(user=self.warga)

    def test_FT_01_buat_laporan_dengan_data_lengkap(self):
        """
        FT-01:
        Warga membuat laporan baru dengan data lengkap.
        Sistem harus mengembalikan HTTP 201 Created.
        """
        payload = {
            'title': 'Lampu Jalan Mati',
            'category': 'Infrastruktur',
            'description': 'Lampu jalan di depan kampus mati sejak semalam.',
            'location': 'Depan Kampus',
            'status': 'DRAFT',
        }

        response = self.client.post('/api/report/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Report.objects.filter(title='Lampu Jalan Mati').exists()
        )

        laporan = Report.objects.get(title='Lampu Jalan Mati')
        self.assertEqual(laporan.reporter, self.warga)
        self.assertEqual(laporan.status, 'DRAFT')

    def test_FT_02_ditolak_jika_judul_kosong(self):
        """
        FT-02:
        Warga membuat laporan tanpa field title.
        Sistem harus menolak dengan HTTP 400 Bad Request.
        """
        payload = {
            'category': 'Infrastruktur',
            'description': 'Deskripsi laporan tetap diisi.',
            'location': 'Gedung A',
            'status': 'DRAFT',
        }

        response = self.client.post('/api/report/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_FT_03_ditolak_jika_deskripsi_kosong(self):
        """
        FT-03:
        Warga membuat laporan tanpa field description.
        Sistem harus menolak dengan HTTP 400 Bad Request.
        """
        payload = {
            'title': 'Laporan Tanpa Deskripsi',
            'category': 'Infrastruktur',
            'location': 'Gedung B',
            'status': 'DRAFT',
        }

        response = self.client.post('/api/report/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)

    def test_FT_04_xss_script_disimpan_sebagai_string_literal(self):
        """
        FT-04:
        Deskripsi laporan berisi script XSS.
        Data tetap diterima sebagai string literal, bukan dieksekusi.
        """
        kode_xss = '<script>alert("xss")</script>'

        payload = {
            'title': 'Laporan XSS Test',
            'category': 'Infrastruktur',
            'description': kode_xss,
            'location': 'Lab Keamanan Siber',
            'status': 'DRAFT',
        }

        response = self.client.post('/api/report/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        laporan = Report.objects.get(title='Laporan XSS Test')

        self.assertIn(
            'script',
            laporan.description.lower()
        )