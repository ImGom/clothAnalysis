# Clothing Analysis System (의류 분석 시스템)

## Overview
A Flask-based web application that uses Google's Gemini AI to analyze images of people wearing clothes and match them to a clothing database. The system can identify tops, bottoms, and shoes from full-body images and display matching items from the local database.

## Recent Changes (September 30, 2025)
- Fixed typo in requirements filename (requirementes.txt → requirements.txt)
- Updated port from 8080 to 5000 for Replit compatibility
- Installed all Python dependencies (Flask, Pillow, google-generativeai, python-dotenv)
- Created workflow for Flask server
- Added .env.example for configuration template
- Configured for Replit environment

## Project Architecture

### Technology Stack
- **Backend**: Flask (Python)
- **AI**: Google Gemini 2.0 Flash Exp
- **Image Processing**: Pillow
- **Frontend**: Vanilla HTML/CSS/JavaScript

### Directory Structure
```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── data/
│   ├── clothing_db.json   # Clothing items database
│   └── config.json        # Color and type normalization config
├── static/
│   └── images/           # Clothing images organized by category
│       ├── Bottoms/
│       ├── Shoes/
│       └── Tops/
└── templates/
    └── index.html        # Web interface
```

### Key Features
1. **Image Upload**: Upload full-body images for analysis
2. **AI Analysis**: Uses Gemini AI to identify clothing items (color, type)
3. **Database Matching**: Matches identified items to local database
4. **Visual Results**: Displays matched clothing items with images

### Configuration Required
- `GOOGLE_API_KEY`: Google Gemini API key (set in Replit Secrets)

### API Endpoints
- `GET /`: Main web interface
- `POST /api/analyze`: Analyze uploaded image and return matches

### Database Schema
Each item in `clothing_db.json` contains:
- `id`: Unique identifier
- `category`: top, bottom, or shoes
- `color`: Standardized color name
- `type`: Specific clothing type
- `description`: Human-readable description (Korean)
- `image`: Path to image file

## Development
The application runs on port 5000 and is configured for the Replit environment.
