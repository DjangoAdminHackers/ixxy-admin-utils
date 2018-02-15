from dal_select2_tagging.widgets import TaggingSelect2
from django import VERSION
from tagging.utils import parse_tag_input


class IxxyTaggingSelect2(TaggingSelect2):

    # TaggingSelect2 doesn't handle spaces as delimeters in tags
    # Django-tagging has a function we can use that just works

    def render_options(self, *args):
        """Render only selected tags."""
        selected_choices_arg = 1 if VERSION < (1, 10) else 0

        selected_choices = args[selected_choices_arg]

        if selected_choices:
            selected_choices = parse_tag_input(selected_choices)

        options = [
            '<option value="%s" selected="selected">%s</option>' % (c, c)
            for c in selected_choices
        ]

        return '\n'.join(options)