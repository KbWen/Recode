import re

from django.db import connections
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from report.models import Channel

from user.models import User
from .serializers import AdTagSerializer, SlotGroupSerializer, SlotSerializer


class SlotGroupViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = SlotGroupSerializer

    def list(self, request):
        # user can only be found there slot
        where_condition = ""
        if not request.user.is_superuser:
            user = User.objects.get(username=request.user.username)
            channels = Channel.objects.filter(users=user)
            channel = "','".join([c.name for c in channels])

            where_condition = f"sql{channel}"

        with connections['db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                FROM 
                INNER JOIN  ON account_id=id
                {where_condition}
                """
            )
            rows = cursor.fetchall()

        # Fixme
        keys = self.serializer_class().fields.keys()
        serializer = self.serializer_class(
            instance=[dict(zip(keys, row)) for row in rows], many=True)
        return Response(serializer.data)


class SlotViewSet(
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = SlotSerializer
    lookup_field = 'name'

    def get_instance(self, name):
        with connections['db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                FROM 
                WHERE name='{name}'
                """
            )
            rows = cursor.fetchall()
        keys = SlotSerializer().fields.keys()
        instance = dict(zip(keys, rows[0]))
        return instance

    def get_queryset(self):
        pass

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)

        name = kwargs.get('name') or request.data.get("name")
        instance = self.get_instance(name)
        request_data = request.data.copy()
        slot_out_of_view = request_data.get("slot", "").upper()
        request_data.update({
            "name": f"{name}",
            "slot_out_of_view": slot_out_of_view or instance.get("slot_out_of_view")
        })

        if not request.user.is_superuser and request.user.username not in name:
            return Response(
                data={'error': f'{name} is not a correct slot name', },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def list(self, request):
        username = str()
        # user can only be found there slot
        # username in slot name
        if not request.user.is_superuser:
            username = request.user.username

        with connections['db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                FROM 
                WHERE LIKE 
                """
            )
            rows = cursor.fetchall()

        # Fixme
        keys = self.serializer_class().fields.keys()
        serializer = self.serializer_class(
            instance=[dict(zip(keys, row)) for row in rows], many=True)
        return Response(serializer.data)

    def retrieve(self, request, **kwargs):
        name = kwargs[self.lookup_field]
        name = kwargs[self.lookup_field] = re.sub("--+", "-", name.replace('"', '&#34;'))

        if not request.user.is_superuser and request.user.username not in name:
            return Response(
                data={'error': f'{name} is not a correct slot name', },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.serializer_class(
            instance=self.get_instance(name))
        return Response(serializer.data)


class AdTagViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = AdTagSerializer
    lookup_field = 'name'

    def get_instance(self, name):
        with connections['db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                FROM 
                LEFT JOIN ON slot_id=id
                WHERE
                """
            )
            rows = cursor.fetchall()
        keys = AdTagSerializer().fields.keys()
        instance = dict(zip(keys, rows[0]))
        return instance

    def get_queryset(self):
        pass

    def check_instance_permissions(self, request, data=None):
        if not request.user.is_superuser:
            user = request.user.username
            name = data.get("name") if data else request.data.get("name", "")
            slot = request.data.get("slot", "")
            if user not in name or (slot and slot not in self._get_user_slot(user)):
                return False
        return True

    def _get_user_slot(self, username):
        user = User.objects.get(username=username)

        channels = Channel.objects.filter(users=user)
        channel = "','".join([c.name for c in channels])

        where_condition = f"{channel}"
        with connections['db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                FROM
                INNER JOIN ON
                {where_condition}
                """
            )
            rows = cursor.fetchall()
        return [row[0] for row in rows]

    def create(self, request, *args, **kwargs):
        if not self.check_instance_permissions(request):
            return Response(
                data={'error': f'{request.user.username} has to be in the name and correct slot.(if slot exist)', },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # fixme request data name
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)

        name = kwargs.get('name') or request.data.get("name")
        instance = self.get_instance(name)
        request_data = request.data.copy()
        request_data.update({"name": f"{name}"})

        if not self.check_instance_permissions(request, request_data):
            return Response(
                data={'error': f'{request.user.username} has to be in name and correct slot.(if slot exist)', },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def list(self, request):
        username = str()
        if not request.user.is_superuser:
            username = request.user.username

        with connections['db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                FROM
                LEFT JOIN ON
                WHERE
                """
            )
            rows = cursor.fetchall()

        # Fixme
        keys = self.serializer_class().fields.keys()
        serializer = self.serializer_class(
            instance=[dict(zip(keys, row)) for row in rows], many=True)
        return Response(serializer.data)

    def retrieve(self, request, **kwargs):
        name = kwargs[self.lookup_field]
        name = kwargs[self.lookup_field] = re.sub("--+", "-", name.replace('"', '&#34;'))

        if not request.user.is_superuser and request.user.username not in name:
            return Response(
                data={'error': f'{name} is not a correct adtag name', },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.serializer_class(
            instance=self.get_instance(name))
        return Response(serializer.data)
