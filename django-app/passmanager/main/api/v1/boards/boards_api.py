from django.db.models.expressions import Case, Value, When
from django.db.models.query_utils import Q
from django.http.response import Http404
from main.models import Board
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import serializers, status, generics
from main.commons import serialization_errors_to_response
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError as CoreValidationError
from django.db import transaction

from main.models.board_passwords_models import BoardTab, BoardUserAssignment
from main.utils.board_tabs_builder import (
    BoardTabsBuilder,
    BoardTabNotFoundError,
    CannotDeleteDefaultTabError
)

from .boards_serializers import (
    BoardsAPIGetRequestSerializer,
    BoardsAPIGetResponseSerializer,
    BoardsAPIPostRequestSerializer,
    BoardsAPIPostResponseSerializer,
    BoardAPIGetRequestSerializer,
    BoardAPIGetResponseSerializer,
    BoardAPIPatchRequestSerializer,
    BoardAPIPatchResponseSerializer,
    BoardAssignmentsAPIGetRequestSerializer,
    BoardAssignmentsAPIGetResponseSerializer,
    BoardAssignmentsAPIPostRequestSerializer,
    BoardAssignmentsAPIPostResponseSerializer,
    BoardAssignmentAPIGetResponseSerializer,
    BoardAssignmentAPIPatchRequestSerializer,
    BoardAssignmentAPIPatchResponseSerializer,
    BoardTabsAPIGetResponseSerializer,
    BoardTabsAPIPostRequestSerializer,
    BoardTabAPIPatchRequestSerializer
)

# ------------------
# Generic Board APIs
# ------------------

