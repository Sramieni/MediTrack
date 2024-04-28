import tkinter as tk
from tkinter import filedialog, messagebox, Entry
from PIL import Image, ImageTk
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import csv

class DrugDatabase:
    def __init__(self, csv_file):
        self.drugs = self.load_drugs_from_csv(csv_file)

    def load_drugs_from_csv(self, csv_file):
        drugs = {}
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                drugs[row['name'].lower()] = {
                    "name": row['name'],
                    "indication": row['indication'],
                    "dosage": row['dosage'],
                    "side_effects": row['side_effects']
                }
        return drugs

    def get_medication_info(self, medication):
        return self.drugs.get(medication.lower())

class ImageAnalyzer:
    def __init__(self, drug_database):
        self.drug_database = drug_database

    def detect_tablet(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        edges = cv2.Canny(blurred, 30, 150)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_tablets = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:
                x, y, w, h = cv2.boundingRect(contour)
                detected_tablets.append((x, y, w, h))

        detected_medication = None

        if detected_tablets:
            detected_medication = self.match_medication(detected_tablets)

        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title('Detected Tablets')
        ax = plt.gca()
        for tablet in detected_tablets:
            x, y, w, h = tablet
            rect = Rectangle((x, y), w, h, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
        plt.axis('off')
        plt.show()

        return detected_medication, detected_tablets

    def match_medication(self, detected_tablets):
    
        medication_names = list(self.drug_database.drugs.keys())
        detected_medication = np.random.choice(medication_names)
        return detected_medication

def display_medication_info(medication_info, result_label):
    result_label.config(text=f"Name: {medication_info['name']}\n"
                              f"Indication: {medication_info['indication']}\n"
                              f"Dosage: {medication_info['dosage']}\n"
                              f"Side Effects: {medication_info['side_effects']}",
                        font=("Helvetica", 12),
                        padx=10, pady=10,
                        justify=tk.LEFT)

def process_image(image_path, drug_database, image_analyzer, result_label):
    try:
        detected_medication, detected_tablets = image_analyzer.detect_tablet(image_path)
        if detected_medication:
            medication_info = drug_database.get_medication_info(detected_medication)
            if medication_info:
                display_medication_info(medication_info, result_label)
            else:
                result_label.config(text="Medication information not available for the detected medication.")
        else:
            result_label.config(text="No medication detected in the image.")
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while processing the image: {e}")

def manual_medication_process(manual_medication_entry, drug_database, result_label):
    medication = manual_medication_entry.get().lower()
    if medication:
        medication_info = drug_database.get_medication_info(medication)
        if medication_info:
            display_medication_info(medication_info, result_label)
        else:
            result_label.config(text="Medication information not available for the entered medication.")
    else:
        result_label.config(text="Please enter a medication.")

def select_image(image_label, drug_database, image_analyzer, result_label):
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image.thumbnail((400, 400))
        imgtk = ImageTk.PhotoImage(image=image)
        image_label.config(image=imgtk)
        image_label.image = imgtk
        process_image(file_path, drug_database, image_analyzer, result_label)

def create_medications_csv():
    medications = [
    
        {"name": "paracetamol", "indication": "Pain relief, fever reduction", "dosage": "Take 1 to 2 tablets every 4 to 6 hours as needed", "side_effects": "Rare, but may cause allergic reactions or liver damage at high doses"},
        {"name": "fluconazole", "indication": "Fungal infections", "dosage": "Varies by infection type; typically 150 mg as a single dose for vaginal yeast infections", "side_effects": "Headache, dizziness, nausea, stomach pain"},
        {"name": "tamoxifen", "indication": "Breast cancer treatment and prevention", "dosage": "Typically 20 mg once daily", "side_effects": "Hot flashes, risk of blood clots, risk of uterine cancer"}
        # Add more medications as needed
    ]


    csv_file = "medications.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["name", "indication", "dosage", "side_effects"])
        writer.writeheader()
        writer.writerows(medications)

    print("Medications data has been saved to medications.csv")

def main():
    create_medications_csv()

    root = tk.Tk()
    root.title("Medication Detection")
    root.geometry("800x600")

    # Load and display background image
    background_image = Image.open("/Users/seshasai/Downloads/drug detection .jpeg")
    background_image = background_image.resize((800, 600))
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    drug_database = DrugDatabase('medications.csv')
    image_analyzer = ImageAnalyzer(drug_database)

    header_label = tk.Label(root, text="Medication Detection", font=("Helvetica", 18))
    header_label.pack(pady=10)

    image_label = tk.Label(root)
    image_label.pack()

    manual_medication_label = tk.Label(root, text="Enter Medication Manually:")
    manual_medication_label.pack()
    manual_medication_entry = Entry(root)
    manual_medication_entry.pack()

    manual_medication_button = tk.Button(root, text="Process Manual Medication", command=lambda: manual_medication_process(manual_medication_entry, drug_database, result_label))
    manual_medication_button.pack()

    select_button = tk.Button(root, text="Select Image", command=lambda: select_image(image_label, drug_database, image_analyzer, result_label))
    select_button.pack()

    result_label = tk.Label(root, text="", wraplength=400)
    result_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
