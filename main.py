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

results_dict = {
    image_path: {emotion: [] for emotion in prompts.emotions}
    for image_path in images
}

total_iterations =  len(images)* 3
current_iteration = 0

for _ in range(3):
    for image_path in images:
        while True:
            try:
                response = model.generate_content([prompts.prompt[0], genai.upload_file(image_path)])
                print(response.text)
                lines = response.text.strip().split('\n')
                for i, line in enumerate(lines):
                    score = float(line.strip())
                    results_dict[image_path][prompts.emotions[i]].append(score)
                current_iteration += 1
                progress = (current_iteration / total_iterations) * 100
                print(f"Progress: {progress:.2f}%")
                break
            except google.api_core.exceptions.ResourceExhausted:
                print("Quota exhausted. Waiting 30s before retry...")
                time.sleep(30)            
            except google.api_core.exceptions.InvalidArgument as e:
                print(f"Invalid argument: {e}")
                break


with open("wyniki.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    header = ["File"]
    for emotion in prompts.emotions:
        header.append(f"{emotion}_Avg")
        header.append(f"{emotion}_Std")
    writer.writerow(header)

    for image_path, emotion_scores_dict in results_dict.items():
        row = [os.path.basename(image_path)]
        for emotion in prompts.emotions:
            scores = emotion_scores_dict[emotion]
            if scores:
                row.append(round(np.mean(scores),2))
                row.append(round(np.std(scores),2))
            else:
                row.extend(["", ""])
        writer.writerow(row)

print(results_dict)