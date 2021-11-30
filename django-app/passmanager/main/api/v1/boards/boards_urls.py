from django.urls import path, re_path
from .boards_api import (
    BoardsAPI, 
    BoardAPI,
    BoardLeaveAPI,
    BoardAssignmentsAPI,
    BoardAssignmentAPI,
    BoardTabsAPI,
    BoardTabAPI,
    BoardAssignmentsUsersSearchAPI
)

urlpatterns = [
    path("api/v1/boards/", BoardsAPI.as_view(), name="api_v1_boards"),
    path("api/v1/board/<int:board_id>", BoardAPI.as_view(), name="api_v1_board"),
    path("api/v1/board/<int:board_id>/leave/", BoardLeaveAPI.as_view(), name="api_v1_board_leave"),
    path("api/v1/board/<int:board_id>/assignments/", BoardAssignmentsAPI.as_view(), name="api_v1_board_assignments"),
    path("api/v1/board/<int:board_id>/assignment/<int:assignment_id>", BoardAssignmentAPI.as_view(), name="api_v1_board_assignment"),
    path("api/v1/board/<int:board_id>/assignments/search-user/", BoardAssignmentsUsersSearchAPI.as_view(), name="api_v1_board_assignments_search_user"),
    path("api/v1/board/<int:board_id>/tabs/", BoardTabsAPI.as_view(), name="api_v1_board_tabs"),
    path("api/v1/board/<int:board_id>/tab/<int:tab_id>", BoardTabAPI.as_view(), name="api_v1_board_tab")
]