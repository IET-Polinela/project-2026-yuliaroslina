from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .models import Report
from .forms import ReportForm


def is_admin_user(user):
    return (
        user.is_authenticated
        and getattr(user, 'is_admin', False)
    )


class HomeView(TemplateView):
    template_name = 'main_app/home.html'


class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

    def dispatch(self, request, *args, **kwargs):
        if not is_admin_user(request.user):
            messages.error(request, 'Akses Ditolak. Halaman laporan backend hanya untuk admin.')
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

    def dispatch(self, request, *args, **kwargs):
        if not is_admin_user(request.user):
            messages.error(request, 'Akses Ditolak. Detail laporan backend hanya untuk admin.')
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        messages.error(
            request,
            'Akses ditolak. Penambahan laporan hanya dapat dilakukan melalui Portal Citizen.'
        )
        return redirect('report_list')


class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/update_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Akses Ditolak.')
            return redirect('report_list')

        if not getattr(request.user, 'is_admin', False):
            messages.error(request, 'Akses Ditolak.')
            return redirect('report_list')

        raise PermissionDenied('Admin tidak boleh mengedit isi laporan warga.')

    def form_valid(self, form):
        messages.error(self.request, 'Admin tidak boleh mengedit isi laporan warga.')
        raise PermissionDenied('Admin tidak boleh mengedit isi laporan warga.')


class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Akses Ditolak.')
            return redirect('report_list')

        if not getattr(request.user, 'is_admin', False):
            messages.error(request, 'Akses Ditolak.')
            return redirect('report_list')

        raise PermissionDenied('Admin tidak boleh menghapus laporan warga.')

    def delete(self, request, *args, **kwargs):
        raise PermissionDenied('Admin tidak boleh menghapus laporan warga.')

    def form_valid(self, form):
        raise PermissionDenied('Admin tidak boleh menghapus laporan warga.')


class ReportUpdateStatusView(View):
    def dispatch(self, request, *args, **kwargs):
        if not is_admin_user(request.user):
            messages.error(request, 'Akses Ditolak')
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        if report.status == 'REPORTED' and new_status == 'VERIFIED':
            report.status = 'VERIFIED'
            report.save()
            messages.success(request, 'Status laporan berhasil diubah ke Verified.')

        elif report.status == 'VERIFIED' and new_status == 'IN_PROGRESS':
            report.status = 'IN_PROGRESS'
            report.save()
            messages.success(request, 'Status laporan berhasil diubah ke In Progress.')

        elif report.status == 'IN_PROGRESS' and new_status == 'RESOLVED':
            report.status = 'RESOLVED'
            report.save()
            messages.success(request, 'Status laporan berhasil diubah ke Resolved.')

        else:
            messages.error(request, 'Perubahan status tidak valid.')

        return redirect('report_list')


def report_search_api(request):
    if not is_admin_user(request.user):
        return JsonResponse(
            {'detail': 'Akses ditolak. Fitur pencarian laporan hanya untuk admin.'},
            status=403
        )

    keyword = request.GET.get('q', '').strip()
    normalized_keyword = keyword.replace(' ', '_')

    reports = Report.objects.all().order_by('-created_at')

    if keyword:
        reports = reports.filter(
            Q(title__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(location__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(status__icontains=normalized_keyword)
        )

    data = []

    for report in reports[:50]:
        data.append({
            'id': report.id,
            'title': report.title,
            'category': report.category,
            'location': report.location,
            'status': report.status,
            'status_display': report.get_status_display(),
            'created_at': report.created_at.strftime('%d %B %Y, %H.%M'),
        })

    return JsonResponse({
        'reports': data,
        'results': data,
    })


def report_detail_api(request, pk):
    report = get_object_or_404(Report, pk=pk)

    data = {
        'id': report.id,
        'title': report.title,
        'category': report.category,
        'description': report.description,
        'location': report.location,
        'status': report.status,
        'status_display': report.get_status_display(),
        'created_at': report.created_at.strftime('%d %B %Y, %H.%M'),
    }

    return JsonResponse(data)