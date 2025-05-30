"""
HTML Widget classes
"""

import copy
import datetime
import warnings
from collections import defaultdict
from graphlib import CycleError, TopologicalSorter
from itertools import chain

from django.forms.utils import flatatt, to_current_timezone
from django.templatetags.static import static
from django.utils import formats
from django.utils.dates import MONTHS
from django.utils.formats import get_format
from django.utils.html import format_html, html_safe
from django.utils.regex_helper import _lazy_re_compile
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django.forms.renderers import get_default_renderer

__all__ = (
    "Script",
    "Media",
    "MediaDefiningClass",
    "Widget",
    "TextInput",
    "NumberInput",
    "EmailInput",
    "URLInput",
    "ColorInput",
    "SearchInput",
    "TelInput",
    "PasswordInput",
    "HiddenInput",
    "MultipleHiddenInput",
    "FileInput",
    "ClearableFileInput",
    "Textarea",
    "DateInput",
    # "DateTimeInput",
    "DateTimeInputNew",
    "TimeInput",
    "CheckboxInput",
    "Select",
    "NullBooleanSelect",
    "SelectMultiple",
    "RadioSelect",
    "CheckboxSelectMultiple",
    "MultiWidget",
    "SplitDateTimeWidget",
    "SplitHiddenDateTimeWidget",
    "SelectDateWidget",
    "TextareaInput",
    "FloatInput",
    "SwitchInput",
    "ImageInput",
    "ForeignKeyInput",
)

MEDIA_TYPES = ("css", "js")


class MediaOrderConflictWarning(RuntimeWarning):
    pass


@html_safe
class MediaAsset:
    element_template = "{path}"

    def __init__(self, path, **attributes):
        self._path = path
        self.attributes = attributes

    def __eq__(self, other):
        # Compare the path only, to ensure performant comparison in Media.merge.
        return (self.__class__ is other.__class__ and self.path == other.path) or (
            isinstance(other, str) and self._path == other
        )

    def __hash__(self):
        # Hash the path only, to ensure performant comparison in Media.merge.
        return hash(self._path)

    def __str__(self):
        return format_html(
            self.element_template,
            path=self.path,
            attributes=flatatt(self.attributes),
        )

    def __repr__(self):
        return f"{type(self).__qualname__}({self._path!r})"

    @property
    def path(self):
        """
        Ensure an absolute path.
        Relative paths are resolved via the {% static %} template tag.
        """
        if self._path.startswith(("http://", "https://", "/")):
            return self._path
        return static(self._path)


class Script(MediaAsset):
    element_template = '<script src="{path}"{attributes}></script>'

    def __init__(self, src, **attributes):
        # Alter the signature to allow src to be passed as a keyword argument.
        super().__init__(src, **attributes)


