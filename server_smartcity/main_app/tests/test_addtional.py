from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.messages.storage.fallback import FallbackStorage
from rest_framework.test import APITestCase

from main_app.models import Report


User = get_user_model()


class SerializerAndModelCoverageTests(APITestCase):
    """
    Test tambahan untuk menaikkan coverage model dan serializer.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_str_test',
            password='Password123!',
            is_admin=False
        )

    def test_report_model_str(self):
        report = Report.objects.create(
            title='Laporan Str Uji',
            category='Lainnya',
            description='Deskripsi',
            location='Lokasi',
            status='REPORTED',
            reporter=self.warga
        )

        self.assertEqual(str(report), 'Laporan Str Uji')

    def test_report_serializer_no_request_context(self):
        from main_app.serializers import ReportSerializer

        report = Report.objects.create(
            title='Laporan Serializer Uji',
            category='Lainnya',
            description='Deskripsi',
            location='Lokasi',
            status='REPORTED',
            reporter=self.warga
        )

        serializer = ReportSerializer(report, context={})

        self.assertFalse(serializer.data['is_owner'])
        self.assertEqual(serializer.data['reporter_name'], 'Warga Anonim')


class MainAppMonolithicViewsCoverageTests(TestCase):
    """
    Test tambahan untuk view monolitik main_app/views.py.
    Disesuaikan dengan aturan project:
    - Admin tidak boleh tambah laporan dari backend.
    - Admin tidak boleh edit laporan warga.
    - Admin tidak boleh hapus laporan warga.
    - Admin hanya boleh update status.
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_mono',
            password='Password123!',
            is_admin=True,
            is_staff=True
        )

        self.citizen = User.objects.create_user(
            username='citizen_mono',
            password='Password123!',
            is_admin=False,
            is_staff=False
        )

        self.report = Report.objects.create(
            title='Laporan Monolitik Uji',
            category='Infrastruktur',
            description='Ada kerusakan infrastruktur.',
            location='Bandung',
            status='REPORTED',
            reporter=self.citizen
        )

    def test_report_detail_api_valid(self):
        from main_app.views import report_detail_api

        factory = RequestFactory()
        request = factory.get('/dummy-url/')

        response = report_detail_api(request, self.report.id)

        self.assertEqual(response.status_code, 200)

    def test_report_detail_api_invalid(self):
        from main_app.views import report_detail_api

        factory = RequestFactory()
        request = factory.get('/dummy-url/')

        with self.assertRaises(Http404):
            report_detail_api(request, 99999)

    def test_report_search_unauthenticated(self):
        response = self.client.get(reverse('report_search') + '?q=Lampu')

        self.assertEqual(response.status_code, 403)

    def test_report_search_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.get(reverse('report_search') + '?q=Lampu')

        self.assertEqual(response.status_code, 403)

    def test_report_search_admin(self):
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.get(reverse('report_search') + '?q=Monolitik')

        self.assertEqual(response.status_code, 200)

    def test_home_view(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_app/home.html')

    def test_report_list_view_unauthenticated(self):
        response = self.client.get(reverse('report_list'))

        self.assertEqual(response.status_code, 302)

    def test_report_list_view_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.get(reverse('report_list'))

        self.assertEqual(response.status_code, 302)

    def test_report_list_view_admin(self):
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.get(reverse('report_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_app/report_list.html')

    def test_report_create_view_unauthenticated(self):
        response = self.client.get(reverse('add_report'))

        self.assertEqual(response.status_code, 302)

    def test_report_create_view_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.get(reverse('add_report'))

        self.assertEqual(response.status_code, 302)

    def test_report_create_view_admin_get(self):
        """
        Admin tidak boleh membuka halaman tambah laporan backend.
        Penambahan laporan hanya lewat Portal Citizen.
        """
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.get(reverse('add_report'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report_list'))

    def test_report_create_view_admin_post_valid(self):
        """
        Admin tidak boleh membuat laporan dari backend.
        Data tidak boleh tersimpan.
        """
        self.client.login(username='admin_mono', password='Password123!')

        payload = {
            'title': 'Laporan Form Baru',
            'category': 'Infrastruktur',
            'description': 'Deskripsi baru.',
            'location': 'Jakarta',
            'status': 'DRAFT'
        }

        response = self.client.post(reverse('add_report'), payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report_list'))
        self.assertFalse(
            Report.objects.filter(title='Laporan Form Baru').exists()
        )

    def test_report_detail_view_unauthenticated(self):
        response = self.client.get(
            reverse('report_detail', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_report_detail_view_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.get(
            reverse('report_detail', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_report_detail_view_admin(self):
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.get(
            reverse('report_detail', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 200)

    def test_report_update_view_unauthenticated(self):
        response = self.client.get(
            reverse('update_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_report_update_view_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.get(
            reverse('update_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_report_update_view_admin_get(self):
        """
        Admin tidak boleh membuka halaman edit laporan warga.
        """
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.get(
            reverse('update_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_report_update_view_admin_post_valid(self):
        """
        Admin tidak boleh mengubah isi laporan warga.
        """
        self.client.login(username='admin_mono', password='Password123!')

        payload = {
            'title': 'Laporan Terupdate Oleh Admin',
            'category': 'Infrastruktur',
            'description': 'Deskripsi terupdate.',
            'location': 'Jakarta',
            'status': 'REPORTED'
        }

        original_title = self.report.title

        response = self.client.post(
            reverse('update_report', kwargs={'pk': self.report.id}),
            payload
        )

        self.assertEqual(response.status_code, 403)

        self.report.refresh_from_db()

        self.assertEqual(self.report.title, original_title)
        self.assertNotEqual(self.report.title, 'Laporan Terupdate Oleh Admin')

    def test_report_delete_view_unauthenticated(self):
        response = self.client.get(
            reverse('delete_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_report_delete_view_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.get(
            reverse('delete_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_report_delete_view_admin_get(self):
        """
        Admin tidak boleh membuka halaman hapus laporan warga.
        """
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.get(
            reverse('delete_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_report_delete_view_admin_post(self):
        """
        Admin tidak boleh menghapus laporan warga.
        """
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.post(
            reverse('delete_report', kwargs={'pk': self.report.id})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Report.objects.filter(id=self.report.id).exists()
        )

    def test_report_delete_view_direct_delete_method(self):
        from main_app.views import ReportDeleteView

        factory = RequestFactory()
        request = factory.post(
            reverse('delete_report', kwargs={'pk': self.report.id})
        )
        request.user = self.admin

        setattr(request, 'session', {})

        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        view = ReportDeleteView()
        view.setup(request, pk=self.report.id)

        with self.assertRaises((PermissionDenied, Http404)):
            view.object = view.get_object()
            view.delete(request)

    def test_report_update_status_view_unauthenticated(self):
        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.report.id}),
            {'status': 'VERIFIED'}
        )

        self.assertEqual(response.status_code, 302)

    def test_report_update_status_view_citizen(self):
        self.client.login(username='citizen_mono', password='Password123!')

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.report.id}),
            {'status': 'VERIFIED'}
        )

        self.assertEqual(response.status_code, 302)

    def test_report_update_status_view_admin_valid(self):
        """
        Admin boleh mengubah status REPORTED menjadi VERIFIED.
        """
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.report.id}),
            {'status': 'VERIFIED'}
        )

        self.assertEqual(response.status_code, 302)

        self.report.refresh_from_db()

        self.assertEqual(self.report.status, 'VERIFIED')

    def test_report_update_status_view_admin_invalid_jump(self):
        """
        Admin tidak boleh lompat status dari REPORTED langsung ke RESOLVED.
        """
        self.client.login(username='admin_mono', password='Password123!')

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.report.id}),
            {'status': 'RESOLVED'}
        )

        self.assertEqual(response.status_code, 302)

        self.report.refresh_from_db()

        self.assertEqual(self.report.status, 'REPORTED')