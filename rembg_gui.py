import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from rembg import remove, new_session
import io
import os
import json

# Attempt to import model_zoo from rembg for model file info
try:
    from rembg import model_zoo
except ImportError:
    model_zoo = None

# Path to store persistent configuration
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".rembg_gui_config.json")

# Create the main application window
root = tk.Tk()
root.title("RemBG GUI")

# Let the user resize, but set a minimum size to avoid content being cut off
root.minsize(1300, 1120)
root.geometry("1300x1120")

# Use ttk style for a modern look
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TFrame", background="#F0F0F0")
style.configure("Warning.TLabel", foreground="red", font=("Segoe UI", 10, "bold"))
style.configure("Instruction.TLabel", font=("Segoe UI", 10, "italic"))

# Global variables for folders, images, zoom/pan, and preview index
input_folder = None
output_folder = None
current_output_image = None
preview_original_full = None
preview_processed_full = None
zoom_factor = 1.0
original_view_center = None
processed_view_center = None
pan_start = None
image_files = []
preview_index = 0
PREVIEW_WIDTH = 600
PREVIEW_HEIGHT = 600
cancel_processing = False

selected_model = tk.StringVar(root)

# Define available models with "u2net" at the top
available_models = [
    "u2net",
    "birefnet-general",
    "birefnet-general-lite",
    "birefnet-portrait",
    "birefnet-dis",
    "birefnet-hrsod",
    "birefnet-cod",
    "birefnet-massive",
    "isnet-anime",
    "isnet-general-use",
    "sam",
    "silueta",
    "u2net_cloth_seg",
    "u2net_custom",
    "u2net_human_seg",
    "u2netp",
    "bria-rmbg"
]
DEFAULT_MODEL = "u2net"
selected_model.set(DEFAULT_MODEL)

# ------------------------
# Persistent Memory
# ------------------------
def load_config():
    global input_folder, output_folder, selected_model
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            input_folder = config.get("input_folder", None)
            output_folder = config.get("output_folder", None)
            model = config.get("selected_model", DEFAULT_MODEL)
            selected_model.set(model)
        except Exception as e:
            print(f"Error loading config: {e}")

def save_config():
    config = {
        "input_folder": input_folder,
        "output_folder": output_folder,
        "selected_model": selected_model.get()
    }
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")

load_config()

# ------------------------
# Model Info
# ------------------------
def update_model_info(*args):
    model = selected_model.get()
    size_text = "Unknown"
    if model_zoo is not None:
        try:
            model_path = model_zoo.get_model_path(model)
            if os.path.exists(model_path):
                size_bytes = os.path.getsize(model_path)
                size_mb = size_bytes / (1024 * 1024)
                size_text = f"{size_mb:.2f} MB"
            else:
                size_text = "File not found"
        except Exception as e:
            size_text = f"Error: {e}"
    else:
        model_path = os.path.join(os.path.expanduser("~"), ".u2net", f"{model}.onnx")
        if os.path.exists(model_path):
            size_bytes = os.path.getsize(model_path)
            size_mb = size_bytes / (1024 * 1024)
            size_text = f"{size_mb:.2f} MB"
        else:
            size_text = "File not found (model_zoo not available)"
    model_info_label.config(text=f"Model: {model} | File Size: {size_text}")

# ------------------------
# Zoom, Pan, Preview
# ------------------------
def render_previews():
    global preview_original_full, original_view_center, preview_processed_full, processed_view_center, zoom_factor
    W, H = PREVIEW_WIDTH, PREVIEW_HEIGHT
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.ANTIALIAS

    # Original
    ow, oh = preview_original_full.size
    crop_w = W / zoom_factor
    crop_h = H / zoom_factor
    cx, cy = original_view_center
    left = max(0, min(cx - crop_w/2, ow - crop_w))
    top = max(0, min(cy - crop_h/2, oh - crop_h))
    box = (left, top, left + crop_w, top + crop_h)
    cropped_orig = preview_original_full.crop(box)
    resized_orig = cropped_orig.resize((W, H), resample=resample_filter)
    img_original = ImageTk.PhotoImage(resized_orig)
    preview_original_label.config(image=img_original)
    preview_original_label.image = img_original

    # Processed
    pw, ph = preview_processed_full.size
    crop_w = W / zoom_factor
    crop_h = H / zoom_factor
    cx, cy = processed_view_center
    left = max(0, min(cx - crop_w/2, pw - crop_w))
    top = max(0, min(cy - crop_h/2, ph - crop_h))
    box = (left, top, left + crop_w, top + crop_h)
    cropped_proc = preview_processed_full.crop(box)
    resized_proc = cropped_proc.resize((W, H), resample=resample_filter)
    img_processed = ImageTk.PhotoImage(resized_proc)
    preview_processed_label.config(image=img_processed)
    preview_processed_label.image = img_processed

