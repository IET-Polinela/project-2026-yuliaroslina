from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.StringRelatedField(read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'title',
            'category',
            'description',
            'location',
            'status',
            'reporter',
            'is_owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'reporter',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        return obj.reporter == request.user