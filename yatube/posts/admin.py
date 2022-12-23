from django.contrib import admin
from .models import Post, Group, Follow, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'image',
                    'pub_date',
                    'author',
                    'group'
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'slug',
                    'title',
                    'description',
                    )
    search_fields = ('description',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author',
                    )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text',
                    'author',
                    'post',
                    'created',
                    )
    search_fields = ('text',)
    list_filter = ('created',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
