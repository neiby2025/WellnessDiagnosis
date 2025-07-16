# 東洋医学体質診断アプリ (Traditional Chinese Medicine Constitution Diagnosis App)

## Overview

This is a Streamlit-based web application that provides Traditional Chinese Medicine (TCM) constitution diagnosis. The app conducts a questionnaire-based assessment to determine a user's constitution type according to TCM principles and provides personalized health advice based on the results.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework
- **UI Pattern**: Single-page application with session state management
- **Layout**: Wide layout configuration for better user experience
- **Language**: Japanese interface with TCM-specific terminology

### Backend Architecture
- **Core Logic**: Python-based diagnosis engine with weighted scoring system
- **Data Processing**: Pandas for data manipulation and CSV operations
- **Session Management**: Streamlit's built-in session state for maintaining user data across interactions

### Data Storage Solutions
- **Primary Storage**: PostgreSQL database for diagnosis results and statistics
- **Database Schema**: 
  - `diagnosis_results` table: stores all diagnosis data with JSONB for responses
  - `users` table: user tracking for future expansion
- **Data Persistence**: Cloud-based PostgreSQL with automated backups
- **Legacy Support**: Maintained CSV export functionality for data portability

## Key Components

### 1. Main Application (app.py)
- **Purpose**: Primary Streamlit interface and orchestration
- **Responsibilities**: 
  - User interface rendering
  - Session state management
  - Result persistence to CSV
  - Integration with diagnosis engine

### 2. Diagnosis Engine (diagnosis_engine.py)
- **Purpose**: Core logic for TCM constitution assessment
- **Algorithm**: Weighted scoring system based on TCM principles
- **Constitution Types**: Supports multiple TCM constitution types (気虚, 陽虚, 陰虚, 痰湿, 湿熱, 血瘀, 気鬱)
- **Scoring Method**: Question-response mapping with constitution-specific weights

### 3. TCM Data Module (tcm_data.py)
- **Purpose**: Static data storage for questions, constitution types, and health advice
- **Content**: 
  - Questionnaire definitions
  - Constitution type descriptions
  - Personalized health recommendations

## Data Flow

1. **User Input**: User provides basic information (age, gender) and completes TCM questionnaire
2. **Response Collection**: Streamlit session state captures and maintains user responses
3. **Diagnosis Processing**: Diagnosis engine processes responses using weighted scoring algorithm
4. **Result Generation**: System determines primary constitution type with confidence score
5. **Advice Delivery**: Personalized health advice retrieved based on constitution type
6. **Data Persistence**: Results automatically saved to CSV file with timestamp

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and CSV operations
- **datetime**: Timestamp generation for result tracking
- **os**: File system operations for data directory management
- **random**: Used in diagnosis engine for algorithmic randomization

### Data Dependencies
- **tcm_data module**: Contains static TCM knowledge base
- **Local file system**: For CSV-based result storage

## Deployment Strategy

### Current Setup
- **Platform**: Designed for Replit deployment
- **Requirements**: Python environment with Streamlit support
- **Storage**: Local file system for data persistence
- **Configuration**: Streamlit page configuration with custom title and icon

### Scalability Considerations
- **Database Migration**: Current CSV storage can be upgraded to database system
- **User Management**: Session-based approach suitable for single-user or small-scale usage
- **Data Backup**: Local CSV files should be backed up regularly

### Known Limitations
- **Concurrent Users**: Session state management may have limitations with multiple simultaneous users
- **Data Persistence**: CSV-based storage is not suitable for high-volume production use
- **Incomplete Implementation**: The diagnosis engine appears to have incomplete constitution weight definitions

### Recommended Enhancements
- **Database Integration**: Consider adding Postgres or similar database for better data management
- **User Authentication**: Add user accounts for personalized history tracking
- **Result Analytics**: Dashboard for viewing diagnosis trends and statistics
- **Mobile Optimization**: Ensure responsive design for mobile devices