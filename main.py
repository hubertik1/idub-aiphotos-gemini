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
number_of_prompts = 18
uploaded_files = [genai.upload_file(image_path) for image_path in images]

model = genai.GenerativeModel(model_name="gemini-1.5-flash")



results_dict = {image_path: [[] for _ in prompts.prompts] for image_path in images}

total_iterations = number_of_prompts * len(images)
current_iteration = 0

for image_path in images:
    try:
        response = model.generate_content([prompts.prompt, genai.upload_file(image_path)])
        lines = response.text.strip().split('\n')
        for i, line in enumerate(lines):
            try:
                score = float(line.strip())
                results_dict[image_path][i].append(score)
            except ValueError:
                print(f"Warning: Could not parse score '{line}'")
    except google.api_core.exceptions.ResourceExhausted:
        print("Quota exhausted. Skipping image...")
    except google.api_core.exceptions.InvalidArgument as e:
        print(f"Invalid argument: {e}")
    current_iteration += 1
    progress = (current_iteration / total_iterations) * 100
    print(f"Progress: {progress:.2f}%")

with open("wyniki.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    header = ["File"]
    for i in range(number_of_prompts):
        header.append(f"Emotion_{i+1}_Avg")
        header.append(f"Emotion_{i+1}_Std")
    writer.writerow(header)

    for image_path, emotion_scores_list in results_dict.items():
        row = [os.path.basename(image_path)]
        for scores in emotion_scores_list:
            if scores:
                row.append(np.mean(scores))
                row.append(np.std(scores))
            else:
                row.extend(["", ""])
        writer.writerow(row)