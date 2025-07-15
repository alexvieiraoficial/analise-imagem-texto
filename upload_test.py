import io
import ipywidgets as widgets
from IPython.display import display, Markdown
from PIL import Image, ImageOps, ImageDraw, ImageFont
import pytesseract
import matplotlib.pyplot as plt

uploader = widgets.FileUpload(accept='image/*', multiple=False)
display(uploader)

def calcular_area_texto_filtrada(imagem_pil, conf_min=60):
    gray = ImageOps.grayscale(imagem_pil)
    largura, altura = gray.size
    img_area = largura * altura
    
    # Dados detalhados do OCR
    dados = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    texto_area = 0
    img_com_retangulo = imagem_pil.copy()
    draw = ImageDraw.Draw(img_com_retangulo)
    
    tamanho_fonte = 16
    try:
        fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
    except:
        fonte = ImageFont.load_default()
    
    n_boxes = len(dados['level'])
    for i in range(n_boxes):
        conf = int(dados['conf'][i])
        if conf > conf_min:
            (x, y, w, h) = (dados['left'][i], dados['top'][i], dados['width'][i], dados['height'][i])
            area_caixa = w * h
            texto_area += area_caixa
            
            # Desenhar retângulo vermelho
            draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
            
            perc_caixa = (area_caixa / img_area) * 100
            texto_caixa = f"{perc_caixa:.1f}%"
            
            # Fundo para o texto
            bbox = draw.textbbox((x + w + 3, y), texto_caixa, font=fonte)
            w_text = bbox[2] - bbox[0]
            h_text = bbox[3] - bbox[1]
            draw.rectangle([(x + w + 3, y), (x + w + 3 + w_text, y + h_text)], fill=(0,0,0,150))
            draw.text((x + w + 3, y), texto_caixa, fill="white", font=fonte)
    
    if texto_area > img_area:
        texto_area = img_area
    
    perc_texto_total = (texto_area / img_area) * 100
    perc_imagem = 100 - perc_texto_total
    
    # Texto total no canto superior esquerdo
    texto_total = f"Texto total: {perc_texto_total:.2f}%"
    padding = 10
    bbox_total = draw.textbbox((0,0), texto_total, font=fonte)
    w_total = bbox_total[2] - bbox_total[0]
    h_total = bbox_total[3] - bbox_total[1]
    draw.rectangle([(0,0), (w_total + 2*padding, h_total + 2*padding)], fill=(0,0,0,150))
    draw.text((padding, padding), texto_total, fill="white", font=fonte)
    
    return perc_texto_total, perc_imagem, img_com_retangulo

def on_upload_change(change):
    if uploader.value:
        for nome_arquivo, arquivo in uploader.value.items():
            content = arquivo['content']
            img = Image.open(io.BytesIO(content))
            
            perc_texto_total, perc_imagem, img_com_retangulo = calcular_area_texto_filtrada(img, conf_min=60)
            
            fig, axs = plt.subplots(1, 2, figsize=(14, 7))
            axs[0].imshow(img)
            axs[0].axis('off')
            axs[0].set_title('Imagem Original')
            
            axs[1].imshow(img_com_retangulo)
            axs[1].axis('off')
            axs[1].set_title('Imagem com texto destacado')
            plt.show()
            
            relatorio = (
                f"**Relatório:**\n\n"
                f"- Porcentagem total de texto: {perc_texto_total:.2f}%\n"
                f"- Porcentagem total de imagem (não texto): {perc_imagem:.2f}%"
            )
            display(Markdown(relatorio))

uploader.observe(on_upload_change, names='value')
