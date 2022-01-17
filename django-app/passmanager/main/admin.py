from django.contrib import admin
from main.models import (
	Password,
	UserPasswordAssignment,
	Board,
	BoardUserAssignment,
	BoardTab,
	BoardPassword,

	UserPassword,
	UserTab,
	UserPasswordShare
)
from dynamic_raw_id.admin import DynamicRawIDMixin
from dynamic_raw_id.filters import DynamicRawIDFilter

class BoardUserAssignmentInline(admin.TabularInline):
	model = BoardUserAssignment
	autocomplete_fields = ('user',)
	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

# Register your models here.
class PasswordAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'description', 'owner', 'created_by', 'created_at', 'updated_by', 'updated_at')

admin.site.register(Password, PasswordAdmin)


class UserPasswordAssignmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'password', "read", "share", "update", "owner")

admin.site.register(UserPasswordAssignment, UserPasswordAssignmentAdmin)


class BoardAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"name",
		"owner",
		"updated_at",
		"updated_by",
		"created_at",
		"created_by"
	)

	search_fields = (
		"owner__username",
		"name"
	)

	list_display_links = (
		"id",
		"name"
	)

	inlines = (
		BoardUserAssignmentInline,
	)

	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

admin.site.register(Board, BoardAdmin)


class BoardUserAssignmentAdmin(DynamicRawIDMixin, admin.ModelAdmin):
	list_display = (
		"id",
		"board",
		"user",
		"perm_admin",
		"perm_create",
		"perm_read",
		"perm_update",
		"perm_delete",
		"updated_at",
		"updated_by",
		"created_at",
		"created_by"
	)

	fieldsets = (
		(None, {
			"fields": (
				"board",
				"user"
			),
		}),
		("Advanced options", {
			'classes': ('collapse',),
			'fields': ('perm_admin', 'perm_create', 'perm_read', 'perm_update', 'perm_delete')
		})
	)

	raw_id_fields = ('board',)
	autocomplete_fields = ('user',)
	
	list_filter = ( 
		('user', DynamicRawIDFilter),
		('board', DynamicRawIDFilter),
	)

	search_fields = (
		"user__username",
		"board__name"
	)

	list_display_links = (
		"id",
	)

	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

admin.site.register(BoardUserAssignment, BoardUserAssignmentAdmin)


class BoardTabAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'name',
		'board',
		'board_order',
		'is_default'
	)

	search_fields = (
		'name',
		'board__name',
	)

	list_display_links = (
		'id', 'name'
	)

	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

admin.site.register(BoardTab, BoardTabAdmin)



class BoardPasswordAdmin(admin.ModelAdmin):
	list_display = (
		"password",
		"updated_at",
		"updated_by",
		"created_at",
		"created_by"
	)

	search_fields = (
		"password__code",
		"password__title",
		"password__url",
		"password__username",
		"password__description",
	)

	list_display_links = (
		'password',
	)

	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

admin.site.register(BoardPassword, BoardPasswordAdmin)


class UserPasswordAdmin(admin.ModelAdmin):
	list_display = (
		"password",
		"updated_at",
		"updated_by",
		"created_at",
		"created_by"
	)

	search_fields = (
		"password__code",
		"password__title",
		"password__url",
		"password__username",
		"password__description",
	)

	list_display_links = (
		'password',
	)

	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

admin.site.register(UserPassword, UserPasswordAdmin)


class UserTabAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"name",
		"user",
		"order",
		"is_default"
	)

	search_fields = (
		"name",
		"user"
	)

	list_display_links = (
		"id",
		"name"
	)


admin.site.register(UserTab, UserTabAdmin)



class UserPasswordShareAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"user",
		"user_password"
	)

	search_fields = (
		"user_password__password__code",
		"user_password__password__title",
		"user_password__password__url",
		"user_password__password__username",
		"user_password__password__description",
	)

	list_display_links = (
		'id',
	)

	exclude = (
		"created_at",
		"created_by",
		"updated_at",
		"updated_by"
	)

admin.site.register(UserPasswordShare, UserPasswordShareAdmin)