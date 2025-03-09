# RemBG GUI

RemBG GUI is a Python-based graphical user interface (GUI) that simplifies the process of removing image backgrounds using the [rembg](https://github.com/danielgatis/rembg) library. Built with Tkinter and Pillow, it provides an intuitive way to process individual images or entire folders while allowing you to preview the results with zoom and pan functionality.

## Features

- **Graphical Interface:** A modern UI built using Tkinter and ttk.
- **Multiple Model Selection:** Choose from various background removal models (e.g. `u2net`, `birefnet-general`, etc.) with the default set to `u2net`.
- **Folder Processing:** Process a batch of images from a selected input folder and save the output in a designated output folder.
- **Preview Functionality:** View both the original and processed images side-by-side with zoom and pan controls.
- **Persistent Configuration:** Saves your input/output folder paths and model choice to a configuration file (`.rembg_gui_config.json`) in your home directory.
- **Optional Cropping:** Option to automatically crop transparent borders from processed images.
- **Device Detection:** Automatically detects whether to use a GPU (if available) or CPU for processing.

## Requirements

- **Python:** >=3.10, <3.14
- **Tkinter:** Typically comes bundled with Python.
- **Pillow:** For image processing.
- **rembg:** For background removal.  
  Additionally, rembg has its own installation requirements:

### rembg Installation

If you already have **onnxruntime** installed, simply run:
```sh
pip install rembg            # for library
pip install "rembg[cli]"     # for library + CLI
```

Otherwise, install rembg with explicit CPU/GPU support.

**CPU support:**
```sh
pip install rembg[cpu]       # for library
pip install "rembg[cpu,cli]" # for library + CLI
```

**GPU support:**
1. Check if your system supports **onnxruntime-gpu** by visiting [onnxruntime.ai](https://onnxruntime.ai) and reviewing the installation matrix.
2. If supported, install with:
   ```sh
   pip install "rembg[gpu]"       # for library
   pip install "rembg[gpu,cli]"   # for library + CLI
   ```
   *Note:* Nvidia GPUs may require additional components such as `onnxruntime-gpu`, CUDA, and cudnn-devel. If you cannot install CUDA or cudnn-devel, use the CPU version with onnxruntime instead.

## Installation

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/your-username/RemBG-GUI.git
   cd RemBG-GUI
   ```

2. **Create and Activate a Virtual Environment (Optional):**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install the Dependencies:**
   If a `requirements.txt` file is provided:
   ```sh
   pip install -r requirements.txt
   ```
   Otherwise, install the dependencies manually:
   ```sh
   pip install pillow rembg
   ```

## Usage

1. **Launch the Application:**
   ```sh
   python rembg_gui.py
   ```
   *(Replace `rembg_gui.py` with the actual filename if different.)*

2. **Using the Interface:**
   - **Select Input Folder:** Click the "Select Input Folder" button to choose the folder containing your images.
   - **Select Output Folder:** Click the "Select Output Folder" button to specify where the processed images should be saved.
   - **Model Selection:** Use the dropdown menu to select a background removal model.
   - **Crop Transparent Borders:** Tick the "Crop Transparent Borders" checkbox if you wish to remove excess transparent space from the output.
   - **Process Folder:** Click "Process Folder" to start processing. The progress bar will indicate the progress, and you can preview images as they’re processed.
   - **Preview Controls:** Use your mouse wheel to zoom in/out and click & drag to pan the preview images.

## Pre-built Executable

For users who prefer a hassle-free experience, a pre-built executable version of RemBG GUI is available. This Windows executable requires no additional installations or dependencies—simply download and run.

**Download the Executable:**

You can download the latest version from [Google Drive]([https://drive.google.com/your-exe-file-link](https://drive.google.com/file/d/1t9hXASicu6Uf8QWGvYjD_5wRSfxyig6_/view?usp=drive_link).  
*(Replace the URL above with your actual Google Drive link.)*

**Usage:**

- No installation is required.
- Simply double-click the executable file to launch RemBG GUI.
- Enjoy background removal without needing to set up a Python environment.

*Note:* This executable is only available for Windows. For users on other operating systems, please compile from source using the instructions provided above.


## Building an Executable

To turn your Python script into an executable file (for example, on Windows), you can use [PyInstaller](https://pyinstaller.org/).

1. **Install PyInstaller:**
   ```sh
   pip install pyinstaller
   ```

2. **Build the Executable:**
   Run PyInstaller with the following command:
   ```sh
   pyinstaller --onefile --noconsole rembg_gui.py
   ```
   *(Replace `rembg_gui.py` with your actual script filename.)*

3. **Locate the Executable:**
   After the build completes, your executable will be located in the `dist/` folder.

## Configuration

Your settings (input folder, output folder, and selected model) are saved in a JSON file located at:
```sh
~/.rembg_gui_config.json
```
This allows the application to remember your preferences between sessions.

## Troubleshooting

- **Large File Handling:** If you experience issues with large files (especially when using Git LFS), refer to the repository documentation or GitHub's guidelines on [Git LFS](https://git-lfs.github.com/).
- **Dependency Issues:** Ensure that all required Python libraries are installed and up-to-date.
- **Executable Issues:** If you encounter problems when building an executable, check the PyInstaller documentation or run the script directly to isolate the issue.

## Contributing

Contributions are welcome! If you find a bug or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Happy background removing! If you have any questions or need further support, please feel free to open an issue on the repository.
