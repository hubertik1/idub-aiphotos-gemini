import PIL.Image
import os
import google.generativeai as genai
import openpyxl

genai.configure(api_key="AIzaSyAcbaTLP7YJlAU4_OOfc2NVvAwVTkL6Yew")
folder_path = "images"
images = [
    os.path.join(folder_path, f)
    for f in os.listdir(folder_path)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash")



wb = openpyxl.Workbook()
ws = wb.active
ws.append(["file name", "radosc", "zlosc", "smutek", "strach"])

for image_path in images:
    sample_file = PIL.Image.open(image_path)
    response = model.generate_content([prompt, sample_file])
    scores = response.text.strip().split()
    ws.append([os.path.basename(image_path)] + scores)

wb.save("wyniki.xlsx")
    




