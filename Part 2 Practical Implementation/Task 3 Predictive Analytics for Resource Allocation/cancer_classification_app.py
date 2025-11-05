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
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            self.model = tf.keras.models.load_model('cancer_classification_model.h5')
            st.sidebar.success("✅ Model loaded successfully!")
        except Exception as e:
            st.error(f"Error loading model: {e}")
            st.info("Please make sure 'cancer_classification_model.h5' is in the same directory")
    
    def preprocess_image(self, image):
        """Preprocess the uploaded image for prediction"""
        # Resize image to match model input size (128x128)
        image = image.resize((128, 128))
        
        # Convert to numpy array and normalize
        img_array = np.array(image) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict_image(self, image):
        """Make prediction on the uploaded image"""
        if self.model is None:
            return None, None, None
        
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
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
        
        st.sidebar.markdown("### Instructions")
        st.sidebar.text("1. Upload a medical image")
        st.sidebar.text("2. Wait for prediction")
        st.sidebar.text("3. View results and confidence")
        
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
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Make prediction when button is clicked
                if st.button("🔍 Analyze Image", type="primary"):
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
    # Check if model exists
    if not os.path.exists('cancer_classification_model.h5'):
        st.error("Model file 'cancer_classification_model.h5' not found!")
        st.info("""
        Please make sure:
        1. The model file is in the same directory as this app
        2. You've run the training script first
        3. The file name is exactly 'cancer_classification_model.h5'
        """)
        
        # Show training instructions
        with st.expander("How to train the model"):
            st.code("""
            # Run the training script first
            python cancer_classification.py
            
            # This will create the model file
            # Then run this app again
            streamlit run cancer_classification_app.py
            """)
        return
    
    # Initialize and run the app
    app = CancerClassifierApp()
    app.run()

if __name__ == "__main__":
    main()