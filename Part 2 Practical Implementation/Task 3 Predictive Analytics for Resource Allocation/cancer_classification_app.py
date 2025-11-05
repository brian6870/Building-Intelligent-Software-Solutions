# cancer_classification_app.py
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import os

# Set page configuration
st.set_page_config(
    page_title="Cancer Image Classifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

class CancerClassifierApp:
    def __init__(self):
        self.model = None
        self.class_names = ['benign', 'malignant']
        self.model_path = None
        self.load_model()
    
    def find_model_file(self):
        """Search for model file in current directory and subdirectories"""
        model_name = 'cancer_classification_model.h5'
        
        # Check current directory first
        if os.path.exists(model_name):
            return model_name
        
        # Search in subdirectories
        for root, dirs, files in os.walk('.'):
            if model_name in files:
                return os.path.join(root, model_name)
        
        # Also check for .keras format
        model_name_keras = 'cancer_classification_model.keras'
        if os.path.exists(model_name_keras):
            return model_name_keras
        
        for root, dirs, files in os.walk('.'):
            if model_name_keras in files:
                return os.path.join(root, model_name_keras)
        
        return None
    
    def load_model(self):
        """Load the trained model from anywhere in the directory/repo"""
        try:
            self.model_path = self.find_model_file()
            
            if self.model_path is None:
                st.error("❌ Model file not found!")
                st.info("""
                Could not find 'cancer_classification_model.h5' or 'cancer_classification_model.keras' 
                in the current directory or any subdirectories.
                
                Please make sure:
                1. The model file exists in this repository
                2. The file name is correct
                3. You've run the training script first
                """)
                return
            
            st.sidebar.info(f"📁 Loading model from: {self.model_path}")
            self.model = tf.keras.models.load_model(self.model_path)
            st.sidebar.success("✅ Model loaded successfully!")
            
        except Exception as e:
            st.error(f"❌ Error loading model: {e}")
            st.info("""
            The model file was found but couldn't be loaded. This might be due to:
            - Incompatible TensorFlow version
            - Corrupted model file
            - Missing custom objects/layers
            """)
    
    def preprocess_image(self, image):
        """Preprocess the uploaded image for prediction"""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to match model input size (128x128)
        image = image.resize((128, 128))
        
        # Convert to numpy array and normalize
        img_array = np.array(image) / 255.0
        
        # Ensure the image has 3 channels (RGB)
        if len(img_array.shape) == 2:  # Grayscale image
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[-1] == 1:  # Single channel
            img_array = np.repeat(img_array, 3, axis=-1)
        elif img_array.shape[-1] == 4:  # RGBA image
            img_array = img_array[:, :, :3]  # Remove alpha channel
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict_image(self, image):
        """Make prediction on the uploaded image"""
        if self.model is None:
            return None, None, None
        
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
        # Debug information (optional)
        st.sidebar.write(f"📊 Input shape: {processed_image.shape}")
        
        # Make prediction
        predictions = self.model.predict(processed_image, verbose=0)
        
        # Get predicted class and confidence
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]
        
        return predicted_class, confidence, predictions[0]
    
    def display_confidence_bars(self, predictions):
        """Display confidence levels as progress bars"""
        for i, (class_name, confidence) in enumerate(zip(self.class_names, predictions)):
            # Create progress bar with color coding
            if i == np.argmax(predictions):
                # Highlight the predicted class
                st.write(f"🎯 **{class_name.upper()}**: {confidence:.2%}")
            else:
                st.write(f"**{class_name.upper()}**: {confidence:.2%}")
            
            st.progress(float(confidence))
            st.write("")
    
    def display_model_info(self):
        """Display information about the loaded model"""
        if self.model and self.model_path:
            with st.sidebar.expander("📊 Model Details"):
                st.write(f"**Model Location:** `{self.model_path}`")
                st.write(f"**Model Layers:** {len(self.model.layers)}")
                st.write(f"**Input Shape:** {self.model.input_shape}")
                st.write(f"**Output Shape:** {self.model.output_shape}")
                st.write(f"**Expected Input:** RGB images (128x128x3)")
    
    def run(self):
        """Run the Streamlit app"""
        # Header
        st.title("🏥 Cancer Image Classification App")
        st.markdown("---")
        
        # Sidebar
        st.sidebar.title("About")
        st.sidebar.info(
            "This app uses a deep learning model to classify cancer images "
            "as **benign** or **malignant**. Upload a medical image to get started."
        )
        
        st.sidebar.markdown("### Model Information")
        st.sidebar.text("Architecture: CNN")
        st.sidebar.text("Accuracy: 79.8%")
        st.sidebar.text("F1-Score: 77.5%")
        st.sidebar.text("Classes: Benign, Malignant")
        
        # Display model details if loaded
        self.display_model_info()
        
        st.sidebar.markdown("### Instructions")
        st.sidebar.text("1. Upload a medical image")
        st.sidebar.text("2. Wait for prediction")
        st.sidebar.text("3. View results and confidence")
        
        # Image format info
        with st.sidebar.expander("📷 Image Requirements"):
            st.write("""
            **Supported formats:** PNG, JPG, JPEG, TIFF, BMP
            
            **Image types handled:**
            - RGB images (3 channels)
            - Grayscale images (converted to RGB)
            - RGBA images (alpha channel removed)
            
            **Expected input:** 128×128×3 RGB images
            """)
        
        # Show model status
        if self.model is None:
            st.sidebar.error("❌ Model not loaded")
        else:
            st.sidebar.success("✅ Model ready for predictions")
        
        # Main content area
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Upload Image")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose a medical image...",
                type=['png', 'jpg', 'jpeg', 'tiff', 'bmp'],
                help="Supported formats: PNG, JPG, JPEG, TIFF, BMP"
            )
            
            if uploaded_file is not None:
                # Display uploaded image
                image = Image.open(uploaded_file)
                
                # Show image information
                st.write(f"**Image format:** {image.format}")
                st.write(f"**Image mode:** {image.mode}")
                st.write(f"**Image size:** {image.size}")
                
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Make prediction when button is clicked
                if st.button("🔍 Analyze Image", type="primary", disabled=self.model is None):
                    with st.spinner("Analyzing image..."):
                        predicted_class, confidence, all_predictions = self.predict_image(image)
                    
                    if predicted_class is not None:
                        # Display results
                        with col2:
                            st.subheader("Analysis Results")
                            
                            # Show prediction with color coding
                            if predicted_class == 0:  # Benign
                                st.success(f"**Prediction: BENIGN**")
                                st.metric("Confidence", f"{confidence:.2%}")
                                st.info("""
                                **Interpretation:** 
                                The model suggests this appears to be a non-cancerous (benign) growth. 
                                Please consult with a healthcare professional for proper diagnosis.
                                """)
                            else:  # Malignant
                                st.error(f"**Prediction: MALIGNANT**")
                                st.metric("Confidence", f"{confidence:.2%}")
                                st.warning("""
                                **Interpretation:** 
                                The model suggests this appears to be a cancerous (malignant) growth. 
                                **Important:** This is an AI prediction and requires confirmation 
                                by a qualified medical professional.
                                """)
                            
                            # Confidence bar
                            st.subheader("Confidence Levels")
                            if all_predictions is not None:
                                self.display_confidence_bars(all_predictions)
            
            else:
                # Show placeholder when no image is uploaded
                with col2:
                    st.subheader("Analysis Results")
                    st.info("👈 Upload an image to see analysis results here")
                    
                    # Sample images section
                    st.subheader("Expected Input")
                    st.text("The model expects medical images similar to:")
                    st.text("• Histopathology slides")
                    st.text("• Medical imaging scans")
                    st.text("• Tissue sample images")
                    
                    st.info("""
                    **Note:** The model expects RGB images. Grayscale images will 
                    be automatically converted to RGB format.
                    """)
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            **Disclaimer:** This tool is for educational and research purposes only. 
            It should not be used for medical diagnosis. Always consult qualified healthcare 
            professionals for medical advice and diagnosis.
            """
        )

def main():
    # Initialize and run the app
    app = CancerClassifierApp()
    app.run()

if __name__ == "__main__":
    main()