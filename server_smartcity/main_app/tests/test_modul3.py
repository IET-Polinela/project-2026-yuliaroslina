from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from main_app.models import Report


User = get_user_model()


# =============================================================================
# MODUL 3: PENGUJIAN ALUR KERJA & ATURAN BISNIS STATUS LAPORAN
# =============================================================================

class WorkflowStateTests(APITestCase):
    """
    Menguji aturan bisnis status laporan melalui REST API.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_wf',
            password='TestPass123!',
            is_admin=False
        )

        self.laporan_draft = Report.objects.create(
            title='Lampu Kampus Mati',
            category='Fasilitas Umum',
            description='Lampu di depan gedung rektorat tidak menyala.',
            location='Gedung Rektorat',
            status='DRAFT',
            reporter=self.warga,
        )

        self.laporan_reported = Report.objects.create(
            title='Saluran Air Tersumbat',
            category='Infrastruktur',
            description='Saluran air di samping kantin tersumbat.',
            location='Kantin Polinela',
            status='REPORTED',
            reporter=self.warga,
        )

        self.laporan_resolved = Report.objects.create(
            title='AC Rusak di Lab',
            category='Fasilitas Umum',
            description='AC di Lab CPS 1 sudah diperbaiki.',
            location='Lab CPS 1',
            status='RESOLVED',
            reporter=self.warga,
        )

    def test_WF_01_warga_mengajukan_draf_menjadi_reported(self):
        """
        WF-01:
        Pemilik laporan mengubah status laporan dari DRAFT menjadi REPORTED.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_draft.pk}/'
        payload = {
            'title': self.laporan_draft.title,
            'category': self.laporan_draft.category,
            'description': self.laporan_draft.description,
            'location': self.laporan_draft.location,
            'status': 'REPORTED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.laporan_draft.refresh_from_db()
        self.assertEqual(self.laporan_draft.status, 'REPORTED')

    def test_WF_02_tidak_bisa_edit_laporan_yang_sudah_reported(self):
        """
        WF-02:
        Warga tidak boleh mengubah isi laporan yang sudah berstatus REPORTED.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_reported.pk}/'
        payload = {
            'title': 'Judul Diubah Paksa',
            'category': self.laporan_reported.category,
            'description': 'Deskripsi ini seharusnya tidak berubah.',
            'location': self.laporan_reported.location,
            'status': 'REPORTED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.title, 'Saluran Air Tersumbat')
        self.assertEqual(
            self.laporan_reported.description,
            'Saluran air di samping kantin tersumbat.'
        )
        self.assertEqual(self.laporan_reported.status, 'REPORTED')

    def test_WF_05_laporan_resolved_tidak_bisa_diubah(self):
        """
        WF-05:
        Laporan yang sudah RESOLVED bersifat final dan tidak boleh diubah.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_resolved.pk}/'
        payload = {
            'title': 'Judul Resolved Diubah',
            'category': self.laporan_resolved.category,
            'description': 'Deskripsi resolved seharusnya tidak berubah.',
            'location': self.laporan_resolved.location,
            'status': 'RESOLVED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.laporan_resolved.refresh_from_db()
        self.assertEqual(self.laporan_resolved.title, 'AC Rusak di Lab')
        self.assertEqual(self.laporan_resolved.status, 'RESOLVED')


# =============================================================================
# MODUL 3b: PENGUJIAN ADMIN PORTAL — TRANSISI STATUS
# =============================================================================

class AdminWorkflowTests(TestCase):
    """
    Menguji alur kerja admin dalam mengubah status laporan.
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_portal',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

        self.citizen = User.objects.create_user(
            username='citizen_portal',
            password='CitizenPass123!',
            is_admin=False,
            is_staff=False,
        )

        self.laporan_reported = Report.objects.create(
            title='Jalan Rusak di Blok C',
            category='Infrastruktur',
            description='Jalan berlubang parah di area parkir Blok C.',
            location='Blok C Polinela',
            status='REPORTED',
            reporter=self.citizen,
        )

    def test_WF_03_admin_mengubah_status_reported_ke_verified(self):
        """
        WF-03:
        Admin mengubah status laporan dari REPORTED menjadi VERIFIED.
        """
        login_berhasil = self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )
        self.assertTrue(login_berhasil)

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.laporan_reported.pk}),
            {'status': 'VERIFIED'}
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_302_FOUND]
        )

        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.status, 'VERIFIED')

    def test_WF_04_tidak_ada_transisi_langsung_ke_resolved_dari_reported(self):
        """
        WF-04:
        Laporan REPORTED tidak boleh langsung lompat menjadi RESOLVED.
        Transisi valid berikutnya hanya VERIFIED.
        """
        login_berhasil = self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )
        self.assertTrue(login_berhasil)

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.laporan_reported.pk}),
            {'status': 'RESOLVED'}
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_302_FOUND]
        )

        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.status, 'REPORTED')
        self.assertNotEqual(self.laporan_reported.status, 'RESOLVED')