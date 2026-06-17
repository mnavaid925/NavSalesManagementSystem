"""Template context shared on every page (registered in settings.TEMPLATES)."""
from .navigation import build_sidebar

# Server-rendered default layout attributes. layout.js restores the user's saved
# choices from localStorage on top of these, so the first paint is never unstyled.
LAYOUT_DEFAULTS = {
    "sidebar": "vertical",       # vertical | horizontal | detached
    "theme": "light",            # light | dark
    "width": "fluid",            # fluid | boxed
    "position": "fixed",         # fixed | scrollable
    "topbar": "light",           # light | dark
    "sidebar_size": "default",   # default | compact | small-icon | icon-hover
    "sidebar_color": "light",    # light | colored
    "direction": "ltr",          # ltr | rtl
    "preloader": "enable",       # enable | disable
}


def site_context(request):
    return {
        "APP_NAME": "Salezy",
        "APP_TAGLINE": "Sales Management System",
        "nav_modules": build_sidebar(),
        "current_path": request.path,
        "current_tenant": getattr(request, "tenant", None),
        "layout_defaults": LAYOUT_DEFAULTS,
        "ASSET_VERSION": "1",  # bump to bust the browser cache on css/js (lesson L15)
    }