def on_zoom(event):
    global zoom_factor, original_view_center, processed_view_center
    W, H = PREVIEW_WIDTH, PREVIEW_HEIGHT
    factor = 1.1 if event.delta > 0 else 0.9
    old_zoom = zoom_factor
    new_zoom = zoom_factor * factor
    rx = event.x / W
    ry = event.y / H
    old_crop_w = W / old_zoom
    old_crop_h = H / old_zoom
    new_crop_w = W / new_zoom
    new_crop_h = H / new_zoom
    dx = (old_crop_w - new_crop_w) * (rx - 0.5)
    dy = (old_crop_h - new_crop_h) * (ry - 0.5)
    ox, oy = original_view_center
    original_view_center = (ox + dx, oy + dy)
    cx, cy = processed_view_center
    processed_view_center = (cx + dx, cy + dy)
    zoom_factor = new_zoom
    render_previews()

def on_pan_start(event):
    global pan_start
    pan_start = (event.x, event.y)

def on_pan_move(event):
    global pan_start, original_view_center, processed_view_center
    if pan_start is None:
        return
    dx = event.x - pan_start[0]
    dy = event.y - pan_start[1]
    ox, oy = original_view_center
    original_view_center = (ox - dx / zoom_factor, oy - dy / zoom_factor)
    cx, cy = processed_view_center
    processed_view_center = (cx - dx / zoom_factor, cy - dy / zoom_factor)
    pan_start = (event.x, event.y)
    render_previews()

def preview_image(index):
    global preview_original_full, preview_processed_full, original_view_center, processed_view_center
    global zoom_factor, image_files, preview_index
    if not image_files:
        return
    preview_index = index % len(image_files)
    image_path = os.path.join(input_folder, image_files[preview_index])
    try:
        original_image = Image.open(image_path).convert("RGB")
        preview_original_full = original_image.copy()
        with open(image_path, 'rb') as infile:
            input_data = infile.read()
        session = new_session(model_name=selected_model.get())
        output_data = remove(input_data, session=session)
        processed_image = Image.open(io.BytesIO(output_data)).convert("RGBA")
        if crop_toggle.get():
            alpha = processed_image.split()[-1]
            bbox = alpha.getbbox()
            if bbox:
                processed_image = processed_image.crop(bbox)
        preview_processed_full = processed_image.copy()
        original_view_center = (preview_original_full.width / 2, preview_original_full.height / 2)
        processed_view_center = (preview_processed_full.width / 2, preview_processed_full.height / 2)
        initial_zoom = min(PREVIEW_WIDTH / preview_original_full.width,
                           PREVIEW_HEIGHT / preview_original_full.height)
        zoom_factor = initial_zoom
        render_previews()
    except Exception as e:
        print(f"Error in preview: {e}")

def preview_first_image():
    global image_files, preview_index
    supported_extensions = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
    image_files = [f for f in os.listdir(input_folder)
                   if os.path.isfile(os.path.join(input_folder, f)) and f.lower().endswith(supported_extensions)]
    if not image_files:
        messagebox.showinfo("No Images", "No supported image files found in the selected input folder.")
        return
    preview_index = 0
    preview_image(preview_index)

def select_input_folder():
    global input_folder
    folder = filedialog.askdirectory(title="Select Input Folder")
    if folder:
        input_folder = folder
        input_folder_label.config(text=f"Input Folder: {input_folder}")
        save_config()
        preview_first_image()

def select_output_folder():
    global output_folder
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_folder = folder
        output_folder_label.config(text=f"Output Folder: {output_folder}")
        save_config()

def get_processing_device():
    try:
        import torch
        return "GPU" if torch.cuda.is_available() else "CPU"
    except ImportError:
        return "CPU"

def process_folder():
    global current_output_image, cancel_processing
    if not input_folder or not output_folder:
        messagebox.showwarning("Folder Not Selected", "Please select both input and output folders first.")
        return

    cancel_processing = False
    device = get_processing_device()
    device_label.config(text=f"Processing Device: {device}")
    if not image_files:
        preview_first_image()
    total_files = len(image_files)
    if total_files == 0:
        messagebox.showinfo("No Images", "No supported image files found in the selected input folder.")
        return

    progress_bar['maximum'] = total_files
    progress_bar['value'] = 0
    processed_count = 0
    for i, filename in enumerate(image_files):
        if cancel_processing:
            messagebox.showinfo("Processing Cancelled", f"Processing cancelled after {processed_count} images.")
            break
        input_path = os.path.join(input_folder, filename)
        try:
            with open(input_path, 'rb') as infile:
                input_data = infile.read()
            session = new_session(model_name=selected_model.get())
            output_data = remove(input_data, session=session)
            output_image = Image.open(io.BytesIO(output_data)).convert("RGBA")
            if crop_toggle.get():
                alpha = output_image.split()[-1]
                bbox = alpha.getbbox()
                if bbox:
                    output_image = output_image.crop(bbox)
            output_filename = os.path.splitext(filename)[0] + "_no_bg.png"
            output_path = os.path.join(output_folder, output_filename)
            output_image.save(output_path)
            processed_count += 1
            current_output_image = output_image
            preview_image(i)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
        finally:
            progress_bar['value'] += 1
            root.update()
    else:
        messagebox.showinfo("Folder Processing", f"Processed {processed_count} image(s).")

