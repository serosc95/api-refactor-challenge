from src.app import app
import src.routes  # Importar para registrar las rutas

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
