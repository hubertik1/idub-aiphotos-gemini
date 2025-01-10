import PIL.Image
import os
import google.generativeai as genai
import prompts
import time
import google.api_core.exceptions
import numpy as np
import csv

genai.configure(api_key="AIzaSyAcbaTLP7YJlAU4_OOfc2NVvAwVTkL6Yew")
folder_path = "images"
images = [
    os.path.join(folder_path, f)
    for f in os.listdir(folder_path)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

uploaded_files = [genai.upload_file(image_path) for image_path in images]

model = genai.GenerativeModel(model_name="gemini-1.5-flash")



results_dict = {image_path: [] for image_path in images}

total_iterations = len(prompts.prompts) * len(images)
current_iteration = 0

for image_path in images:
    for prompt in prompts.prompts:
        while True:
            try:
                response = model.generate_content([prompt, genai.upload_file(image_path)])
                print(response.text)
                scores = response.text.strip().split()
                print(scores)
                if len(scores) != 1:
                    print(f"Warning: Expected 1 score, got {len(scores)} instead. Skipping...")
                    break
                results_dict[image_path].append(float(scores[0]))
                break
            except google.api_core.exceptions.ResourceExhausted:
                print("Quota exhausted. Retrying after a delay...")
                time.sleep(30)
            except google.api_core.exceptions.InvalidArgument as e:
                print(f"Invalid argument: {e}")
                break
        current_iteration += 1
        progress = (current_iteration / total_iterations) * 100
        print(f"Progress: {progress:.2f}%")

with open("wyniki.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["File", "Average Score", "Std Dev"])
    for image_path, scores in results_dict.items():
        avg_scores = np.mean(scores)
        std_dev_scores = np.std(scores)
        writer.writerow([os.path.basename(image_path), avg_scores, std_dev_scores])