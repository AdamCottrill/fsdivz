from django import forms
from django.forms import DateTimeInput
from django.template import loader
from django.utils.safestring import mark_safe


class SemanticDatePicker(DateTimeInput):
    """A date-time picker using sematic-ui

    modified from examples here:

    https://simpleisbetterthancomplex.com/tutorial/2019/01/03/
    how-to-use-date-picker-with-django.html
    """

    template_name = "widgets/semantic_calendar.html"

    def get_context(self, name, value, attrs):
        datetimepicker_id = "id_{name}".format(name=name)
        if attrs is None:
            attrs = dict()

        attrs["class"] = "ui calendar"

        context = super().get_context(name, value, attrs)
        context["widget"]["datetimepicker_id"] = datetimepicker_id
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class MySelect(forms.Select):
    """A custom widget that will add 'disalbed' attribute to any select
    options that don't have an id - mistakes passed in from Excel."""

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        # if option.get("value") == "":
        if option.get("value") == "-999":
            option["attrs"]["selected"] = "selected"
            option["attrs"]["disabled"] = "disabled"
        return option