@html_safe
class Media:
    def __init__(self, media=None, css=None, js=None):
        if media is not None:
            css = getattr(media, "css", {})
            js = getattr(media, "js", [])
        else:
            if css is None:
                css = {}
            if js is None:
                js = []
        self._css_lists = [css]
        self._js_lists = [js]

    def __repr__(self):
        return "Media(css=%r, js=%r)" % (self._css, self._js)

    def __str__(self):
        return self.render()

    @property
    def _css(self):
        css = defaultdict(list)
        for css_list in self._css_lists:
            for medium, sublist in css_list.items():
                css[medium].append(sublist)
        return {medium: self.merge(*lists) for medium, lists in css.items()}

    @property
    def _js(self):
        return self.merge(*self._js_lists)

    def render(self):
        return mark_safe(
            "\n".join(
                chain.from_iterable(
                    getattr(self, "render_" + name)() for name in MEDIA_TYPES
                )
            )
        )

    def render_js(self):
        return [
            (
                path.__html__()
                if hasattr(path, "__html__")
                else format_html('<script src="{}"></script>', self.absolute_path(path))
            )
            for path in self._js
        ]

    def render_css(self):
        # To keep rendering order consistent, we can't just iterate over items().
        # We need to sort the keys, and iterate over the sorted list.
        media = sorted(self._css)
        return chain.from_iterable(
            [
                (
                    path.__html__()
                    if hasattr(path, "__html__")
                    else format_html(
                        '<link href="{}" media="{}" rel="stylesheet">',
                        self.absolute_path(path),
                        medium,
                    )
                )
                for path in self._css[medium]
            ]
            for medium in media
        )

    def absolute_path(self, path):
        """
        Given a relative or absolute path to a static asset, return an absolute
        path. An absolute path will be returned unchanged while a relative path
        will be passed to django.templatetags.static.static().
        """
        if path.startswith(("http://", "https://", "/")):
            return path
        return static(path)

    def __getitem__(self, name):
        """Return a Media object that only contains media of the given type."""
        if name in MEDIA_TYPES:
            return Media(**{str(name): getattr(self, "_" + name)})
        raise KeyError('Unknown media type "%s"' % name)

    @staticmethod
    def merge(*lists):
        """
        Merge lists while trying to keep the relative order of the elements.
        Warn if the lists have the same elements in a different relative order.

        For static assets it can be important to have them included in the DOM
        in a certain order. In JavaScript you may not be able to reference a
        global or in CSS you might want to override a style.
        """
        ts = TopologicalSorter()
        for head, *tail in filter(None, lists):
            ts.add(head)  # Ensure that the first items are included.
            for item in tail:
                if head != item:  # Avoid circular dependency to self.
                    ts.add(item, head)
                head = item
        try:
            return list(ts.static_order())
        except CycleError:
            warnings.warn(
                "Detected duplicate Media files in an opposite order: {}".format(
                    ", ".join(repr(list_) for list_ in lists)
                ),
                MediaOrderConflictWarning,
            )
            return list(dict.fromkeys(chain.from_iterable(filter(None, lists))))

    def __add__(self, other):
        combined = Media()
        combined._css_lists = self._css_lists[:]
        combined._js_lists = self._js_lists[:]
        for item in other._css_lists:
            if item and item not in self._css_lists:
                combined._css_lists.append(item)
        for item in other._js_lists:
            if item and item not in self._js_lists:
                combined._js_lists.append(item)
        return combined


def media_property(cls):
    def _media(self):
        # Get the media property of the superclass, if it exists
        sup_cls = super(cls, self)
        try:
            base = sup_cls.media
        except AttributeError:
            base = Media()

        # Get the media definition for this class
        definition = getattr(cls, "Media", None)
        if definition:
            extend = getattr(definition, "extend", True)
            if extend:
                if extend is True:
                    m = base
                else:
                    m = Media()
                    for medium in extend:
                        m += base[medium]
                return m + Media(definition)
            return Media(definition)
        return base

    return property(_media)


