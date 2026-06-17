from django import forms


class StyledFormMixin:
    """Apply the theme.css form classes to every widget automatically.

    Shared by every app's forms so inputs render consistently without repeating
    `attrs={'class': ...}` on each field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = "form-check-input"
            elif isinstance(widget, forms.Select):
                css = "form-select"
            elif isinstance(widget, forms.Textarea):
                css = "form-textarea"
            else:
                css = "form-input"
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css}".strip()
