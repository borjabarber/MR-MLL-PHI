from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import pymysql
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración de la base de datos usando variables de entorno
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Valor por defecto 3306
DB_NAME = os.getenv("DB_NAME")

try:
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
    )
    
    db.autocommit(True)
    cursor = db.cursor()
    print("Conectado al servidor MySQL correctamente.")
    
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")
    
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            role VARCHAR(50),
            content TEXT,
            response TEXT
        )
    """)
    print("Tabla 'chats' verificada/creada.")
    
except pymysql.MySQLError as e:
    print(f"Error al conectar al servidor MySQL: {e}")
    raise e

# Configuración de Hugging Face con clave de API desde el entorno
HF_API_KEY = os.getenv("HF_API_KEY")
client = InferenceClient(api_key=HF_API_KEY)

class ChatRequest(BaseModel):
    role: str
    content: str

@app.get("/")
async def hello():
    return {"message": "Bienvenido a tu cibertaberna, entra en /chat para hablar con el camarero"}

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    messages = [{"role": request.role, "content": request.content}]
    
    try:
        completion = client.chat.completions.create(
            model="microsoft/Phi-3.5-mini-instruct",
            messages=messages,
            max_tokens=1000
        )
        
        response = completion.choices[0].message.content
        
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO chats (role, content, response) 
            VALUES (%s, %s, %s)
        """, (request.role, request.content, response))
        
        db.commit()
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
