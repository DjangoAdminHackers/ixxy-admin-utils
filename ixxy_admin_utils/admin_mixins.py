from django.http import HttpResponseRedirect
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .custom_fields import (
    BooleanTimeStampField,
    BooleanTimeStampFormField,
    BooleanTimeStampWidget,
)

try:
    from dal_select2.widgets import ModelSelect2Multiple
except ImportError:  # Avoid ImportError in the absence of django-autocomplete-light
    ModelSelect2Multiple = None


class RedirectableAdmin(object):
    
    """If you use this as a mixin to your ModelAdmin then the change and add forms will accept
        a url parameter '_redirect' and redirect to that on save"""
    
    def response_post_save_change(self, request, obj):
        if '_redirect' in request.GET:
            return HttpResponseRedirect(request.GET['_redirect'])
        else:
            return super(RedirectableAdmin, self).response_post_save_change(request, obj)

    def response_post_save_add(self, request, obj):
        if '_redirect' in request.GET:
            return HttpResponseRedirect(request.GET['_redirect'])
        else:
            return super(RedirectableAdmin, self).response_post_save_add(request, obj)

    def delete_view(self, request, object_id, extra_context=None):
        response = super(RedirectableAdmin, self).delete_view(request, object_id, extra_context)
        if '_redirect' in request.GET and response.status_code == 302:
            return HttpResponseRedirect(request.GET['_redirect'])
        else:
            return response


class ModifyRelatedObjectAdmin(RedirectableAdmin):
    
    """If you use this as a mixin to your ModelAdmin then the change form will accept
        _redirect same as with RedirectableAdmin. Additionally add forms
        will also accept paramters to identify a parent object and field which will
        be set to the newly created object before redirecting"""

    def response_post_save_add(self, request, obj):
        if '_related_object' in request.GET:
            app_label, model_name, object_id, field_name = request.GET['_related_object'].split(' ')
            content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
            related_object = content_type.get_object_for_this_type(pk=object_id)
            setattr(related_object, field_name, obj)
            related_object.save()
        return super(ModifyRelatedObjectAdmin, self).response_post_save_add(request, obj)


class HideAddRelatedMixin(object):
    
    """ModelAdmin mixin that disables the green 'add related object' plus icon
    for any fields listed in hide_add_related_fields
    Usage: hide_add_related_fields = ['user', 'group']
    Alternately if there is a property 'show_add_related_fields' then this works as a whitelist"""

    def get_form(self, request, obj=None, **kwargs):
        form = super(HideAddRelatedMixin, self).get_form(request, obj, **kwargs)
        if getattr(self, 'show_add_related_fields', None) is not None:
            for field in list(form.base_fields.keys()):
                if field not in self.show_add_related_fields:
                    form.base_fields[field].widget.can_add_related = False
        else:
            for field in getattr(self, 'hide_add_related_fields', []):
                form.base_fields[field].widget.can_add_related = False

        return form


class DisableDeletionMixin(object):
    def has_delete_permission(self, request, obj=None):
        return False


class LongListFilterMixin(object):
    
    """Automatically reduce the amount of space taken up by very long filters.
    It hides the list of options and replaces it with an input field that autocompletes.
    
    Unlike a true autocomplete this won't save queries or speed up page load
    but it's a quick and dirty improvement to the UI"""
    
    @property
    def media(self):
        
        cdn_base = 'https://ajax.googleapis.com/ajax/libs/'
        
        show = getattr(self, 'long_list_filter_show', 'active')
        threshold = getattr(self, 'long_list_filter_threshold', '300')
        height = getattr(self, 'long_list_filter_height', '100')
        
        default_media = super(LongListFilterMixin, self).media
        
        js = default_media._js + [
            '{}jqueryui/1.13.2/jquery-ui.min.js'.format(cdn_base),
            mark_safe('js/ixxy_admin_utils/long_list_filter.js?show={}&threshold={}&height={}'.format(
                show,
                threshold,
                height,
            )),
        ]
        css = {
            'all': default_media._css.get('all', []) + [
                '{}jqueryui/1.13.2/themes/smoothness/jquery-ui.css'.format(cdn_base)
            ]
        }
        media = forms.Media(js=js, css=css)
        return media


class AutocompleteMixin(object):
    
    """Reduces the amount of boilerplate needed by autocomplete-light.
    Define a property on your ModelAdmin called 'autocomplete_widgets'.
    This is a dict mapping field names to Autocomplete fields:

    autocomplete_widgets = {
        'contact': autocomplete.ModelSelect2(url='contact-autocomplete'),
        'event': autocomplete.ModelSelect2(url='event-autocomplete'),
        'team': autocomplete.ModelSelect2(url='team-autocomplete', forward=['event']),
    }
    """
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # Automatically assign autocomplete widgets based on an autocomplete_widgets dict
        if db_field.name in getattr(self, 'autocomplete_widgets', {}):
            kwargs['widget'] = self.autocomplete_widgets[db_field.name]
        return super(AutocompleteMixin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Remove the hardcoded m2m help_text if the widget is ModelSelect2Multiple
        form_field = super(AutocompleteMixin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )
        if isinstance(form_field.widget, ModelSelect2Multiple):
            unwanted_msg = 'Hold down "Control", or "Command" on a Mac, to select more than one.'
            form_field.help_text = form_field.help_text.replace(unwanted_msg, '')
        return form_field


class BooleanTimeStampMixin(object):
    
    """If you this with any model containing BooleanTimeStampField
    then flipping the checkbox to 'on' will set the datetime to timezone.now()
    The widget will be a checkbox with the stored datetime as label"""
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, BooleanTimeStampField):
            kwargs['form_class'] = BooleanTimeStampFormField
            kwargs['widget'] = BooleanTimeStampWidget(label=db_field.verbose_name.title())
            kwargs['label'] = ''
            request = kwargs.pop('request')
            db_field.formfield(**kwargs)
            kwargs['request'] = request
        return super(BooleanTimeStampMixin, self).formfield_for_dbfield(db_field, **kwargs)
