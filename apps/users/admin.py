# coding=utf-8
#
# Created on Mar 21, 2014, by Junn
# 
#

from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters)


def set_user_not_active(modeladmin, request, queryset):
    queryset.filter(is_superuser=False).update(is_active=False)
set_user_not_active.short_description = u'封禁账号'

def set_user_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
set_user_active.short_description = u'激活账号'


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nickname', 'email', 'phone', 'gender', 'avatar',
                                         'login_count', )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    list_display = (
        'id', 'nickname', 'email', 'phone', 'username', 'gender',
        'is_active', 'is_superuser', 'is_staff', 'login_count', 'created_time'
    )

    list_display_links = ('id', 'email', 'nickname', 'username', )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups',)
    search_fields = ('id', 'username', 'nickname', 'email', 'phone')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    add_form_template = 'admin/auth/user/add_form.html'

    actions = (set_user_not_active, set_user_active)

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)

    def lookup_allowed(self, lookup, value):
        if lookup.startswith('password'):
            return False
        return super(UserAdmin, self).lookup_allowed(lookup, value)

    def save_model(self, request, obj, form, change):
        super(UserAdmin, self).save_model(request, obj, form, change)
        obj.clear_cache()

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(UserAdmin, self).response_add(request, obj, post_url_continue)


admin.site.register(User, UserAdmin)