def cancel_processing_flag():
    global cancel_processing
    cancel_processing = True

# --- GUI Layout ---
folder_frame = ttk.Frame(root)
folder_frame.pack(pady=10)

input_button = ttk.Button(folder_frame, text="Select Input Folder", command=select_input_folder)
input_button.grid(row=0, column=0, padx=5)
output_button = ttk.Button(folder_frame, text="Select Output Folder", command=select_output_folder)
output_button.grid(row=0, column=1, padx=5)

input_folder_label = ttk.Label(root, text=f"Input Folder: {input_folder or 'Not selected'}")
input_folder_label.pack()
output_folder_label = ttk.Label(root, text=f"Output Folder: {output_folder or 'Not selected'}")
output_folder_label.pack()

# Updated OptionMenu with the default model set explicitly
model_dropdown = ttk.OptionMenu(root, selected_model, selected_model.get(), *available_models, command=lambda _: update_model_info())
model_dropdown.pack(pady=5)

warning_label = ttk.Label(root, text="Warning: Changing models may download additional large files.", style="Warning.TLabel")
warning_label.pack(pady=2)

default_model_label = ttk.Label(root, text=f"Default Model (preinstalled): {DEFAULT_MODEL}")
default_model_label.pack(pady=2)

model_info_label = ttk.Label(root, text="")
model_info_label.pack(pady=5)
update_model_info()

crop_toggle = tk.BooleanVar()
crop_check = ttk.Checkbutton(root, text="Crop Transparent Borders", variable=crop_toggle)
crop_check.pack(pady=5)

device_label = ttk.Label(root, text="Processing Device: Unknown")
device_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=10)

process_frame = ttk.Frame(root)
process_frame.pack(pady=5)

process_button = ttk.Button(process_frame, text="Process Folder", command=process_folder)
process_button.grid(row=0, column=0, padx=5)

cancel_button = ttk.Button(process_frame, text="Cancel Processing", command=cancel_processing_flag)
cancel_button.grid(row=0, column=1, padx=5)

# --- Preview Section ---
preview_frame = ttk.Frame(root, width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT)
preview_frame.pack(pady=10)
preview_frame.pack_propagate(False)

preview_original_label = ttk.Label(preview_frame)
preview_original_label.grid(row=0, column=0, padx=5)

preview_processed_label = ttk.Label(preview_frame)
preview_processed_label.grid(row=0, column=1, padx=5)

instruction_label = ttk.Label(root, text="Use mouse wheel to zoom and click & drag to pan the preview images.", style="Instruction.TLabel")
instruction_label.pack(pady=5)

nav_frame = ttk.Frame(root)
nav_frame.pack(pady=5)

btn_back10 = ttk.Button(nav_frame, text="<< Prev 10", command=lambda: preview_image(preview_index - 10))
btn_back10.grid(row=0, column=0, padx=5)

sub_nav_frame = ttk.Frame(nav_frame)
sub_nav_frame.grid(row=0, column=1, padx=5)

btn_back = ttk.Button(sub_nav_frame, text="< Prev", command=lambda: preview_image(preview_index - 1))
btn_back.pack(side="top", pady=2)

btn_next = ttk.Button(sub_nav_frame, text="Next >", command=lambda: preview_image(preview_index + 1))
btn_next.pack(side="top", pady=2)

btn_next10 = ttk.Button(nav_frame, text="Next 10 >>", command=lambda: preview_image(preview_index + 10))
btn_next10.grid(row=0, column=2, padx=5)

for widget in (preview_frame, preview_original_label, preview_processed_label):
    widget.bind("<Enter>", lambda e: e.widget.focus_set())
    widget.bind("<MouseWheel>", on_zoom)
    widget.bind("<ButtonPress-1>", on_pan_start)
    widget.bind("<B1-Motion>", on_pan_move)

def on_close():
    save_config()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

if input_folder is not None:
    preview_first_image()

root.mainloop()
