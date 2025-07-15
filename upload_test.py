import cv2
import numpy as np
import matplotlib.pyplot as plt
from google.colab import files
import io
from PIL import Image

# Instalar o EasyOCR
# !pip install easyocr
import easyocr

# Função para fazer o upload da imagem
def upload_image():
    uploaded = files.upload()
    for filename in uploaded.keys():
        content = uploaded[filename]
        image = Image.open(io.BytesIO(content)).convert("RGB")
        return np.array(image)
    return None

# Carregar o modelo EasyOCR (pode demorar um pouco na primeira execução)
reader = easyocr.Reader(['en', 'pt'], gpu=False) # 'en' e 'pt' para inglês e português. Mude para 'gpu=True' se tiver GPU disponível.

# 1. Fazer o upload da imagem
print("Por favor, faça o upload da imagem para análise:")
image_np = upload_image()

if image_np is not None:
    # Converter para escala de cinza para algumas operações se necessário
    gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

    # 2. Detectar texto na imagem
    # O detect retorna uma lista de tuplas, onde cada tupla contém:
    # (coordenadas do bounding box, texto detectado, confiança)
    results = reader.readtext(image_np)

    # Criar uma cópia da imagem para desenhar os retângulos
    image_with_boxes = image_np.copy()

    total_image_pixels = image_np.shape[0] * image_np.shape[1]
    total_text_pixels = 0
    text_data = [] # Para armazenar informações de texto (texto, % na caixa)

    for (bbox, text, prob) in results:
        # Extrair coordenadas do bounding box
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))

        # Calcular a área do texto detectado
        text_width = bottom_right[0] - top_left[0]
        text_height = bottom_right[1] - top_left[1]
        text_area = text_width * text_height
        total_text_pixels += text_area

        # Desenhar o retângulo na imagem
        cv2.rectangle(image_with_boxes, top_left, bottom_right, (0, 255, 0), 2) # Cor verde, espessura 2

        # Adicionar o texto e a porcentagem da área na imagem
        # Calcular a porcentagem da área do texto em relação à área total da imagem
        percentage_of_image = (text_area / total_image_pixels) * 100
        text_label = f"{text} ({percentage_of_image:.2f}%)"
        cv2.putText(image_with_boxes, text_label, (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2) # Cor azul para o texto

    # Calcular a porcentagem de texto e não texto
    percentage_text = (total_text_pixels / total_image_pixels) * 100
    percentage_non_text = 100 - percentage_text

    # 3. Exibir as imagens e os resultados
    fig, axes = plt.subplots(1, 2, figsize=(18, 9))

    axes[0].imshow(image_np)
    axes[0].set_title("Imagem Original")
    axes[0].axis('off')

    axes[1].imshow(image_with_boxes)
    axes[1].set_title("Texto Detectado (com % de área)")
    axes[1].axis('off')

    plt.tight_layout()
    plt.show()

    # 4. Gerar relatório
    print("\n--- Relatório de Análise de Imagem ---")
    print(f"Porcentagem de Texto na Imagem: {percentage_text:.2f}%")
    print(f"Porcentagem de Não Texto na Imagem: {percentage_non_text:.2f}%")
    print("-------------------------------------")

else:
    print("Nenhuma imagem foi carregada. Por favor, tente novamente.")