class MediaDefiningClass(type):
    """
    Metaclass for classes that can have media definitions.
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        if "media" not in attrs:
            new_class.media = media_property(new_class)

        return new_class


class Widget(metaclass=MediaDefiningClass):
    needs_multipart_form = False  # Determines does this widget need multipart form
    is_localized = False
    is_required = False
    supports_microseconds = True
    use_fieldset = False

    def __init__(self, attrs=None):
        self.attrs = {} if attrs is None else attrs.copy()

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        memo[id(self)] = obj
        return obj

    @property
    def is_hidden(self):
        return self.input_type == "hidden" if hasattr(self, "input_type") else False

    def subwidgets(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        yield context["widget"]

    def format_value(self, value):
        """
        Return a value as it should appear when rendered in a template.
        """
        if value == "" or value is None:
            return None
        if self.is_localized:
            return formats.localize_input(value)
        return str(value)

    def get_context(self, name, value, attrs):
        try:
            field_name = self.field_name
        except:
            field_name = ''
            
        return {
            "widget": {
                "name": name,
                'field_name': field_name,
                "is_hidden": self.is_hidden,
                "required": self.is_required,
                "value": self.format_value(value),
                "attrs": self.build_attrs(self.attrs, attrs),
                "template_name": self.template_name,
            },
        }

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        context = self.get_context(name, value, attrs)
        # print(context)
        return self._render(self.template_name, context, renderer)

    def _render(self, template_name, context, renderer=None):
        if renderer is None:
            renderer = get_default_renderer()
        return mark_safe(renderer.render(template_name, context))

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build an attribute dictionary."""
        return {**base_attrs, **(extra_attrs or {})}

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, return the value
        of this widget or None if it's not provided.
        """
        return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        return name not in data

    def id_for_label(self, id_):
        """
        Return the HTML ID attribute of this Widget for use by a <label>, given
        the ID of the field. Return an empty string if no ID is available.

        This hook is necessary because some widgets have multiple HTML
        elements and, thus, multiple IDs. In that case, this method should
        return an ID value that corresponds to the first ID in the widget's
        tags.
        """
        return id_

    def use_required_attribute(self, initial):
        return not self.is_hidden


class Input(Widget):
    """
    Base class for all <input> widgets.
    """

    input_type = None  # Subclasses must define this.
    template_name = "sohoui_widgets/input.html"

    def __init__(self, attrs=None):
        if attrs is not None:
            attrs = attrs.copy()
            self.input_type = attrs.pop("type", self.input_type)
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # 获取当前用户是否有编辑权
        # print(context)
        context["widget"]["type"] = self.input_type
        context["widget"]["upload_to"] = getattr(self, 'upload_to', '')
        context["widget"]["el_disabled"] = getattr(self, 'el_disabled', '')
        context["widget"]["foreigh_choices"] = getattr(self, 'foreigh_choices', [])
        return context


class TextInput(Input):
    input_type = "text"
    template_name = "sohoui_widgets/text.html"
    

class NumberInput(Input):
    input_type = "number"
    template_name = "sohoui_widgets/number.html"


class EmailInput(Input):
    input_type = "email"
    template_name = "sohoui_widgets/email.html"


class URLInput(Input):
    input_type = "url"
    template_name = "sohoui_widgets/url.html"


class ColorInput(Input):
    input_type = "color"
    template_name = "sohoui_widgets/color.html"


class SearchInput(Input):
    input_type = "search"
    template_name = "sohoui_widgets/search.html"


class TelInput(Input):
    input_type = "tel"
    template_name = "sohoui_widgets/tel.html"


class PasswordInput(Input):
    input_type = "password"
    template_name = "sohoui_widgets/password.html"

    def __init__(self, attrs=None, render_value=False):
        super().__init__(attrs)
        self.render_value = render_value

    def get_context(self, name, value, attrs):
        if not self.render_value:
            value = None
        return super().get_context(name, value, attrs)


class HiddenInput(Input):
    input_type = "hidden"
    template_name = "sohoui_widgets/hidden.html"



class Textarea(Widget):
    template_name = "sohoui_widgets/textarea.html"

    def __init__(self, attrs=None):
        # Use slightly better defaults than HTML's 20x2 box
        default_attrs = {"cols": "40", "rows": "10"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class DateTimeBaseInput(TextInput):
    format_key = ""
    supports_microseconds = False

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs)
        self.format = format or None

    def format_value(self, value):
        return formats.localize_input(
            value, self.format or formats.get_format(self.format_key)[0]
        )


class DateInput(DateTimeBaseInput):
    format_key = "DATE_INPUT_FORMATS"
    template_name = "sohoui_widgets/date.html"

class DateTimeInputNew(DateTimeBaseInput):
    format_key = "DATETIME_INPUT_FORMATS"
    template_name = "sohoui_widgets/datetime.html"


class TimeInput(DateTimeBaseInput):
    format_key = "TIME_INPUT_FORMATS"
    template_name = "sohoui_widgets/time.html"

class SliderInput(Textarea):
    template_name = 'widgets/slider.html'


class TextareaInput(TextInput):
    input_type = "textarea"
    template_name = "sohoui_widgets/textarea.html"


class FloatInput(TextInput):
    template_name = "sohoui_widgets/float.html"


class SwitchInput(Input):
    template_name = "sohoui_widgets/switch.html"
    
class ImageInput(Input):
    template_name = "sohoui_widgets/image.html"
    
class ForeignKeyInput(Input):
    template_name = "sohoui_widgets/foreignkey.html"
