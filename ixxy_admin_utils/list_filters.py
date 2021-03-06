import datetime
from django.contrib.admin import FieldListFilter, DateFieldListFilter
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


def custom_field_list_filter(title=None):

    # Allow overriding of
    # ('events__type', custom_field_list_filter(title='event type')),

    class Wrapper(FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = FieldListFilter.create(*args, **kwargs)
            instance.title = title or instance.title
            return instance
    return Wrapper


def makeRangeFieldListFilter(lookups, nullable=False, title=None):
    
    """Mostly based on https://djangosnippets.org/snippets/2779/
    
    Modified to work with date ranges

    A factory for ListFilter's.
    
    Example Usage:

    list_filter = (

       ('chapters', makeRangeFieldListFilter([
           ('1', 1, 2),
           ('2 to 10', 2, 10),
           ('11 to 30', 11, 30),
           ('31 to 100', 31, 100),
           ('At least 100', 100, None),
       ], nullable=True)),

       ('word_count', makeRangeFieldListFilter([
           ('Less than 1000', None, 1000),
           ('1K to 5K', 1000, 5000),
           ('5K to 10K', 5000, 10000),
           ('10K to 75K', 10000, 75000),
           ('75K to 150K', 75000, 150000),
           ('150K to 300K', 150000, 300000),
           ('At least 300K', 300000, None),
       ], nullable=True)),

       ('derivatives_count', makeRangeFieldListFilter([
           ('None', 0, 1),
           ('1 to 5', 1, 5),
           ('5 to 50', 5, 50),
           ('50 to 1000', 50, 1000),
           ('At least 1000', 1000, None),
       ])),

    )"""
    
    class RangeFieldListFilter(FieldListFilter):
        
        def __init__(self, field, request, params, model, model_admin, field_path, title=title):
            
            self.field_generic = '%s__' % field_path
            self.range_params = dict(
                [(k, v) for k, v in params.items()
                    if k.startswith(self.field_generic)]
            )
            
            self.lookup_kwarg_start = '%s__gte' % field_path
            self.lookup_kwarg_stop = '%s__lt' % field_path
            self.lookup_kwarg_null = '%s__isnull' % field_path
            
            self.links = [(_('Any'), {}), ]
            
            for name, start, stop in lookups:
                
                # If we pass in a timedelta then assume we want date filtering
                # relative to now
                # TODO This only supports date not datetime
                is_date_based = False
                if isinstance(start, datetime.timedelta):
                    start = timezone.now() + start
                    is_date_based = True
                if isinstance(stop, datetime.timedelta):
                    stop = timezone.now() + stop
                    is_date_based = True
                
                query_params = {}
                
                if is_date_based:
                    if start is not None:
                        start = str(start.date())
                    if stop is not None:
                        stop = str(stop.date())

                if start is not None:
                    query_params[self.lookup_kwarg_start] = start
                if stop is not None:
                    query_params[self.lookup_kwarg_stop] = stop
                
                self.links.append((name, query_params))
            
            if nullable:
                self.links.append((_('Unknown'), {
                    self.lookup_kwarg_null: 'True'
                }))
            
            super(RangeFieldListFilter, self).__init__(
                field,
                request,
                params,
                model,
                model_admin,
                field_path,
            )

            # Allow a custom title
            if title is not None:
                self.title = title
        
        def expected_parameters(self):
            return [
                self.lookup_kwarg_start,
                self.lookup_kwarg_stop,
                self.lookup_kwarg_null
            ]
        
        def choices(self, cl):
            for title, param_dict in self.links:
                yield {
                    'selected': self.range_params == param_dict,
                    'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                    'display': title,
                }
    
    return RangeFieldListFilter


class DateFieldListFilterOrNull(DateFieldListFilter):
    # TODO this class won't be necessary in django >= 1.11
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_isnull = '%s__isnull' % (field_path, )
        super(DateFieldListFilterOrNull, self).__init__(field, request, params, model, model_admin, field_path)
        # 'Any date' is poor wording for an empty query, replace it with 'All items'
        self.links = ((_('All items'), {}),) + self.links[1:]
        # Add filters for _isnull
        self.links = self.links + (
           (_('No date'), {
                self.lookup_kwarg_isnull: 'True',
            }),
           (_('Has date'), {
                self.lookup_kwarg_isnull: 'False',
            }),
           )

    def expected_parameters(self):
        return super(DateFieldListFilterOrNull, self).expected_parameters() + [self.lookup_kwarg_isnull, ]
