import matplotlib.pyplot as plt
from PIL import Image
import ipywidgets as widgets
from IPython.display import display

uploader = widgets.FileUpload(
    accept='image/*',  
    multiple=False
)

display(uploader)

def on_upload_change(change):
    for filename, fileinfo in uploader.value.items():
        img = Image.open(fileinfo['content'])
        plt.imshow(img)
        plt.axis('off')
        plt.title(f'Imagem carregada: {filename}')
        plt.show()

uploader.observe(on_upload_change, names='value')
print("📸 Faça upload de uma imagem usando o botão acima.")
