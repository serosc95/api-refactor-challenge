from .app import app
from .views import (
    TensileView,
    CteView,
    NanoindentationView,
    DmaView,
    DscView,
)


def register_routes():
    """
    Registra todas las rutas de la aplicación.
    """
    app.add_url_rule(
        '/tensile',
        view_func=TensileView.as_view("tensile"),
        methods=['GET', 'POST']
    )
    
    app.add_url_rule(
        '/cte',
        view_func=CteView.as_view("cte"),
        methods=['GET', 'POST']
    )
    
    app.add_url_rule(
        '/nanoindentation',
        view_func=NanoindentationView.as_view("nanoindentation"),
        methods=['GET', 'POST']
    )
    
    app.add_url_rule(
        '/dma',
        view_func=DmaView.as_view("dma"),
        methods=['GET', 'POST']
    )
    
    app.add_url_rule(
        '/dsc',
        view_func=DscView.as_view("dsc"),
        methods=['GET', 'POST']
    )


# Registrar rutas al importar el módulo
register_routes()