class BoardsAPI(GenericAPIView):

    def get_queryset(self):
        qs = Board.objects.filter(
            Q(owner=self.request.user)
            |Q(user_assignments__user=self.request.user)
        ).distinct().order_by("id")

        return qs

    def filter_queryset(self, qs, data:BoardsAPIGetRequestSerializer):
        if data.validated_data["search_text"] is not None:
            qs = qs.annotate(
                full_text_search=Concat('name', V(' '), 'description')
            ).filter(full_text_search__icontains=data.validated_data["search_text"])
            return qs

        return qs

    def get(self, request):
        
        serializer = BoardsAPIGetRequestSerializer(data=request.query_params)

        if serializer.is_valid():
            qs = self.get_queryset().annotate(
                is_owner=Case(
                    When(owner_id=request.user.id, then=Value(True)),
                    default=Value(False)
                )
            )
            qs = self.filter_queryset(qs, serializer)
            total_pages = 1

            if serializer.validated_data["per_page"] != -1:
                p = Paginator(qs, serializer.validated_data["per_page"])
                page = serializer.validated_data["page"]

                if page > p.num_pages:
                    qs = []
                else:
                    qs = p.page(page)

                total_pages = p.num_pages

            response = BoardsAPIGetResponseSerializer(instance={
                "per_page": serializer.validated_data["per_page"],
                "page": serializer.validated_data["page"],
                "items": qs,
                "total_pages": total_pages
            })

            return Response(data=response.data, status=status.HTTP_200_OK)


        errors = serialization_errors_to_response(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        
        serializer = BoardsAPIPostRequestSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            board_data = {
                "name": data["name"]
            }
            if data.__contains__("description"):
                board_data["description"] = data["description"]

            owner = request.user
            obj = Board(
                **board_data,
                owner=owner
            )
            default_tab = BoardTab(
                board=obj,
                name=data["default_tab_name"] if data["default_tab_name"] is not None else "Default tab",
                board_order=1
            )

            try:
                with transaction.atomic():
                    obj.save()
                    default_tab.save()
            except CoreValidationError as e:
                errors = serialization_errors_to_response(e.error_dict)
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(data={
                    "message": "An unknown internal server error occured, please try again later"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            resp_data = {
                "id": obj.id,
                "name": obj.name,
                "description": obj.description,
                "default_tab_name": default_tab.name
            }
            response = BoardsAPIPostResponseSerializer(instance=resp_data)
            return Response(data=response.data, status=status.HTTP_201_CREATED)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)



class BoardAPI(GenericAPIView):

    def get_queryset(self, admin_required=False):
        qs1 = Board.objects.filter(
            Q(owner=self.request.user)
            |Q(user_assignments__user=self.request.user)
        ).distinct()

        if not admin_required:
            return qs1, None

        else:
            qs2 = Board.objects.filter(
                Q(owner=self.request.user)
                |Q(
                    user_assignments__user=self.request.user,
                    user_assignments__perm_admin=True
                )
            ).distinct()

            return qs1, qs2

    def get(self, request, board_id:int):

        serializer = BoardAPIGetRequestSerializer(data=request.query_params)

        if serializer.is_valid():
            select_related_arr = []
            prefetch_related_arr = []
            serializer_fields = [
                "id",
                "name",
                "description"
            ]
            data = serializer.validated_data
            admin_required = False

            if data["include_owner"]:
                select_related_arr.append("owner")
                serializer_fields.append("owner")
                admin_required = True
            if data["include_users"]:
                prefetch_related_arr.append("user_assignments")
                prefetch_related_arr.append("user_assignments__user")
                serializer_fields.append("users")
                admin_required=True
            if data["include_tabs"]:
                prefetch_related_arr.append("board_tabs")
                serializer_fields.append("tabs")
            

            qs_no_admin, qs_admin = self.get_queryset(admin_required=admin_required)

            exists = False

            try:
                if not admin_required:
                    qs = qs_no_admin
                else:
                    qs = qs_admin
                    exists = qs_no_admin.filter(id=board_id).exists()

                obj = qs \
                    .select_related(*select_related_arr) \
                    .prefetch_related(*prefetch_related_arr) \
                    .get(id=board_id) \

            except Board.DoesNotExist:
                if exists:
                    return Response(status=status.HTTP_403_FORBIDDEN)

                raise Http404()

            response = BoardAPIGetResponseSerializer(instance=obj, fields=serializer_fields)

            return Response(data=response.data, status=status.HTTP_200_OK)


        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, board_id:int):
        serializer = BoardAPIPatchRequestSerializer(data=request.data, partial=True)

        qs_no_admin, qs_admin = self.get_queryset(admin_required=True)

        exists = qs_no_admin.filter(id=board_id).exists()
        obj = None
        try:
            obj = qs_admin.get(id=board_id)
        except Board.DoesNotExist:
            if not exists:
                raise Http404()

            return Response(status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            data = serializer.validated_data
            if len(data) == 0:
                return Response(data={
                    "detail": "Nothing to update",
                    "code": "empty_request"
                }, status=status.HTTP_400_BAD_REQUEST)

            changed_owner = False

            if data.__contains__("owner_id"):
                if obj.owner != request.user:
                    return Response(status=status.HTTP_403_FORBIDDEN)

                data["owner"] = data["owner_id"]
                data.pop("owner_id")

                if obj.owner_id != data["owner"].id:
                    changed_owner = True
                else:
                    data.pop("owner")


            for key, value in data.items():
                setattr(obj, key, value)

            try:
                with transaction.atomic():
                    if changed_owner:
                        old_owner_assignment = BoardUserAssignment(
                            board_id=board_id,
                            user=self.request.user,
                            perm_admin=True,
                            perm_create=True,
                            perm_read=True,
                            perm_update=True,
                            perm_delete=True
                        )
                        BoardUserAssignment.objects.filter(
                            board_id=board_id,
                            user_id=data["owner"].id
                        ).delete()
                        old_owner_assignment.save()

                    obj.save()
            except CoreValidationError as error:
                errors = serialization_errors_to_response(serializer.errors)
                return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

            response = BoardAPIPatchResponseSerializer(instance=obj)

            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, board_id:int):

        qs, tmp = self.get_queryset()

        try:
            obj = qs.select_related("owner").get(id=board_id)
        except Board.DoesNotExist:
            raise Http404()

        if obj.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



#
# Assigning users to board
#

class BoardAssignmentsAPI(GenericAPIView):

    def get_queryset(self, board_id:int):
        qs = BoardUserAssignment.objects.filter(board_id=board_id)
        return qs

    def get_object(self, board_id:int):
        return Board.objects.get(
            Q(owner=self.request.user)
            |Q(
                user_assignments__user=self.request.user,
                user_assignments__perm_admin=True
            ),
            id=board_id
        )

    def object_exists(self, board_id:int):
        exists = Board.objects.filter(
            Q(owner=self.request.user)
            |Q(user_assignments__user=self.request.user),
            id=board_id
        ).exists()

        return exists

    def assignment_exists(self, board_id:int, user_id:int):
        return BoardUserAssignment.objects.filter(
            board_id=board_id,
            user_id=user_id
        ).exists()


    def get(self, request, board_id:int):
        
        obj = None
        exists = self.object_exists(board_id)
        try:
            obj = self.get_object(board_id)
        except Board.DoesNotExist:
            if not exists:
                raise Http404()
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardAssignmentsAPIGetRequestSerializer(data=request.query_params)

        if serializer.is_valid():
            data = serializer.validated_data
            qs = self.get_queryset(board_id).prefetch_related("user")
            total_pages = 1

            if data["per_page"] != -1:
                p = Paginator(qs, per_page=data["per_page"])

                if data["page"] > p.num_pages:
                    qs = []
                else:
                    qs = p.page(data["page"])

                total_pages = p.num_pages

            response = BoardAssignmentsAPIGetResponseSerializer(instance={
                "per_page": data["per_page"],
                "page": data["page"],
                "total_pages": total_pages,
                "items": qs
            })
            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    
    def post(self, request, board_id:int):
        exists = self.object_exists(board_id)
        obj = None
        try:
            obj = self.get_object(board_id)
        except Board.DoesNotExist:
            if not exists:
                raise Http404()
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardAssignmentsAPIPostRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            if data["user"].id == obj.owner.id or self.assignment_exists(board_id, data["user"].id):
                return Response(data={
                    "user_id": {
                        "string": "User is already assigned to this board",
                        "code": "exists"
                    }
                }, status=status.HTTP_409_CONFLICT)

            if data.__contains__("perm_admin") and data["perm_admin"] and obj.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            new_obj = BoardUserAssignment(
                board=obj,
                **data
            )
            try:
                new_obj.save()
            except CoreValidationError as e:
                errors = serialization_errors_to_response(e.error_dict)
                return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(data={
                    "detail": "An unrecognized internal server error has occured",
                    "code": "internal_server_error"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            response = BoardAssignmentsAPIPostResponseSerializer(instance=new_obj)
            return Response(data=response.data, status=status.HTTP_201_CREATED)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)



class BoardAssignmentAPI(GenericAPIView):

    def get_object(self, board_id:int, assignment_id:int, readonly:bool=False):
        owner_qs = Board.objects.filter(id=board_id, owner=self.request.user)
        assigned_admin_qs = Board.objects.filter(
            id=board_id,
            user_assignments__user=self.request.user,
            user_assignments__perm_admin=True
        ).distinct()

        if not readonly:
            return BoardUserAssignment.objects.select_related("board", "user").get(
                Q(board__in=owner_qs)
                |Q(
                    perm_admin=False,
                    board__in=assigned_admin_qs
                ),
                id=assignment_id
            )
        else:
            return BoardUserAssignment.objects.select_related("board", "user").get(
                Q(board__in=owner_qs)
                |Q(board__in=assigned_admin_qs),
                id=assignment_id
            )

    def object_exists(self, board_id:int, assignment_id:int):
        owner_qs = Board.objects.filter(id=board_id, owner=self.request.user)
        assigned_qs = Board.objects.filter(
            id=board_id,
            user_assignments__user=self.request.user
        )
        exists = BoardUserAssignment.objects.filter(
            Q(board__in=owner_qs)
            |Q(board__in=assigned_qs),
            id=assignment_id
        ).exists()

        return exists

    def verify_permissions(self, board_id:int):
        board_exists = Board.objects.filter(id=board_id).exists()

        exists1 = Board.objects.filter(id=board_id, owner=self.request.user).exists()
        exists2 = Board.objects.filter(
            id=board_id,
            user_assignments__user=self.request.user,
            user_assignments__perm_admin=True
        ).exists()
        exists3 = Board.objects.filter(
            id=board_id,
            user_assignments__user=self.request.user
        ).exists()

        if not board_exists:
            raise Http404()

        access = exists1 or exists2
        if not access and not exists3:
            raise Http404()

        return access


    def get(self, request, board_id:int, assignment_id:int):
        if not self.verify_permissions(board_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        exists = self.object_exists(board_id, assignment_id)

        obj = None
        try:
            obj = self.get_object(board_id, assignment_id, readonly=True)
        except BoardUserAssignment.DoesNotExist:
            if not exists:
                raise Http404()
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = BoardAssignmentAPIGetResponseSerializer(instance=obj)
        return Response(data=response.data, status=status.HTTP_200_OK)

    
    def patch(self, request, board_id:int, assignment_id:int):
        if not self.verify_permissions(board_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        exists = self.object_exists(board_id, assignment_id)
        obj = None
        try:
            obj = self.get_object(board_id, assignment_id)
        except BoardUserAssignment.DoesNotExist:
            if not exists:
                raise Http404()
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardAssignmentAPIPatchRequestSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            data = serializer.validated_data

            if data.__contains__("perm_admin") \
                and obj.board.owner_id != request.user.id:

                return Response(status=status.HTTP_403_FORBIDDEN)

            # Preventing dumb users from modifying their own assignments
            # In theory this is not possible with current code (admins cannot modify other admins), buuuuut just to be sure I'm gonna leave it here
            if obj.user_id == request.user.id:
                return Response(data={
                    "detail": "Attempted to modify your own assignment.",
                    "code": "own_assignment"
                }, status=status.HTTP_400_BAD_REQUEST)

            for key, value in data.items():
                setattr(obj, key, value)

            try:
                obj.save()
            except CoreValidationError as e:
                errors = serialization_errors_to_response(e.error_dict)
                return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(data={
                    "detail": "An unknown internal server error occured",
                    "code": "internal_server_error"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            response = BoardAssignmentAPIPatchResponseSerializer(instance=obj)
            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, board_id:int, assignment_id:int):
        if not self.verify_permissions(board_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        exists = self.object_exists(board_id, assignment_id)

        obj = None
        try:
            obj = self.get_object(board_id, assignment_id)
        except BoardUserAssignment.DoesNotExist:
            if not exists:
                raise Http404()
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Preventing dumb users from deleting their own assignments
        # In theory this is not possible with current code (admins cannot remove admins), buuuuut just to be sure I'm gonna leave it here
        if obj.user_id == request.user.id:
            return Response(data={
                "detail": "Attempted to delete your own assignment. If you wish to leave the board, use a different endpoint designed specifically for that purpose.",
                "code": "own_assignment"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj.delete()
        except Exception as e:
            return Response(data={
                "detail": "An unknown internal server error occured",
                "code": "internal_server_error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)




#
# Managing tabs
#

class BoardTabsAPI(GenericAPIView):
    
    def verify_permissions(self, board_id:int, readonly=False):
        board_exists = Board.objects.filter(id=board_id).exists()

        exists1 = Board.objects.filter(id=board_id, owner=self.request.user).exists()
        exists3 = Board.objects.filter(
            id=board_id,
            user_assignments__user=self.request.user
        ).exists()
        if not readonly:
            exists2 = Board.objects.filter(
                id=board_id,
                user_assignments__user=self.request.user,
                user_assignments__perm_admin=True
            ).exists()
        else:
            exists2 = exists3

        if not board_exists:
            raise Http404()

        access = exists1 or exists2
        if not access and not exists3:
            raise Http404()

        return access

    def get(self, request, board_id:int, format=None):
        access = self.verify_permissions(board_id, readonly=True)

        if not access:
            return Response(status=status.HTTP_403_FORBIDDEN)

        qs = BoardTab.objects.filter(
            board_id=board_id
        ).order_by("board_order")
        response = BoardTabsAPIGetResponseSerializer(instance=qs, many=True)

        return Response(data=response.data, status=status.HTTP_200_OK)

    def post(self, request, board_id:int, format=None):
        access = self.verify_permissions(board_id)

        if not access:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardTabsAPIPostRequestSerializer(board_id, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            builder = BoardTabsBuilder(board_id)
            if data["add_after"] is not None:
                try:
                    builder.insert_tab_after_id(data["name"], data["add_after"], False)
                except BoardTabNotFoundError:
                    return Response(data={
                        "add_after": {
                            "string": "Tab ID not found",
                            "code": "tab_not_found"
                        }
                    })
            else:
                builder.append_tab(data["name"])
            builder.save()

            objects = BoardTab.objects.filter(board_id=board_id).order_by("board_order")
            response = BoardTabsAPIGetResponseSerializer(instance = objects, many=True)
            return Response(data=response.data, status=status.HTTP_201_CREATED)


        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)



class BoardTabAPI(GenericAPIView):

    def verify_permissions(self, board_id:int, readonly=False):
        board_exists = Board.objects.filter(id=board_id).exists()

        exists1 = Board.objects.filter(id=board_id, owner=self.request.user).exists()
        exists3 = Board.objects.filter(
            id=board_id,
            user_assignments__user=self.request.user
        ).exists()
        if not readonly:
            exists2 = Board.objects.filter(
                id=board_id,
                user_assignments__user=self.request.user,
                user_assignments__perm_admin=True
            ).exists()
        else:
            exists2 = exists3

        if not board_exists:
            raise Http404()

        access = exists1 or exists2
        if not access and not exists3:
            raise Http404()

        return access


    def get(self, request, board_id:int, tab_id:int, format=None):
        if not self.verify_permissions(board_id, readonly=True):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            obj = BoardTab.objects.get(
                id=tab_id,
                board_id=board_id
            )
        except BoardTab.DoesNotExist:
            raise Http404()

        response = BoardTabsAPIGetResponseSerializer(instance=obj)
        return Response(data=response.data, status=status.HTTP_200_OK)


    def patch(self, request, board_id:int, tab_id:int, format=None):
        if not self.verify_permissions(board_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardTabAPIPatchRequestSerializer(board_id, data=request.data, partial=True)

        if serializer.is_valid():
            builder = BoardTabsBuilder(board_id)
            try:
                obj = builder.get_tab(tab_id)
            except BoardTabNotFoundError:
                raise Http404()
            
            data = serializer.validated_data
            if data.__contains__("name"):
                obj.name = data["name"]
            if data.__contains__("put_after"):
                try:
                    builder.change_tab_order(tab_id, data["put_after"])
                except BoardTabNotFoundError:
                    return Response(data={
                        "put_after": {
                            "string": "Requested tab id has not been found",
                            "code": "tab_not_found"
                        }
                    })

            builder.save()

            tabs = BoardTab.objects.filter(board_id=board_id).order_by("board_order")

            response = BoardTabsAPIGetResponseSerializer(instance=tabs, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)
            

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, board_id:int, tab_id:int, format=None):
        if not self.verify_permissions(board_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        builder = BoardTabsBuilder(board_id)
        try:
            builder.delete_tab(tab_id)
        except BoardTabNotFoundError:
            raise Http404()
        except CannotDeleteDefaultTabError:
            return Response({
                "detail": "Cannot delete default tab",
                "code": "cannot_delete_default"
            })

        builder.save()

        response = BoardTabsAPIGetResponseSerializer(instance=builder.tabs, many=True)
        return Response(data=response.data, status=status.HTTP_204_NO_CONTENT)