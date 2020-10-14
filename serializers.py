import copy
from rest_framework import serializers
from django.db import connections

from gchannel.rpc import RPC



class EnumField(serializers.ChoiceField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        kwargs['choices'] = [(e.name, e.name) for e in enum]
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        try:
            return self.enum[data].name
        except KeyError:
            self.fail('invalid_choice', input=data)


class SlotSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slot_out_of_view = EnumField(enum=OutOfView)
    float_top = serializers.CharField(
        max_length=20, default="initial", help_text="ad Player"
    )
    float_bottom = serializers.CharField(
        max_length=20, default="100px", help_text="ad時 Player"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rpc_client = RPC("db")

    def update(self, instance, validated_data):
        copy_data = copy.deepcopy(validated_data)
        with connections['db'].cursor() as cursor:

            name = copy_data.pop("name", "") or instance.get("name")
            slot_id = instance.get('id')
            # Data processing before entering SQL
            valid_data = []
            for key, value in copy_data.items():
                if type(value) == int:
                    sql_value = str(value)
                elif value is None:
                    sql_value = "Null"
                else:
                    sql_value = f"{value}".join('""')

                valid_data.append(f"{key} = {sql_value}")

            cursor.execute(
                f"""
                UPDATE
                SET
                WHERE
                """
            )
            # update ad slot google cloud
            self.rpc_client.adtag_update_cloudorm(slot_id)

        return validated_data


class SlotGroupSerializer(serializers.Serializer):
    account = serializers.CharField()
    name = serializers.CharField()


class AdTagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True)
    type = serializers.CharField(default="google")
    adTagUrl = serializers.URLField(allow_blank=True, required=False, default=str())
    adTagXml = serializers.CharField(allow_blank=True, default=str())
    priority = serializers.IntegerField(default=0)
    adPlacement = serializers.JSONField(initial="[1]", default="[1]", allow_null=True)
    slot = serializers.CharField(allow_blank=True, default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rpc_client = RPC("db")

    def _get_slot(self, cursor, copy_data):
        # slot name --> slot id
        slot_name = copy_data.pop('slot')
        cursor.execute(f'')
        rows = cursor.fetchall()
        if slot_name and not rows:
            raise
        elif not rows:
            slot_id = None
        else:
            slot_id = rows[0][0]
        copy_data["slot_id"] = slot_id

        return copy_data

    def create(self, validated_data):
        copy_data = copy.deepcopy(validated_data)

        with connections['db'].cursor() as cursor:
            copy_data = self._get_slot(cursor, copy_data)

            # Data processing before entering SQL
            values = []
            for data in copy_data.values():
                if type(data) == int:
                    values.append(str(data))
                elif data is None:
                    values.append("Null")
                else:
                    values.append(f"{data}".join('""'))

            cursor.execute(
                f"""
                INSERT INTO
                VALUES
                """
            )
            # update adtag google cloud
            self.rpc_client.adtag_update_cloudorm(copy_data.get("slot_id"))

        return validated_data

    def update(self, instance, validated_data):
        copy_data = copy.deepcopy(validated_data)
        with connections['db'].cursor() as cursor:

            name = copy_data.pop("name", "") or instance.get("name")

            if "slot" not in copy_data.keys():
                copy_data['slot'] = instance.get("slot")
            else:
                pass
            copy_data = self._get_slot(cursor, copy_data)

            # Data processing before entering SQL
            valid_data = []
            for key, value in copy_data.items():
                if type(value) == int:
                    sql_value = str(value)
                elif value is None:
                    sql_value = "Null"
                else:
                    sql_value = f"{value}".join('""')

                valid_data.append(f"{key} = {sql_value}")

            cursor.execute(
                f"""
                UPDATE
                SET
                WHERE
                """
            )
            # update adtag google cloud
            self.rpc_client.adtag_update_cloudorm(copy_data.get("slot_id"))

        return validated_data