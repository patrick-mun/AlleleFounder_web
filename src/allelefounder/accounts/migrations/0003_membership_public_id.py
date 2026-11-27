import uuid

from django.db import migrations, models


def populate_membership_public_ids(apps, schema_editor) -> None:
    membership_model = apps.get_model("accounts", "Membership")
    memberships = membership_model.objects.filter(public_id__isnull=True).iterator()
    for membership in memberships:
        membership.public_id = uuid.uuid4()
        membership.save(update_fields=("public_id",))


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_organizations_and_access")]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="public_id",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(populate_membership_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="membership",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
