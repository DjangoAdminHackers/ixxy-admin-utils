from django import forms
from django.db import models
from django.utils import timezone


class BooleanTimeStampWidget(forms.CheckboxInput):
    
    """Used in conjunction with BooleanTimeStampMixin"""
    
    def __init__(self, attrs=None, check_test=None, label=None):
        self.label = label
        super(BooleanTimeStampWidget, self).__init__(attrs, check_test)
    
    def render(self, name, value, attrs=None):
        widget_html = super(BooleanTimeStampWidget, self).render(name, value, attrs)
        
        # If there are validation errors - then value will still be a boolean
        # So you can't just check for truthiness
        # We're looking for a non-null datetime
        if value is not None and value is not True:
            html = '{}<span class="vCheckboxLabel">{}: {}</span>'.format(
                widget_html,
                self.label,
                value.strftime('%H:%M:%S %d/%m/%Y'),
            )
        else:
            html = '{}<span class="vCheckboxLabel">{}</span>'.format(widget_html, self.label)
        return html


class BooleanTimeStampFormField(forms.DateTimeField):
    
    """Used in conjunction with BooleanTimeStampMixin"""
    
    def to_python(self, value):
        if value:
            value = timezone.now()
        else:
            value = None
        return value


class BooleanTimeStampField(models.DateTimeField):
    
    """Used in conjunction with BooleanTimeStampMixin"""
    
    def clean(self, value, model_instance):
        
        saved_value = None
        if model_instance.pk:
            saved_instance = type(model_instance).objects.get(pk=model_instance.pk)
            saved_value = getattr(saved_instance, self.name)
        if value and saved_value is None:
            value = timezone.now()
        elif value and saved_value is not None:
            value = saved_value
        elif value is False:
            value = None
        else:
            raise ValueError
        return value
