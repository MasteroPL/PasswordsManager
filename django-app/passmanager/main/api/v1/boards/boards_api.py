from django.contrib.auth.models import User
from django.db.models.expressions import Case, Value, When
from django.db.models.query import Prefetch
from django.db.models.query_utils import Q
from django.http.response import Http404
from main.models import Board
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from main.commons import serialization_errors_to_response
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError as CoreValidationError
from django.db import transaction

from main.models.board_passwords_models import BoardPassword, BoardTab, BoardUserAssignment
from main.models.generic_models import GenericPassword
from main.utils.board_tabs_builder import (
    BoardTabsBuilder,
    BoardTabNotFoundError,
    CannotDeleteDefaultTabError
)

from .boards_serializers import (
    BoardAssignmentsUsersSearchAPIGetResponseSerializer,
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
    BoardTabAPIPatchRequestSerializer,
    BoardAssignmentsUsersSearchAPIGetRequestSerializer,
    BoardPasswordsAPIPostRequestSerializer,
    BoardPasswordAPIResponseSerializer,
    BoardTabAPIDeleteRequestSerializer,
    BoardPasswordsAPIPatchRequestSerializer
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
                ),
                # This one is modified later, to avoid too complex queries
                # By default, if user is the owner, they are also an admin
                # (Also Django really doesn't work too well with queries that are too complex)
                is_admin=Case(
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
                    qs = Board.objects.none()
                else:
                    qs = p.page(page)

                total_pages = p.num_pages

            ids = qs.values_list('id', flat=True)
            is_admin_qs = BoardUserAssignment.objects.filter(
                board_id__in=ids,
                user_id=request.user.id,
                perm_admin=True
            ).order_by('board_id')

            board_index = 0
            board_id = None
            
            qs = list(qs) # Fetching everything from DB at this line
            for item in is_admin_qs:
                board_id = qs[board_index].id

                while(item.board_id > board_id):
                    board_index += 1
                    board_id = qs[board_index].id
                    
                # If anyhow duplicates appear, they will be omitted by this if
                if item.board_id == board_id:
                    setattr(qs[board_index], "is_admin", True)
                    board_index += 1

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
                board_order=1,
                is_default=True
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
                "description",
                "permissions"
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
                # Cool prefetch
                prefetch_related_arr.append(
                    Prefetch(
                        "board_tabs",
                        queryset=BoardTab.objects.order_by("board_id", "board_order")
                    )
                )
                serializer_fields.append("tabs")
                serializer_fields.append(
                    Prefetch(
                        "tabs__tab_passwords",
                        queryset=BoardPassword.objects.order_by("password__title")
                    )
                )
            

            qs_no_admin, qs_admin = self.get_queryset(admin_required=True)

            is_admin = False

            try:
                if admin_required:
                    is_admin = qs_admin.filter(id=board_id).exists()
                    obj = qs_no_admin.select_related(*select_related_arr) \
                        .prefetch_related(*prefetch_related_arr) \
                        .get(id=board_id) 

                    if not is_admin:
                        serializer_fields.remove("owner")
                        serializer_fields.remove("users")

                else:
                    obj = qs_no_admin.select_related(*select_related_arr) \
                        .prefetch_related(*prefetch_related_arr) \
                        .get(id=board_id) 

            except Board.DoesNotExist:
                raise Http404()

            if obj.owner_id != request.user.id:
                assignment = BoardUserAssignment.objects.get(board_id=board_id, user_id=request.user.id)
                setattr(obj, 'permissions', {
                    "admin": assignment.perm_admin,
                    "create": assignment.perm_admin or assignment.perm_create,
                    "read": assignment.perm_admin or assignment.perm_read,
                    "update": assignment.perm_admin or assignment.perm_update,
                    "delete": assignment.perm_admin or assignment.perm_delete
                })
            else:
                setattr(obj, 'permissions', {
                    "admin": True,
                    "create": True,
                    "read": True,
                    "update": True,
                    "delete": True
                })

            response = BoardAPIGetResponseSerializer(instance=obj, fields=serializer_fields)

            return Response(data=response.data, status=status.HTTP_200_OK)


        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, board_id:int):
        serializer = BoardAPIPatchRequestSerializer(board_id, data=request.data, partial=True)

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


