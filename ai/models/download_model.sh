#!/bin/bash
# Script para descargar modelo TFLite preentrenado

MODEL_DIR="$(dirname "$0")"
MODEL_URL="https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip"

echo "Descargando modelo MobileNet SSD..."
cd "$MODEL_DIR"

# Descargar
wget -q "$MODEL_URL" -O model.zip

# Extraer
unzip -o model.zip

# Renombrar
mv detect.tflite detect.tflite 2>/dev/null || true

# Limpiar
rm -f model.zip

echo "Modelo descargado en: $MODEL_DIR/detect.tflite"
