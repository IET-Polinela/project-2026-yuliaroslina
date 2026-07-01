from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from main_app.models import Report


User = get_user_model()


# =============================================================================
# MODUL 2: PENGUJIAN VISIBILITAS DATA & PRIVASI PELAPOR
# =============================================================================

class PrivacyAndDataHidingTests(APITestCase):
    """
    Kelas pengujian untuk modul Visibilitas Data & Privasi Pelapor.

    Menguji mekanisme penyamaran identitas dan isolasi data draf antar pengguna.
    """

    def setUp(self):
        self.warga_a = User.objects.create_user(
            username='warga_a',
            password='TestPass123!',
            is_admin=False
        )

        self.warga_b = User.objects.create_user(
            username='warga_b',
            password='TestPass123!',
            is_admin=False
        )

        self.draft_milik_b = Report.objects.create(
            title='Draf Rahasia Warga B',
            category='Infrastruktur',
            description='Ini adalah draf yang belum diajukan.',
            location='Lokasi Rahasia',
            status='DRAFT',
            reporter=self.warga_b,
        )

        self.laporan_publik_a = Report.objects.create(
            title='Jalan Berlubang di Depan Kampus',
            category='Infrastruktur',
            description='Ada lubang besar yang membahayakan pengendara.',
            location='Jl. Soekarno Hatta',
            status='REPORTED',
            reporter=self.warga_a,
        )

        self.laporan_publik_b = Report.objects.create(
            title='Sampah Menumpuk di Trotoar',
            category='Kebersihan',
            description='Sampah tidak diangkut selama seminggu.',
            location='Jl. Gatot Subroto',
            status='REPORTED',
            reporter=self.warga_b,
        )

    def test_PRIV_01_feed_kota_menyembunyikan_identitas_reporter(self):
        """
        PRIV-01:
        Warga A mengakses feed kota.
        Reporter pada feed publik harus tampil sebagai Warga Anonim.
        """
        self.client.force_authenticate(user=self.warga_a)

        response = self.client.get('/api/report/?tab=feed')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', [])
        self.assertTrue(len(results) > 0)

        for laporan in results:
            self.assertEqual(laporan['reporter'], 'Warga Anonim')

    def test_PRIV_02_laporan_saya_menampilkan_nama_asli(self):
        """
        PRIV-02:
        Warga A mengakses daftar laporan miliknya sendiri.
        reporter_name harus menampilkan username asli pemilik laporan.
        """
        self.client.force_authenticate(user=self.warga_a)

        response = self.client.get('/api/report/?tab=my_reports')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', [])
        self.assertTrue(len(results) > 0)

        for laporan in results:
            self.assertEqual(laporan['reporter_name'], 'warga_a')

    def test_PRIV_03_tidak_bisa_baca_draf_orang_lain(self):
        """
        PRIV-03:
        Warga A mencoba membaca detail draf milik Warga B.
        Sistem harus menyembunyikan draf asing dengan HTTP 404.
        """
        self.client.force_authenticate(user=self.warga_a)

        url = f'/api/report/{self.draft_milik_b.pk}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_PRIV_04_tidak_bisa_modifikasi_draf_orang_lain(self):
        """
        PRIV-04:
        Warga A mencoba mengubah draf milik Warga B.
        Sistem harus mengembalikan HTTP 404 dan data asli tetap aman.
        """
        self.client.force_authenticate(user=self.warga_a)

        url = f'/api/report/{self.draft_milik_b.pk}/'

        payload = {
            'title': 'Judul Diubah Paksa',
            'category': 'Infrastruktur',
            'description': 'Deskripsi ini seharusnya tidak tersimpan.',
            'location': 'Lokasi Diubah',
            'status': 'DRAFT',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.draft_milik_b.refresh_from_db()
        self.assertEqual(self.draft_milik_b.title, 'Draf Rahasia Warga B')
        self.assertEqual(self.draft_milik_b.description, 'Ini adalah draf yang belum diajukan.')
        self.assertEqual(self.draft_milik_b.location, 'Lokasi Rahasia')
        self.assertEqual(self.draft_milik_b.status, 'DRAFT')