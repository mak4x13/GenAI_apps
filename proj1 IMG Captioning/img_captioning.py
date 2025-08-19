import requests
from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration


# Load the pretrained processor and model
processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


# Load your image, DONT FORGET TO WRITE YOUR IMAGE NAME
img_path = "new-year-background-736885_1280.jpg"
# convert it into an RGB format
image = Image.open(img_path).convert('RGB')


# You do not need a question for image captioning
text = "the image of"
inputs = processor(images=image, text=text, return_tensors="pt")


# Generate a caption for the image
outputs = model.generate(**inputs, max_length=50)


# Decode the generated tokens to text
caption = processor.decode(outputs[0], skip_special_tokens=True)
# Print the caption
print(caption)