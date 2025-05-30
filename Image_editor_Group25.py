# Course Name : Software Now
# Course Code : HIT137
# GROUP NAME : CAS/DAN GROUP-25
# GROUP MEMBERS:
#Kushal Mahajan - Student S383488
#Darshan Veerabhadrappa Meti - Student S388441
#Joanna Rivera - Student S392556
#Anmol Singh - Student S385881

# Importing Required Libraries
from tkinter import *
from tkinter import filedialog, ttk
import cv2
from PIL import ImageTk, Image

class ImageEditor:
    def __init__(self, root):
        # Initialize the main application window and set up variables
        self.root = root
        self.root.title("Python Image Editor - CAS/DAN Group 25")
        self.root.geometry("1000x800")

        # Image storage
        self.original_image = None  # Stores the original loaded image
        self.modified_image = None  # Stores the current edited version
        self.filename = None  # Path to the current image file

        # Undo/Redo functionality
        self.undo_stack = []  # Stores previous states for undo
        self.redo_stack = []  # Stores undone states for redo

        # Crop functionality variables
        self.crop_mode = False  # Flag for when we're in crop mode
        self.crop_start_x = None  # Starting X coordinate for crop
        self.crop_start_y = None  # Starting Y coordinate for crop
        self.crop_rectangle = None  # ID of the crop rectangle on canvas
        self.current_image_width = 0  # Original image width before preview scaling
        self.current_image_height = 0  # Original image height before preview scaling

        self.setup_ui()

    def setup_ui(self):
        # Create and arrange all the user interface elements
        # Create main containers
        self.create_image_canvases()
        self.create_control_panel()
        self.create_instructions_panel()
        self.setup_keyboard_shortcuts()

    def create_image_canvases(self):
        """Create the left and right image display canvases"""
        self.canvas_frame = Frame(self.root)
        self.canvas_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Left canvas shows original image
        self.canvas_original = Canvas(self.canvas_frame, width=350, height=350, 
                                    bg="lightblue", highlightthickness=1, 
                                    highlightbackground="gray")
        self.canvas_original.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.canvas_original.create_text(175, 175, text="Original Image", 
                                       fill="darkblue", font=("Arial", 14))

        # Right canvas shows modified image
        self.canvas_modified = Canvas(self.canvas_frame, width=350, height=350, 
                                    bg="#D2C4FB", highlightthickness=1, 
                                    highlightbackground="gray")
        self.canvas_modified.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.canvas_modified.create_text(175, 175, text="Edited Image", 
                                       fill="darkblue", font=("Arial", 14))

    def create_control_panel(self):
        """Create the panel with all control buttons and sliders"""
        self.button_frame = Frame(self.root, padx=20, pady=10, bg="white")
        self.button_frame.pack(fill=X)

        # Create buttons with consistent styling
        button_style = {'padx': 8, 'pady': 5, 'width': 10}
        
        Button(self.button_frame, text="Select Image", 
              command=self.select_image, **button_style).pack(side=LEFT, padx=5)
        
        Button(self.button_frame, text="Crop", 
              command=self.activate_crop_mode, **button_style).pack(side=LEFT, padx=5)
        
        Button(self.button_frame, text="Grayscale", 
              command=self.convert_to_grayscale, **button_style).pack(side=LEFT, padx=5)
        
        Button(self.button_frame, text="Rotate", 
              command=self.rotate_image, **button_style).pack(side=LEFT, padx=5)
        
        Button(self.button_frame, text="Undo", 
              command=self.undo_action, **button_style).pack(side=LEFT, padx=5)
        
        Button(self.button_frame, text="Redo", 
              command=self.redo_action, **button_style).pack(side=LEFT, padx=5)
        
        # Zoom slider with better labeling
        self.zoom_slider = Scale(self.button_frame, label="Zoom Level", 
                               from_=25, to=125, orient=HORIZONTAL, 
                               length=300, command=self.adjust_zoom)
        self.zoom_slider.set(75)
        self.zoom_slider.pack(side=LEFT, padx=10)
        
        Button(self.button_frame, text="Save Image", 
              command=self.save_image, **button_style).pack(side=LEFT, padx=5)

    def create_instructions_panel(self):
        """Create the panel with usage instructions"""
        instructions = Label(self.root, text=
            '''Instructions:
            1. Click "Select Image" or press Ctrl+O to choose an image
            2. Use the tools to edit your image:
               - Crop (Ctrl+C): Click and drag to select area to keep
               - Grayscale (Ctrl+G): Convert to black and white
               - Rotate (Ctrl+R): Rotate 90 degrees clockwise
            3. Adjust zoom with the slider
            4. Use Undo (Ctrl+Z) and Redo (Ctrl+Y) as needed
            5. Save your work with Ctrl+S or the Save button''',
            justify=LEFT, padx=10, pady=10, font=("Arial", 10), bg="#f0f0f0")
        instructions.pack(fill=X, pady=10)

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for common actions"""
        self.root.bind("<Control-o>", lambda e: self.select_image())
        self.root.bind("<Control-c>", lambda e: self.activate_crop_mode())
        self.root.bind("<Control-g>", lambda e: self.convert_to_grayscale())
        self.root.bind("<Control-r>", lambda e: self.rotate_image())
        self.root.bind("<Control-z>", lambda e: self.undo_action())
        self.root.bind("<Control-y>", lambda e: self.redo_action())
        self.root.bind("<Control-s>", lambda e: self.save_image())

    def select_image(self):
        """Open a file dialog to select an image file"""
        filetypes = [
            ("Image Files", "*.png *.jpg *.jpeg"),
            ("All Files", "*.*")
        ]
        
        self.filename = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=filetypes
        )
        
        if not self.filename:
            return  # User cancelled the dialog

        try:
            # Read the image using OpenCV
            self.original_image = cv2.imread(self.filename)
            if self.original_image is None:
                raise ValueError("Could not read the image file")
                
            # Reset editing state
            self.modified_image = None
            self.undo_stack.clear()
            self.redo_stack.clear()
            
            # Update the display
            self.display_images()
            print(f"Successfully loaded: {self.filename}")
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.show_error_message("Could not load the selected image")

    def display_images(self):
        # Displays both original and modified images on the canvases
        if self.original_image is None:
            return

        # Get current zoom level (75% by default)
        zoom_factor = self.zoom_slider.get() / 100

        # Display original image
        self.display_single_image(
            self.original_image, 
            self.canvas_original, 
            "original", 
            zoom_factor
        )

        # Display modified image (or original if no modifications)
        image_to_show = self.modified_image if self.modified_image is not None else self.original_image
        self.display_single_image(
            image_to_show, 
            self.canvas_modified, 
            "modified", 
            zoom_factor
        )

    def display_single_image(self, image, canvas, image_type, zoom_factor):
        # Convert from BGR (OpenCV) to RGB (PIL/Tkinter)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_height, original_width = image_rgb.shape[:2]

        # Calculate dimensions to fit in canvas while maintaining aspect ratio
        canvas_width = 350  # Initial canvas size
        canvas_height = 350
        
        # Calculate scale to fit canvas, then apply zoom
        scale = min(canvas_width/original_width, canvas_height/original_height, 1)
        scale *= zoom_factor
        
        # Calculate final display dimensions
        display_width = int(original_width * scale)
        display_height = int(original_height * scale)
        
        # Resize the image
        resized_image = cv2.resize(image_rgb, (display_width, display_height), 
                                interpolation=cv2.INTER_AREA)
        
        # Convert to PhotoImage and display
        tk_image = ImageTk.PhotoImage(image=Image.fromarray(resized_image))
        
        # Update the canvas
        canvas.config(width=display_width, height=display_height)
        canvas.delete("all")
        canvas.create_image(display_width//2, display_height//2, image=tk_image)
        
        # Keep reference to prevent garbage collection
        if image_type == "original":
            self.tk_original_image = tk_image
        else:
            self.tk_modified_image = tk_image
            
        # Store dimensions for crop calculations
        if image_type == "modified":
            self.preview_dimensions = (display_width, display_height)
            self.current_image_width = original_width
            self.current_image_height = original_height

    def activate_crop_mode(self):
        """Enable crop mode and set up event bindings"""
        if not self.has_image_loaded():
            self.show_error_message("Please load an image first")
            return
            
        self.crop_mode = True
        self.canvas_modified.config(cursor="cross")
        
        # Bind mouse events for crop selection
        self.canvas_modified.bind("<ButtonPress-1>", self.start_crop_selection)
        self.canvas_modified.bind("<B1-Motion>", self.update_crop_selection)
        self.canvas_modified.bind("<ButtonRelease-1>", self.finalize_crop)
        
        print("Crop mode activated - click and drag on the right image to select area")

    def start_crop_selection(self, event):
        """Record starting position when user clicks for crop"""
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        
        # Remove any existing crop rectangle
        if self.crop_rectangle:
            self.canvas_modified.delete(self.crop_rectangle)
            self.crop_rectangle = None

    def update_crop_selection(self, event):   # Update the crop rectangle as user drags mouse
        if not self.crop_mode:
            return
            
        current_x, current_y = event.x, event.y
        
        # Create or update the rectangle
        if self.crop_rectangle is None:
            self.crop_rectangle = self.canvas_modified.create_rectangle(
                self.crop_start_x, self.crop_start_y,
                current_x, current_y,
                outline="red", width=2, dash=(5,5) # Dotted line style for better visibility
            )
        else:
            self.canvas_modified.coords(
                self.crop_rectangle,
                self.crop_start_x, self.crop_start_y,
                current_x, current_y
            )

    def finalize_crop(self, event):
        """Complete the crop operation when user releases mouse"""
        if not self.crop_mode:
            return
            
        # Get final coordinates
        crop_end_x, crop_end_y = event.x, event.y
        
        # Clean up event bindings
        self.canvas_modified.unbind("<ButtonPress-1>")
        self.canvas_modified.unbind("<B1-Motion>")
        self.canvas_modified.unbind("<ButtonRelease-1>")
        self.crop_mode = False
        self.canvas_modified.config(cursor="")
        
        # Calculate the selected area
        x1 = min(self.crop_start_x, crop_end_x)
        y1 = min(self.crop_start_y, crop_end_y)
        x2 = max(self.crop_start_x, crop_end_x)
        y2 = max(self.crop_start_y, crop_end_y)
        
        # Check for minimum size
        if (x2 - x1) < 10 or (y2 - y1) < 10:
            print("Selection too small - please select a larger area")
            if self.crop_rectangle:
                self.canvas_modified.delete(self.crop_rectangle)
                self.crop_rectangle = None
            return
            
        # Convert preview coordinates to original image coordinates
        preview_width, preview_height = self.preview_dimensions
        width_ratio = self.current_image_width / preview_width
        height_ratio = self.current_image_height / preview_height
        
        x1_image = int(x1 * width_ratio)
        y1_image = int(y1 * height_ratio)
        x2_image = int(x2 * width_ratio)
        y2_image = int(y2 * height_ratio)
        
        # Ensure coordinates are within image bounds
        x1_image = max(0, x1_image)
        y1_image = max(0, y1_image)
        x2_image = min(self.current_image_width, x2_image)
        y2_image = min(self.current_image_height, y2_image)
        
        # Get the current image to crop
        image_to_crop = self.modified_image if self.modified_image is not None else self.original_image
        
        # Save current state for undo
        self.save_current_state()
        
        try:
            # Perform the crop
            self.modified_image = image_to_crop[y1_image:y2_image, x1_image:x2_image].copy()
            print("Image cropped successfully!")
            
            # Update display
            self.display_images()
            
        except Exception as e:
            print(f"Error during cropping: {e}")
            self.show_error_message("Failed to crop image")
            
        finally:
            # Clean up the crop rectangle
            if self.crop_rectangle:
                self.canvas_modified.delete(self.crop_rectangle)
                self.crop_rectangle = None

    def convert_to_grayscale(self):
        """Convert the current image to grayscale"""
        if not self.has_image_loaded():
            self.show_error_message("Please load an image first")
            return
            
        # Get current image (modified if available, otherwise original)
        current_image = self.modified_image if self.modified_image is not None else self.original_image
        
        # Save current state for undo
        self.save_current_state()
        
        try:
            # Convert to grayscale and back to BGR for consistency
            gray_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
            self.modified_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
            
            # Update display
            self.display_images()
            print("Image converted to grayscale successfully!")
            
        except Exception as e:
            print(f"Error converting to grayscale: {e}")
            self.show_error_message("Failed to convert image to grayscale")

    def rotate_image(self):
        """Rotate the current image 90 degrees clockwise"""
        if not self.has_image_loaded():
            self.show_error_message("Please load an image first")
            return
            
        # Get current image
        current_image = self.modified_image if self.modified_image is not None else self.original_image
        
        # Save current state for undo
        self.save_current_state()
        
        try:
            # Perform rotation
            self.modified_image = cv2.rotate(current_image, cv2.ROTATE_90_CLOCKWISE)
            
            # Update display
            self.display_images()
            print("Image rotated successfully!")
            
        except Exception as e:
            print(f"Error rotating image: {e}")
            self.show_error_message("Failed to rotate image")

    def save_current_state(self):
        """Save the current image state to the undo stack"""
        current_image = self.modified_image if self.modified_image is not None else self.original_image
        if current_image is not None:
            self.undo_stack.append(current_image.copy())
            self.redo_stack.clear()  # Clear redo stack when making new changes

    def undo_action(self):
        """Undo the last edit operation"""
        if not self.undo_stack:
            self.show_error_message("Nothing to undo")
            return
            
        # Get current image for redo
        current_image = self.modified_image if self.modified_image is not None else self.original_image
        
        # Move current state to redo stack
        if current_image is not None:
            self.redo_stack.append(current_image.copy())
            
        # Restore previous state
        self.modified_image = self.undo_stack.pop()
        
        # Special case: If we've undone back to original
        if not self.undo_stack and self.modified_image is not None:
            if (self.modified_image == self.original_image).all():
                self.modified_image = None
        
        # Update display
        self.display_images()
        print("Undo successful")

    def redo_action(self):
        """Redo the last undone operation"""
        if not self.redo_stack:
            self.show_error_message("Nothing to redo")
            return
            
        # Save current state for possible undo
        current_image = self.modified_image if self.modified_image is not None else self.original_image
        if current_image is not None:
            self.undo_stack.append(current_image.copy())
            
        # Restore next state
        self.modified_image = self.redo_stack.pop()
        
        # Update display
        self.display_images()
        print("Redo successful")

    def adjust_zoom(self, value):
        """Adjust the zoom level of displayed images"""
        if self.original_image is not None:
            self.display_images()

    def save_image(self):
        """Save the current modified image to a file"""
        if not self.has_image_loaded():
            self.show_error_message("No image to save")
            return
            
        # Determine which image to save
        image_to_save = self.modified_image if self.modified_image is not None else self.original_image
        
        # Set up file dialog
        filetypes = [
            ("JPEG", "*.jpg"),
            ("PNG", "*.png"),
            ("All Files", "*.*")
        ]
        
        save_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".jpg",
            filetypes=filetypes
        )
        
        if not save_path:  # User cancelled
            return
            
        try:
            # Save the image
            cv2.imwrite(save_path, image_to_save)
            print(f"Image saved successfully to: {save_path}")
            
        except Exception as e:
            print(f"Error saving image: {e}")
            self.show_error_message("Failed to save image")

    def has_image_loaded(self):
        """Check if an image is loaded"""
        return self.original_image is not None

    def show_error_message(self, message):
        """Show an error message to the user"""
        print(f"Error: {message}")
        # Could use messagebox here for better UX
        # from tkinter import messagebox
        # messagebox.showerror("Error", message)

def main():
    """Main function to start the application"""
    root = Tk()
    app = ImageEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()