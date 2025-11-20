```python
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os

# Define the letters to recognize
letters = 'abcdefghijklmnopqrstuvwxyz'

# Load a pre-trained model
model = models.resnet18(pretrained=True)
model.eval()

# Define the transformation for input images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def predict_letter(image_path):
    # Load and preprocess the image
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)

    # Perform inference
    with torch.no_grad():
        outputs = model(image)
    
    # Get the predicted class
    _, predicted = torch.max(outputs, 1)
    return letters[predicted.item() % len(letters)]  # Modulo to fit within letters

def main(input_folder, output_file):
    results = {}
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            letter = predict_letter(os.path.join(input_folder, filename))
            results[filename] = letter
    
    # Save results to a text file
    with open(output_file, 'w') as f:
        for filename, letter in results.items():
            f.write(f"{filename}: {letter}\n")

if __name__ == "__main__":
    input_folder = 'path/to/your/images'  # Change this to your images folder
    output_file = 'ocr_results.txt'
    main(input_folder, output_file)