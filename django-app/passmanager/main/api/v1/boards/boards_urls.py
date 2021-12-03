from django.urls import path, re_path
from .boards_api import (
    BoardsAPI, 
    BoardAPI,
    BoardLeaveAPI,
    BoardAssignmentsAPI,
    BoardAssignmentAPI,
    BoardTabsAPI,
    BoardTabAPI,
    BoardAssignmentsUsersSearchAPI,
    BoardPasswordsAPI,
    BoardPasswordAPI,
    BoardPasswordCopyAPI
)

urlpatterns = [
    path("api/v1/boards/", BoardsAPI.as_view(), name="api_v1_boards"),
    path("api/v1/board/<int:board_id>", BoardAPI.as_view(), name="api_v1_board"),
    path("api/v1/board/<int:board_id>/leave/", BoardLeaveAPI.as_view(), name="api_v1_board_leave"),
    path("api/v1/board/<int:board_id>/assignments/", BoardAssignmentsAPI.as_view(), name="api_v1_board_assignments"),
    path("api/v1/board/<int:board_id>/assignment/<int:assignment_id>", BoardAssignmentAPI.as_view(), name="api_v1_board_assignment"),
    path("api/v1/board/<int:board_id>/assignments/search-user/", BoardAssignmentsUsersSearchAPI.as_view(), name="api_v1_board_assignments_search_user"),
    path("api/v1/board/<int:board_id>/tabs/", BoardTabsAPI.as_view(), name="api_v1_board_tabs"),
    path("api/v1/board/<int:board_id>/tab/<int:tab_id>", BoardTabAPI.as_view(), name="api_v1_board_tab"),
    path("api/v1/board/<int:board_id>/passwords/", BoardPasswordsAPI.as_view(), name="api_v1_board_passwords"),
    re_path(r'^api/v1/board/(?P<board_id>([0-9]+))/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))$', BoardPasswordAPI.as_view(), name='api_v1_board_password'),
    re_path(r'^api/v1/board/(?P<board_id>([0-9]+))/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/copy/$', BoardPasswordCopyAPI.as_view(), name='api_v1_board_password_copy'),
]