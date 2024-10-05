from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from PIL import Image
import io
import logging
import requests
from dotenv import load_dotenv
import os


load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)

# Função para decodificar a imagem base64
def decode_image(image_base64):
    try:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        image = np.array(image)
        logging.info("Imagem decodificada com sucesso.")
        return image
    except Exception as e:
        logging.error(f"Erro ao decodificar a imagem base64: {str(e)}")
        return None

# Função para pré-processar a imagem
def preprocess_image(image):
    try:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        logging.info("Imagem pré-processada com sucesso.")
        return blurred_image
    except Exception as e:
        logging.error(f"Erro ao pré-processar a imagem: {str(e)}")
        return None

# Função para determinar o tipo de pele
def determine_skin_type(stddev):
    if stddev[0][0] < 20:
        return "seca"
    elif 20 <= stddev[0][0] < 40:
        return "mista"
    else:
        return "oleosa"

# Função para analisar a pele
def analyze_skin(image):
    logging.info("Iniciando a análise da pele...")
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    logging.info("Imagem convertida para o espaço de cor HSV.")

    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    skin_mask = cv2.inRange(hsv_image, lower_skin, upper_skin)
    logging.info("Máscara de pele criada.")

    skin = cv2.bitwise_and(image, image, mask=skin_mask)
    logging.info("Aplicando máscara de pele na imagem.")

    gray_skin = preprocess_image(skin)
    if gray_skin is None:
        logging.error("Erro ao pré-processar a imagem da pele.")
        return None

    mean, stddev = cv2.meanStdDev(gray_skin, mask=skin_mask)

    skin_type = determine_skin_type(stddev)
    color_analysis = analyze_color(hsv_image)
    problems = detect_skin_problems(gray_skin, image)
    texture_analysis = analyze_texture(gray_skin)

    logging.info("Análise da pele concluída.")
    return {
        'skinType': skin_type,
        'colorAnalysis': color_analysis,
        'problems': problems,
        'textureAnalysis': texture_analysis
    }

# Função para analisar a cor
def analyze_color(hsv_image):
    h, s, v = cv2.split(hsv_image)
    return {
        'meanHue': np.mean(h),
        'meanSaturation': np.mean(s),
        'meanValue': np.mean(v)
    }

# Função para detectar problemas na pele
def detect_skin_problems(gray_skin, original_image):
    problems = []
    _, skin_mask = cv2.threshold(gray_skin, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_problems = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:
            problem_type = classify_spot(gray_skin, contour)
            detected_problems.append(f'{problem_type} detectada com área: {area:.2f}')
            cv2.drawContours(original_image, [contour], -1, (0, 0, 255), 2)

    if detected_problems:
        problems.append("Manchas detectadas: " + ', '.join(detected_problems))
    else:
        problems.append("Nenhuma mancha detectada.")

    return problems

# Função para classificar as manchas
def classify_spot(gray_skin, contour):
    mask = np.zeros(gray_skin.shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mean_intensity = cv2.mean(gray_skin, mask=mask)[0]

    if mean_intensity < 80:
        return "Possível mancha de sol"
    elif 80 <= mean_intensity < 150:
        return "Possível mancha de acne"
    else:
        return "Possível mancha desconhecida"

# Função para analisar a textura
def analyze_texture(gray_skin):
    texture_stddev = np.std(gray_skin)
    if texture_stddev < 20:
        return {
            'textureCondition': "boa",
            'textureStdDev': texture_stddev
        }
    elif 20 <= texture_stddev < 40:
        return {
            'textureCondition': "razoável",
            'textureStdDev': texture_stddev
        }
    else:
        return {
            'textureCondition': "ruim",
            'textureStdDev': texture_stddev
        }

# Função para obter a imagem processada
def get_processed_image(image):
    try:
        _, buffer = cv2.imencode('.png', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        logging.info("Imagem processada e codificada com sucesso.")
        return image_base64
    except Exception as e:
        logging.error(f"Erro ao codificar a imagem processada: {str(e)}")
        return None

# Função para enviar os dados para o Gemini
def send_to_gemini(analysis_result):
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

    message = (
        f"Resultados da análise da pele:\n"
        f"Tipo de pele: {analysis_result['skinType']}\n"
        f"Análise de cor: Hue médio: {analysis_result['colorAnalysis']['meanHue']}, "
        f"Saturação média: {analysis_result['colorAnalysis']['meanSaturation']}, "
        f"Valor médio: {analysis_result['colorAnalysis']['meanValue']}\n"
        f"Problemas detectados: {', '.join(analysis_result['problems'])}\n"
        f"Condição da textura: {analysis_result['textureAnalysis']['textureCondition']}, "
        f"Desvio padrão da textura: {analysis_result['textureAnalysis']['textureStdDev']}\n"
    )

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(gemini_url, headers=headers, json=data)

        if response.status_code == 200:
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            logging.info(f"Resposta do Gemini: {gemini_response}")
            return gemini_response
        else:
            logging.error(f"Erro ao comunicar com o Gemini. Status code: {response.status_code}, Resposta: {response.text}")
            return f"Erro ao comunicar com o Gemini. Status code: {response.status_code}"

    except Exception as e:
        logging.error(f"Erro na comunicação com a API: {str(e)}")
        return f"Erro na comunicação com a API: {str(e)}"

@app.route('/analyze-skin', methods=['POST'])
def analyze_skin_route():
    data = request.get_json()
    image_base64 = data.get('image')

    if not image_base64:
        logging.error("Nenhuma imagem fornecida no request.")
        return jsonify({'error': 'Nenhuma imagem fornecida'}), 400

    logging.info("Imagem base64 recebida, iniciando decodificação.")
    image = decode_image(image_base64)

    if image is None:
        logging.error("Erro ao decodificar a imagem.")
        return jsonify({'error': 'Erro ao decodificar a imagem'}), 500

    logging.info(f"Imagem recebida com dimensões: {image.shape}.")
    
    logging.info("Iniciando análise da pele.")
    analysis_result = analyze_skin(image)
    if analysis_result is None:
        logging.error("Erro na análise da pele.")
        return jsonify({'error': 'Erro na análise da pele'}), 500

    logging.info(f"Resultado da Análise da Pele: {analysis_result}")

    logging.info("Iniciando processamento da imagem.")
    processed_image_base64 = get_processed_image(image)

    if processed_image_base64 is None:
        logging.error("Erro ao processar a imagem.")
        return jsonify({'error': 'Erro ao processar a imagem'}), 500

    logging.info("Imagem processada e codificada com sucesso.")
    gemini_response = send_to_gemini(analysis_result)

    logging.info("Respondendo com a análise e a imagem processada.")
    return jsonify({
        "analysis_result": analysis_result,
        "processed_image": processed_image_base64,
        "gemini_response": gemini_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