class BoardAssignmentsUsersSearchAPI(GenericAPIView):
    
    def get_queryset(self, board:Board):
        owner_id = board.owner_id
        assigned_ids = BoardUserAssignment.objects.filter(board_id=board.id).values_list("user_id", flat=True)

        qs = User.objects.all().exclude(
            Q(id=owner_id)|Q(id__in=assigned_ids)
        ).annotate(
            search_value=Concat(
                "username",
                Value(" ("),
                "last_name",
                Value(" "),
                "first_name",
                Value(")")
            )
        )

        return qs


    def get(self, request, board_id:int, format=None):
        obj = None
        try:
            obj = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise Http404()

        serializer = BoardAssignmentsUsersSearchAPIGetRequestSerializer(data=request.query_params)

        if serializer.is_valid():
            data = serializer.validated_data
            qs = self.get_queryset(obj).filter(
                search_value__icontains=data["search_text"]
            ).order_by("search_value")[:10]

            response = BoardAssignmentsUsersSearchAPIGetResponseSerializer(instance=qs, many=True)

            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class BoardLeaveAPI(GenericAPIView):

    def get_queryset(self, board_id:int):
        qs = Board.objects.filter(
            Q(owner=self.request.user)
            |Q(user_assignments__user=self.request.user),
            id=board_id
        ).distinct()

        return qs

    def delete(self, request, board_id:int, format=None):

        qs = self.get_queryset(board_id)
        exists = qs.exists()
        obj = qs[0]

        if not exists:
            raise Http404()

        if obj.owner_id == request.user.id:
            return Response(data={
                "detail": "You cannot leave a board you are the owner of. Either change the boards owner or delete the board entirely.",
                "code": "is_owner"
            }, status=status.HTTP_400_BAD_REQUEST)

        BoardUserAssignment.objects.filter(
            board_id=board_id,
            user_id=request.user.id
        ).delete()

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
        ).prefetch_related(
            Prefetch(
                "tab_passwords",
                queryset=BoardPassword.objects.order_by("password__title")
            )
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
                builder.prepend_tab(data["name"])
            builder.save()

            objects = BoardTab.objects.filter(board_id=board_id).prefetch_related(
                Prefetch(
                    "tab_passwords",
                    queryset=BoardPassword.objects.order_by("password__title")
                )
            ).order_by("board_order")

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
            ).prefetch_related(
                Prefetch(
                    "tab_passwords",
                    queryset=BoardPassword.objects.order_by("password__title")
                )
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

            tabs = BoardTab.objects.filter(board_id=board_id).prefetch_related(
                Prefetch(
                    "tab_passwords",
                    queryset=BoardPassword.objects.order_by("password__title")
                )
            ).order_by("board_order")

            response = BoardTabsAPIGetResponseSerializer(instance=tabs, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)
            

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, board_id:int, tab_id:int, format=None):
        if not self.verify_permissions(board_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardTabAPIDeleteRequestSerializer(board_id, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            builder = BoardTabsBuilder(board_id)
            try:
                builder.delete_tab(tab_id, delete_passwords=data["remove_passwords"], move_to_tab=data["move_passwords_to_tab_id"])
            except BoardTabNotFoundError:
                raise Http404()
            except CannotDeleteDefaultTabError:
                return Response({
                    "detail": "Cannot delete default tab",
                    "code": "cannot_delete_default"
                })

            builder.save()

            tabs = BoardTab.objects.filter(board_id=board_id).prefetch_related(
                Prefetch(
                    "tab_passwords",
                    queryset=BoardPassword.objects.order_by("password__title")
                )
            ).order_by("board_order")
            response = BoardTabsAPIGetResponseSerializer(instance=tabs, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


#
# Board passwords
#

class BoardPasswordsAPI(GenericAPIView):

    def post(self, request, board_id:int, format=None):
        
        board = None
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist():
            raise Http404()

        try:
            permissions = board.get_user_permissions(request.user)
        except BoardUserAssignment.DoesNotExist:
            raise Http404()

        if not permissions["create"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardPasswordsAPIPostRequestSerializer(board.id, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            board_password, generic_password = BoardPassword.create(
                board.id,
                board_tab_id=data["board_tab_id"],
                password=data["password"],
                title=data["title"],
                description=data["description"],
                url=data["url"],
                username=data["username"]
            )

            response = BoardPasswordAPIResponseSerializer(instance=board_password)
            return Response(data=response.data, status=status.HTTP_201_CREATED)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    
class BoardPasswordAPI(GenericAPIView):

    def get(self, request, board_id:int, password_code:str, format=None):
        try:
            Board.get_board_user_permissions(board_id, request.user.id)
        except BoardUserAssignment.DoesNotExist:
            raise Http404()
        
        try:
            obj = BoardPassword.objects.select_related("password").get(
                board_id=board_id,
                password__code=password_code
            )
        except BoardPassword.DoesNotExist:
            raise Http404()

        response = BoardPasswordAPIResponseSerializer(instance=obj)
        return Response(data=response.data, status=status.HTTP_200_OK)


    def patch(self, request, board_id:int, password_code:str, format=None):
        try:
            permissions = Board.get_board_user_permissions(board_id, request.user.id)
        except BoardUserAssignment.DoesNotExist:
            raise Http404()
        
        try:
            obj = BoardPassword.objects.select_related("password").get(
                board_id=board_id,
                password__code=password_code
            )
        except BoardPassword.DoesNotExist:
            raise Http404()

        if not permissions["update"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = BoardPasswordsAPIPatchRequestSerializer(board_id, data=request.data, partial=True)
        if serializer.is_valid():
            data = serializer.validated_data

            password_obj = obj.password

            new_password_provided = False
            new_password = None
            if data.__contains__("password"):
                new_password_provided = True
                new_password = data.pop("password")

            new_board_tab_id_provided = False
            new_board_tab_id = None
            if data.__contains__("board_tab_id"):
                new_board_tab_id_provided = True
                new_board_tab_id = data.pop("board_tab_id")

            with transaction.atomic():
                for key, value in data.items():
                    setattr(password_obj, key, value)

                if new_password_provided:
                    password_obj.change_password(new_password, commit=False)
                if new_board_tab_id_provided:
                    obj.board_tab_id = new_board_tab_id

                password_obj.save()
                obj.save()

            response = BoardPasswordAPIResponseSerializer(instance=obj)
            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, board_id:int, password_code:str, format=None):
        try:
            permissions = Board.get_board_user_permissions(board_id, request.user.id)
        except BoardUserAssignment.DoesNotExist:
            raise Http404()
        
        try:
            obj = BoardPassword.objects.select_related("password").get(
                board_id=board_id,
                password__code=password_code
            )
        except BoardPassword.DoesNotExist:
            raise Http404()


        if not permissions["delete"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj.remove()

        return Response(status=status.HTTP_204_NO_CONTENT)

        

class BoardPasswordCopyAPI(GenericAPIView):

    def post(self, request, board_id:int, password_code:str, format=None):
        try:
            permissions = Board.get_board_user_permissions(board_id, request.user.id)
        except BoardUserAssignment.DoesNotExist:
            raise Http404()
        
        try:
            obj = BoardPassword.objects.select_related("password").get(
                board_id=board_id,
                password__code=password_code
            )
        except BoardPassword.DoesNotExist:
            raise Http404()

        if not permissions["read"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(data=obj.password.read(), status=status.HTTP_200_OK)
