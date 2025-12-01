import numpy as np
from flask import Flask, request, render_template
import os 
from dotenv import load_dotenv # Para manejar la clave API
from google import genai
from google.genai import types

# Carga las variables de entorno desde el archivo .env (incluida tu clave API)
load_dotenv()

# --- CONFIGURACIÓN DE GEMINI ---
# Obtiene la clave de entorno. Se asume que está en una variable de entorno
# llamada GEMINI_API_KEY o GOOGLE_API_KEY.
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except AttributeError:
    # Esto ocurre si la clave no se carga, Render lo gestiona con Secretes
    client = genai.Client() 


# Create an app object using the Flask class. 
app = Flask(__name__)

# --- FIN DE CONFIGURACIÓN DE GEMINI ---


@app.route('/')
def home():
    # Renderizamos la plantilla, el texto de predicción será vacío al inicio
    return render_template('index.html', prediction_text="")

# Define el endpoint para la recomendación de libros
@app.route('/predict', methods=['POST'])
def recommend_books():
    # 1. Obtener la consulta del usuario
    # Asume que el formulario en index.html tiene un campo 'user_query'
    user_query = request.form.get('user_query', '')
    
    if not user_query:
        return render_template('index.html', prediction_text='Por favor, introduce tu preferencia de libros.')

    # 2. Ingeniería del Prompt y Configuración de la API
    
    # 2a. Instrucción de Sistema para el Rol
    system_instruction = (
        "Eres un crítico literario y bibliotecario experto. Tu única tarea es recomendar 3 "
        "libros basándote estrictamente en la preferencia del usuario. Debes responder "
        "en formato JSON para que la aplicación web lo pueda procesar."
    )
    
    # 2b. Esquema JSON para la salida (importante para el procesamiento)
    response_schema = types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "titulo": types.Schema(type=types.Type.STRING),
                "autor": types.Schema(type=types.Type.STRING),
                "razon": types.Schema(type=types.Type.STRING, description="Breve explicación de por qué encaja con la solicitud.")
            },
            required=["titulo", "autor", "razon"]
        )
    )

    # 3. Llamada a la API de Gemini
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Modelo rápido y eficiente
            contents=[user_query],     # La consulta del usuario
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.7 # Una temperatura media para sugerencias creativas
            )
        )
    except Exception as e:
        print(f"Error en la llamada a la API: {e}")
        return render_template('index.html', prediction_text='Hubo un error al consultar a la IA. Inténtalo de nuevo.')

    # 4. Procesamiento de la Respuesta
    
    # La respuesta ya viene en un string JSON, la parseamos
    try:
        # response.text es el string JSON que generó Gemini
        import json
        recomendaciones = json.loads(response.text)
    except json.JSONDecodeError:
         return render_template('index.html', prediction_text='La IA devolvió un formato incorrecto. Inténtalo de nuevo.')
    
    # 5. Formatear la salida para el Frontend
    
    output_html = "<h2>📚 Recomendaciones de Libros:</h2><ul>"
    for book in recomendaciones:
        output_html += f"<li><strong>{book.get('titulo', 'N/D')}</strong> de {book.get('autor', 'N/D')}"
        output_html += f"<p>Razón: {book.get('razon', 'Sin razón.')}</p></li>"
    output_html += "</ul>"

    # Muestra el resultado
    return render_template('index.html', prediction_text=output_html)


if __name__ == "__main__":
    # Importante: para Render, debes usar Gunicorn en producción
    # app.run(debug=True) # Usar solo para desarrollo local
    app.run()