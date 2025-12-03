"""
Cliente HTTP para probar la API de IA directamente
Permite enviar imágenes y ver resultados sin MQTT
"""
import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


class AIServiceClient:
    """Cliente para el servicio de IA"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('AI_SERVICE_URL', 'http://localhost:5001')
        
    def health_check(self) -> Dict[str, Any]:
        """Verificar estado del servicio"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "No se puede conectar al servicio"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo"""
        try:
            response = requests.get(f"{self.base_url}/model/info", timeout=5)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def detect_objects(self, image_path: str) -> Dict[str, Any]:
        """
        Detectar objetos en una imagen (endpoint /detect)
        Retorna detecciones sin guardar en BD
        """
        try:
            # Leer imagen
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Enviar como multipart/form-data
            files = {
                'image': (Path(image_path).name, image_data, 'image/jpeg')
            }
            
            response = requests.post(
                f"{self.base_url}/detect",
                files=files,
                timeout=30
            )
            
            return response.json()
            
        except FileNotFoundError:
            return {"error": f"Imagen no encontrada: {image_path}"}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_evidence(self, evidence_id: int, image_path: str) -> Dict[str, Any]:
        """
        Analizar evidencia existente (endpoint /analyze)
        Actualiza ai_metadata en la BD
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            files = {
                'image': (Path(image_path).name, image_data, 'image/jpeg')
            }
            data = {
                'evidence_id': evidence_id
            }
            
            response = requests.post(
                f"{self.base_url}/analyze",
                files=files,
                data=data,
                timeout=30
            )
            
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}


class BackendAPIClient:
    """Cliente para el backend principal"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('API_URL', 'http://localhost:5000/api')
        self.token = None
    
    def login(self, email: str, password: str) -> bool:
        """Iniciar sesión y obtener token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                return True
            return False
            
        except Exception as e:
            print(f"Error login: {e}")
            return False
    
    def _headers(self) -> Dict[str, str]:
        """Headers con autenticación"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def get_zones(self) -> list:
        """Obtener zonas"""
        try:
            response = requests.get(
                f"{self.base_url}/zones",
                headers=self._headers(),
                timeout=10
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            return []
    
    def get_devices(self) -> list:
        """Obtener dispositivos"""
        try:
            response = requests.get(
                f"{self.base_url}/devices",
                headers=self._headers(),
                timeout=10
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            return []
    
    def get_events(self, limit: int = 10) -> list:
        """Obtener eventos recientes"""
        try:
            response = requests.get(
                f"{self.base_url}/events",
                params={"limit": limit},
                headers=self._headers(),
                timeout=10
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            return []
    
    def get_evidences(self, limit: int = 10) -> list:
        """Obtener evidencias"""
        try:
            response = requests.get(
                f"{self.base_url}/evidences",
                params={"limit": limit},
                headers=self._headers(),
                timeout=10
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            return []


def print_detection_results(results: Dict[str, Any], image_name: str = ""):
    """Imprimir resultados de detección de forma bonita"""
    print("\n" + "="*60)
    if image_name:
        print(f"📷 Imagen: {image_name}")
    print("="*60)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Info general
    if "image_size" in results:
        w, h = results["image_size"]
        print(f"📐 Tamaño: {w}x{h} píxeles")
    
    if "simulated" in results and results["simulated"]:
        print("⚠️  Modo simulado (sin modelo TFLite)")
    
    # Detecciones
    detections = results.get("detections", [])
    total = results.get("total_detections", len(detections))
    persons = results.get("persons_detected", 0)
    
    print(f"\n🔍 Total detecciones: {total}")
    print(f"👤 Personas detectadas: {persons}")
    
    if detections:
        print("\n📋 Detalle de detecciones:")
        print("-"*50)
        for i, det in enumerate(detections, 1):
            cls = det.get("class", "unknown")
            conf = det.get("confidence", 0)
            bbox = det.get("bbox", [])
            
            # Emoji según clase
            emoji = "👤" if cls == "person" else "🚗" if cls == "car" else "🐕" if cls in ["dog", "cat"] else "📦"
            
            print(f"  {i}. {emoji} {cls}")
            print(f"     Confianza: {conf*100:.1f}%")
            if bbox:
                print(f"     BBox: [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]")
            print()
    else:
        print("\n✨ No se detectaron objetos")
    
    print("="*60)
