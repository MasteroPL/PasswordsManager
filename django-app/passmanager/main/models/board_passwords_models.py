from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User

from .abstract_models import AuditModel
from .generic_models import GenericPassword
import os

class Board(AuditModel):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, blank=False, verbose_name=_("Board_owner"))

    name = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Board_name"))
    description = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("Description"))

    @staticmethod
    def get_board_user_permissions(board_id:int, user_id:int):
        owner = Board.objects.filter(id=board_id, owner_id=user_id).exists()
        assignment = BoardUserAssignment.objects.filter(
            board_id=board_id, 
            user_id=user_id
        )

        if owner:
            return {
                "create": True,
                "read": True,
                "update": True,
                "delete": True
            }

        if len(assignment) == 0:
            raise BoardUserAssignment.DoesNotExist()

        if assignment.perm_admin:
            return {
                "create": True,
                "read": True,
                "update": True,
                "delete": True
            }

        return {
            "create": assignment.perm_create,
            "read": assignment.perm_read,
            "update": assignment.perm_update,
            "delete": assignment.perm_delete
        }


    def get_user_permissions(self, user:User):
        if self.owner.id == user.id:
            return {
                "create": True,
                "read": True,
                "update": True,
                "delete": True
            }

        assignment = BoardUserAssignment.objects.get(
            board=self,
            user=user
        )

        if assignment.perm_admin:
            return {
                "create": True,
                "read": True,
                "update": True,
                "delete": True
            }

        return {
            "create": assignment.perm_create,
            "read": assignment.perm_read,
            "update": assignment.perm_update,
            "delete": assignment.perm_delete
        }


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

    password = models.OneToOneField(GenericPassword, on_delete=models.CASCADE, primary_key=True, verbose_name=_("Generic_password_id"), related_name="board_password")

    board = models.ForeignKey(Board, on_delete=models.RESTRICT, verbose_name=_("Board"))
    board_tab = models.ForeignKey(BoardTab, on_delete=models.RESTRICT, verbose_name=_("Board_tab"), related_name="tab_passwords")

    @staticmethod
    def create(
        board_id:int, board_tab_id:int,
        password:str, title:str, 
        description:str=None, url:str=None,
        username:str=None,
        commit:bool=True
    ):
        target_file = None
        try:
            with transaction.atomic():
                generic_password, target_file = GenericPassword.create(
                    password,
                    title,
                    description=description,
                    url=url,
                    username=username,
                    commit=False
                )

                board_password = BoardPassword(
                    password=generic_password,
                    board_id=board_id,
                    board_tab_id=board_tab_id
                )

                if commit:
                    generic_password.save()
                    board_password.save()

                return board_password, generic_password

        except Exception as e:
            if target_file is not None:
                os.remove(target_file)

            raise e


    def remove(self):
        with transaction.atomic():
            password = self.password

            self.delete()

            password.remove()




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
