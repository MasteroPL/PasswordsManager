from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User

from .abstract_models import AuditModel
from .generic_models import GenericPassword

class Board(AuditModel):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, blank=False, verbose_name=_("Board_owner"))

    name = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Board_name"))
    description = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("Description"))


class BoardTab(AuditModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Board"), related_name="board_tabs")

    name = models.CharField(max_length=30, null=False, blank=False, verbose_name=_("Board_tab"))
    board_order = models.IntegerField(verbose_name=_("Order_of_the_tab"))
    is_default = models.BooleanField(null=True, blank=True, default=None, 
        choices=(
            (None, "False"),
            (True, "True")
        )
    )


    class Meta:
        unique_together = (
            ('board', 'is_default'),
        )


class BoardPassword(AuditModel):

    id = models.OneToOneField(GenericPassword, on_delete=models.CASCADE, primary_key=True, verbose_name=_("Generic_password_id"), related_name="board_password")

    board = models.ForeignKey(Board, on_delete=models.RESTRICT, verbose_name=_("Board"))
    board_tab = models.ForeignKey(BoardTab, on_delete=models.RESTRICT, verbose_name=_("Board_tab"))


class BoardUserAssignment(AuditModel):

    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Board"), related_name="user_assignments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User"))

    perm_admin = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("Admin_permission"))
    perm_create = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("Create_permission"))
    perm_read = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("Read_permission"))
    perm_update = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("Update_permission"))
    perm_delete = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("Delete_permission"))

    class Meta:
        unique_together = (
            ("board", "user"),
        )
