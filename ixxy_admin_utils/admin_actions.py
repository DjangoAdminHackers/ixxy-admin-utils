from django.http import HttpResponse
from import_export.formats import base_formats


def xlsx_export_action(modeladmin, request, queryset):

    formats = modeladmin.get_export_formats()
    file_format = base_formats.XLSX()

    export_data = modeladmin.get_export_data(file_format, queryset, request=request)
    content_type = file_format.get_content_type()
    # Django 1.7 uses the content_type kwarg instead of mimetype
    try:
        response = HttpResponse(export_data, content_type=content_type)
    except TypeError:
        response = HttpResponse(export_data, mimetype=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        modeladmin.get_export_filename(file_format),
    )
    return response
xlsx_export_action.short_description = "Export selected rows to Excel"