The code is in github codespace

# 🥗 Food Health Analyzer

An AI-powered application that analyzes packaged food products to provide detailed health insights. The app uses computer vision to scan barcodes and nutrition labels, cross-references with FSSAI regulations, and provides a comprehensive health analysis.

## 🎯 Key Features

- **Multi-Source Barcode Lookup**
  - OpenFoodFacts database integration
  - UPCitemdb API fallback
  - BarcodeSpider API support
  
- **Advanced Image Processing**
  - Barcode detection with multiple preprocessing methods
  - OCR-based nutrition label analysis
  - Intelligent ingredients section detection
  
- **Health Analysis**
  - Detailed nutrient analysis
  - FSSAI regulation compliance checking
  - Health score calculation (0-100)
  - Ingredient safety assessment
  
- **User Interface**
  - Camera-based product scanning
  - Manual barcode entry
  - Image upload support
  - Detailed analysis visualization

## 🛠️ Technology Stack

### Backend
- Python 3.12
- OpenCV (Computer Vision)
- Tesseract OCR
- PyZBar (Barcode Processing)
- NumPy & Pandas (Data Processing)

### Frontend
- Streamlit (Web Interface)
- PIL (Image Processing)

### APIs & Data Sources
- OpenFoodFacts API
- UPCitemdb API
- BarcodeSpider API
- FSSAI Regulations Database

## 📋 Prerequisites

### System Requirements
- Ubuntu 24.04 LTS or compatible Linux system
- Python 3.12+
- 4GB RAM minimum
- Webcam (for scanning features)

### System Dependencies
```bash
# Install required system packages
sudo apt-get update && sudo apt-get install -y \
    libzbar0 \
    libzbar-dev \
    python3-opencv \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0t64
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/food-health-analyzer.git
cd food-health-analyzer
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your API keys:
# GOOGLE_API_KEY=your_key
# GOOGLE_CX=your_cx
```

5. Create necessary directories:
```bash
mkdir -p app/references
```

## 💻 Usage

1. Start the Streamlit app:
```bash
cd app
streamlit run app.py
```

2. Access the application:
- Local: http://localhost:8501
- Network: http://10.0.2.79:8501
- External: http://4.240.18.229:8501

## 📁 Project Structure

```
food-health-analyzer/
├── app/
│   ├── __init__.py
│   ├── app.py              # Main Streamlit application
│   ├── input_handler.py    # Product data fetching
│   ├── scoring.py          # Health score calculation
│   ├── vision_handler.py   # Image processing & OCR
│   ├── web_fallback.py     # Additional API integrations
│   └── references/         # Database files
│       ├── fssai_regulations.json
│       └── nutrient_limits.json
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── README.md
```

## 🔍 Technical Details

### Barcode Processing Pipeline
1. Image preprocessing (resize, denoise, contrast enhancement)
2. Multiple processing methods attempted:
   - Original grayscale
   - Denoised
   - Contrast enhanced
   - Thresholded
   - Morphological operations

### Text Extraction Process
1. Image preprocessing
2. Intelligent section detection
3. OCR with Tesseract
4. Post-processing and validation

### Health Score Calculation
- Base score: 100 points
- Deductions for:
  - Excessive additives (-5 per item)
  - High sugar/salt/fat content (-10 each)
  - Non-compliant ingredients (-15 each)
- Bonuses for:
  - Healthy nutrients (+5 each)
  - Compliant ingredients (+2 each)

## 🔒 Security Notes

- API keys are stored in `.env` file (not committed)
- Image processing is done locally
- No user data is stored
- All API calls use HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request



## 🙏 Acknowledgments

- [OpenFoodFacts](https://world.openfoodfacts.org/) for product database
- [FSSAI](https://www.fssai.gov.in/) for food regulations
- [Streamlit](https://streamlit.io/) for the web framework
- [Tesseract](https://github.com/tesseract-ocr/tesseract) for OCR capabilities
- [OpenCV](https://opencv.org/) for image processing

## 📚 References

- [FSSAI Regulations](https://www.fssai.gov.in/regulations.php)
- [OpenFoodFacts API Documentation](https://openfoodfacts.github.io/api-documentation/)
- [Tesseract Documentation](https://tesseract-ocr.github.io/tessdoc/)
- [Streamlit Documentation](https://docs.streamlit.io/)
