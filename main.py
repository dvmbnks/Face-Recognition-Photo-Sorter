import cv2
import face_recognition
import os
import shutil
from tkinter import Tk, filedialog, Button, Label, messagebox, Frame, Toplevel
from PIL import Image, ImageTk
import threading

# Initialize Tkinter
root = Tk()
root.title("Face Recognition Photo Sorter")
root.geometry("820x310")
root.resizable(False, False)

# Global variables
image_encoding = None
photos_folder = None
output_folder = None
cap = cv2.VideoCapture(0)

# Function to update frame
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img.thumbnail((300, 250), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
    camera_label.after(10, update_frame)

# Function to capture photo
def capture_photo():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('captured_photo.jpg', frame)
        global image_encoding
        image = face_recognition.load_image_file('captured_photo.jpg')
        encodings = face_recognition.face_encodings(image)
        if encodings:
            image_encoding = encodings[0]
            ref_image_label.config(text="Reference Image Selected!")
            display_image('captured_photo.jpg')
        else:
            messagebox.showwarning("No Face Detected", "No face detected in the captured photo.")

# Function to display the captured image
def display_image(file_path):
    try:
        img = Image.open(file_path)
        img.thumbnail((300, 250))  # Maintain aspect ratio
        imgtk = ImageTk.PhotoImage(image=img)
        reference_image_label.imgtk = imgtk
        reference_image_label.configure(image=imgtk)
    except Exception as e:
        messagebox.showerror("Error", "Failed to load image: " + str(e))

# Modify select_image function
def select_image():
    file_path = filedialog.askopenfilename(title="Select Reference Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        global image_encoding
        image = face_recognition.load_image_file(file_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            image_encoding = encodings[0]
            ref_image_label.config(text="Reference Image Selected!")
            display_image(file_path)
        else:
            messagebox.showwarning("No Face Detected", "No face detected in the selected image.")
    else:
        ref_image_label.config(text="No Image Selected")

# Function to select input folder
def select_input_folder():
    folder_path = filedialog.askdirectory(title="Select Photos Folder")
    if folder_path:
        global photos_folder
        photos_folder = folder_path
        folder_label.config(text="Photos Folder Selected!")
    else:
        folder_label.config(text="No Folder Selected")

# Function to select output folder
def select_output_folder():
    output_path = filedialog.askdirectory(title="Select Output Folder")
    if output_path:
        global output_folder
        output_folder = output_path
        output_label.config(text="Output Folder Selected!")
    else:
        output_label.config(text="No Output Folder Selected")

# Function to scan and sort photos
def scan():
    # Create a loading window
    root.withdraw()
    loading_window = Toplevel(root)
    loading_window.title("Please Wait")
    loading_window.geometry("200x100")
    loading_label = Label(loading_window, text="Scanning and Sorting Photos...\nPlease Wait...", padx=20, pady=20)
    loading_label.pack()

    def perform_scan():
        for filename in os.listdir(photos_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image_path = os.path.join(photos_folder, filename)
                test_image = face_recognition.load_image_file(test_image_path)
                encodings = face_recognition.face_encodings(test_image)
                if encodings:
                    face_encoding = encodings[0]
                    match = face_recognition.compare_faces([image_encoding], face_encoding)
                    if match[0]:
                        shutil.copy(test_image_path, os.path.join(output_folder, filename))

        loading_window.destroy()
        root.deiconify() 
        messagebox.showinfo("Process Completed", "Matching images have been sorted!")

    # Start the scanning process in a separate thread
    threading.Thread(target=perform_scan, daemon=True).start()

# Create GUI components
camera_label = Label(root)
camera_label.grid(row=0, column=2, padx=10, pady=10)

# Reference image display
reference_image_label = Label(root)
reference_image_label.grid(row=0, column=3, padx=10, pady=10)

# Create a frame for buttons and labels
button_frame = Frame(root)
button_frame.grid(row=0, column=1, padx=10, pady=10)

# Create buttons in the button frame
capture_button = Button(button_frame, text="Capture Photo", command=capture_photo, bg='lightblue', width=20)
capture_button.pack(pady=5)

ref_image_button = Button(button_frame, text="Select Reference Image", command=select_image, bg='lightgreen', width=20)
ref_image_button.pack(pady=5)

folder_button = Button(button_frame, text="Select Input Folder", command=select_input_folder, bg='lightcoral', width=20)
folder_button.pack(pady=5)

output_button = Button(button_frame, text="Select Output Folder", command=select_output_folder, bg='lightpink', width=20)
output_button.pack(pady=5)

scan_button = Button(button_frame, text="Scan and Sort Photos", command=scan, bg='lightgray', width=20)
scan_button.pack(pady=5)

# Labels for feedback
ref_image_label = Label(button_frame, text="No Image Selected")
ref_image_label.pack()

folder_label = Label(button_frame, text="No Folder Selected")
folder_label.pack()

output_label = Label(button_frame, text="No Output Folder Selected")
output_label.pack()

update_frame()
root.mainloop()

# Release the capture when done
cap.release()
cv2.destroyAllWindows()
