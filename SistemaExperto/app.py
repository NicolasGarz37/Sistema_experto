from flask import Flask, render_template, request, jsonify
from experta import KnowledgeEngine, Rule, Fact, MATCH
import os

app = Flask(__name__)

# Cargar enfermedades desde el archivo
def cargar_enfermedades():
    enfermedades = []
    archivo = "enfermedades.txt"
    
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as file:
            for linea in file:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    enfermedad = partes[0].strip()
                    sintomas = [s.strip().lower() for s in partes[1].split(",")]
                    tratamiento = partes[2].strip()
                    enfermedades.append((enfermedad, sintomas, tratamiento))
    return enfermedades

enfermedades = cargar_enfermedades()

# Definir el sistema experto
class Diagnostico(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.resultado = None

    @Rule(Fact(sintomas=MATCH.sintomas))
    def diagnosticar(self, sintomas):
        sintomas_usuario = [s.strip().lower() for s in sintomas]
        for enfermedad, sintomas_enfermedad, tratamiento in enfermedades:
            if all(symptom in sintomas_usuario for symptom in sintomas_enfermedad):
                self.resultado = (enfermedad, tratamiento)
                break  # Se detiene en la primera coincidencia

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/diagnose", methods=["POST"])
def diagnose():
    datos = request.json
    sintomas_usuario = [s.strip().lower() for s in datos.get("symptoms", [])]
    
    # Verificar si hay al menos 3 síntomas ingresados
    if len(sintomas_usuario) < 3:
        return jsonify({"error": "Ingrese al menos 3 síntomas"}), 400

    # Diagnóstico con el sistema experto
    expert = Diagnostico()
    expert.reset()
    expert.declare(Fact(sintomas=sintomas_usuario))
    expert.run()

    if expert.resultado:
        enfermedad, tratamiento = expert.resultado
        return jsonify({"enfermedad": enfermedad, "tratamiento": tratamiento})
    else:
        return jsonify({"error": "No se encontró una enfermedad con esos síntomas."}), 404

if __name__ == "__main__":
    app.run(debug=True)
