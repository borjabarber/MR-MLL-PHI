import requests
import os

# Cargar las variables de entorno
from dotenv import load_dotenv
load_dotenv()

# URL base para la aplicación FastAPI
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_hello_endpoint():
    # Test para verificar que el endpoint raíz ("/") devuelve el mensaje correcto
    url = f"{BASE_URL}/"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenido a tu cibertaberna, entra en /chat para hablar con el camarero"}

def test_chat_page():
    # Test para verificar que la página de chat ("/chat") carga correctamente
    url = f"{BASE_URL}/chat"
    response = requests.get(url)
    assert response.status_code == 200
    assert "html" in response.headers["Content-Type"].lower()

def test_chat_endpoint():
    # Test para verificar que el endpoint de chat (POST /chat) responde correctamente
    url = f"{BASE_URL}/chat"
    data = {
        "role": "user",
        "content": "Hola, camarero, ¿cómo estás?"
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert "response" in response.json()



