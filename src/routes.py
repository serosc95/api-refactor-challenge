from .app import app
from .views import (
    TensileView,
    CteView,
    NanoindentationView,
    DmaView,
    DscView,
)
from .views.download import DownloadView, DownloadByNameView


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
    
    app.add_url_rule(
        '/files/<path:file_key>',
        view_func=DownloadView.as_view("get_file_by_key"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/files',
        view_func=DownloadView.as_view("get_file_by_key_query"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/files/name/<path:filename>',
        view_func=DownloadByNameView.as_view("get_file_by_name"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/files/name',
        view_func=DownloadByNameView.as_view("get_file_by_name_query"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/download/<path:file_key>',
        view_func=DownloadView.as_view("download_by_key"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/download',
        view_func=DownloadView.as_view("download_by_key_query_old"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/download/name/<path:filename>',
        view_func=DownloadByNameView.as_view("download_by_name"),
        methods=['GET']
    )
    
    app.add_url_rule(
        '/download/name',
        view_func=DownloadByNameView.as_view("download_by_name_query_old"),
        methods=['GET']
    )


# Registrar rutas al importar el módulo
register_routes()
