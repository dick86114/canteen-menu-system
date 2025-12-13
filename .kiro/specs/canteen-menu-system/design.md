# Design Document - Canteen Menu System

## Overview

The Canteen Menu System is a full-stack web application that enables administrators to upload Excel files containing weekly menus and allows users to browse daily menus through an intuitive date-based interface. The system consists of a React frontend for user interaction and a Flask backend for file processing and data management.

## Architecture

The system follows a client-server architecture with clear separation of concerns:

### Frontend (React)
- **User Interface Layer**: React components for file upload, menu display, and date navigation
- **State Management**: React hooks for managing application state and API interactions
- **Responsive Design**: CSS Grid/Flexbox with Bootstrap for cross-device compatibility

### Backend (Flask)
- **API Layer**: RESTful endpoints for file upload and menu data retrieval
- **File Processing Layer**: Excel parsing using pandas and openpyxl
- **Data Layer**: In-memory storage with optional database persistence

### Communication
- **HTTP/REST API**: JSON-based communication between frontend and backend
- **File Upload**: Multipart form data for Excel file transmission

## Components and Interfaces

### Frontend Components

#### MenuUpload Component
- **Purpose**: Handle Excel file selection and upload
- **Props**: onUploadSuccess callback
- **State**: uploadStatus, selectedFile, uploadProgress
- **Methods**: handleFileSelect(), uploadFile(), validateFile()

#### MenuDisplay Component  
- **Purpose**: Render daily menu cards with food items
- **Props**: menuData, selectedDate
- **State**: displayMode (card/list)
- **Methods**: renderMenuCard(), formatMealTime(), groupByMealType()

#### DateSelector Component
- **Purpose**: Provide date navigation and selection
- **Props**: selectedDate, onDateChange, availableDates
- **State**: calendarVisible, dateRange
- **Methods**: handleDateChange(), navigateDate(), checkDateAvailability()

#### App Component
- **Purpose**: Main application container and state management
- **State**: currentDate, menuData, uploadedFiles, loading
- **Methods**: fetchMenuData(), handleDateChange(), handleUploadSuccess()

### Backend Interfaces

#### File Upload API
```python
POST /api/upload
Content-Type: multipart/form-data
Response: {
  "status": "success|error",
  "message": "string",
  "data": MenuData[]
}
```

#### Menu Retrieval API
```python
GET /api/menu?date=YYYY-MM-DD
Response: {
  "date": "YYYY-MM-DD",
  "meals": [
    {
      "type": "breakfast|lunch|dinner",
      "time": "HH:MM",
      "items": [
        {
          "name": "string",
          "description": "string",
          "category": "string"
        }
      ]
    }
  ]
}
```

#### Available Dates API
```python
GET /api/dates
Response: {
  "dates": ["YYYY-MM-DD"],
  "dateRange": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD"
  }
}
```

## Data Models

### MenuData Model
```typescript
interface MenuData {
  date: string;           // ISO date format YYYY-MM-DD
  meals: Meal[];
}

interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner';
  time: string;           // HH:MM format
  items: MenuItem[];
}

interface MenuItem {
  name: string;
  description?: string;
  category?: string;
  price?: number;
}
```

### Excel Data Structure
Expected Excel format:
- Column A: Date (YYYY-MM-DD or recognizable date format)
- Column B: Meal Type (breakfast/lunch/dinner)
- Column C: Time (HH:MM)
- Column D: Food Name
- Column E: Description
- Column F: Category (optional)

### Storage Model
```python
class MenuStorage:
    def __init__(self):
        self.menu_data: Dict[str, List[Meal]] = {}
        self.uploaded_files: List[str] = []
    
    def store_menu_data(self, date: str, meals: List[Meal]) -> None
    def get_menu_by_date(self, date: str) -> Optional[List[Meal]]
    def get_available_dates(self) -> List[str]
    def clear_data(self) -> None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, the following correctness properties have been identified:

**Property 1: File format validation consistency**
*For any* uploaded file, the system should accept the file if and only if it has a .xlsx extension, rejecting all other formats with appropriate error messages
**Validates: Requirements 1.1, 1.4, 5.1**

**Property 2: Excel parsing completeness**
*For any* valid Excel file with menu data, the parser should extract all present data fields (dates, food names, descriptions, meal types) without loss
**Validates: Requirements 1.2**

**Property 3: Data storage round trip**
*For any* parsed menu data, storing and then retrieving the data should return equivalent menu information
**Validates: Requirements 1.3**

**Property 4: File size limit enforcement**
*For any* file upload attempt, files exceeding the size limit should be consistently rejected regardless of content or format
**Validates: Requirements 1.5, 5.4**

**Property 5: Fallback menu selection**
*For any* date without menu data, the system should display the most recent available menu from the stored data
**Validates: Requirements 2.2**

**Property 6: Menu display completeness**
*For any* valid menu data, the display should include all required fields (food names, descriptions, meal times) in the rendered output
**Validates: Requirements 2.3**

**Property 7: Empty date handling**
*For any* date with no menu data, the system should display a consistent "no data available" message
**Validates: Requirements 2.4**

**Property 8: Meal organization consistency**
*For any* menu data with multiple meals, the display should group items by meal type and order them by time periods
**Validates: Requirements 2.5**

**Property 9: Date selection synchronization**
*For any* date selection, the menu display should update to show the corresponding menu data for that specific date
**Validates: Requirements 3.2**

**Property 10: Date state persistence**
*For any* date selection during a user session, the selected date should remain active until explicitly changed by the user
**Validates: Requirements 3.5**

**Property 11: Excel parsing robustness**
*For any* malformed or corrupted Excel file, the parser should handle errors gracefully without system crashes and provide meaningful error messages
**Validates: Requirements 5.2, 5.5**

**Property 12: UI styling consistency**
*For any* menu card rendered, the styling classes and typography should be applied consistently across all cards
**Validates: Requirements 6.2**

## Error Handling

### File Upload Errors
- **Invalid Format**: Return HTTP 400 with descriptive error message
- **File Too Large**: Return HTTP 413 with size limit information
- **Corrupted File**: Return HTTP 422 with parsing error details
- **Network Issues**: Implement retry mechanism with exponential backoff

### Data Processing Errors
- **Malformed Excel**: Log error details, return user-friendly message
- **Missing Required Columns**: Validate structure, provide column mapping guidance
- **Date Parsing Failures**: Use fallback date formats, flag problematic entries
- **Empty Data Sets**: Handle gracefully, maintain system stability

### Frontend Error Handling
- **API Failures**: Display error notifications with retry options
- **Loading States**: Show progress indicators during file processing
- **Network Connectivity**: Detect offline state, queue operations
- **Invalid User Input**: Provide real-time validation feedback

## Testing Strategy

### Dual Testing Approach

The system will employ both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Testing**:
- Specific examples demonstrating correct behavior
- Integration points between frontend and backend components
- Edge cases like empty files, single-day menus, boundary dates
- Error conditions and recovery scenarios

**Property-Based Testing**:
- Universal properties that should hold across all inputs
- Uses Hypothesis for Python backend testing
- Uses fast-check for JavaScript frontend testing
- Each property-based test configured to run minimum 100 iterations
- Each test tagged with format: '**Feature: canteen-menu-system, Property {number}: {property_text}**'

**Testing Framework Selection**:
- **Backend**: pytest with Hypothesis for property-based testing
- **Frontend**: Jest with fast-check for property-based testing
- **Integration**: Cypress for end-to-end testing scenarios

**Property-Based Test Requirements**:
- Each correctness property must be implemented by a single property-based test
- Tests must reference the corresponding design document property
- Minimum 100 iterations per property test to ensure statistical confidence
- Smart generators that constrain input space intelligently (valid Excel structures, realistic menu data)

### Test Data Generation

**Excel File Generators**:
- Valid menu structures with varying date ranges
- Files with missing columns or malformed data
- Empty files and files with only headers
- Files with different date formats and meal types

**Menu Data Generators**:
- Random but realistic food names and descriptions
- Various meal types and time combinations
- Edge cases like single meals or full-day menus
- Different date ranges and availability patterns

## Implementation Technologies

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Styling**: Bootstrap 5 with custom CSS modules
- **Date Handling**: react-datepicker for date selection
- **HTTP Client**: Axios for API communication
- **State Management**: React hooks (useState, useEffect, useContext)
- **Build Tool**: Vite for fast development and building

### Backend Stack
- **Framework**: Flask 2.3 with Python 3.9+
- **Excel Processing**: pandas and openpyxl for file parsing
- **File Handling**: Werkzeug for secure file uploads
- **API Documentation**: Flask-RESTX for OpenAPI documentation
- **CORS**: Flask-CORS for cross-origin requests
- **Validation**: marshmallow for request/response validation

### Development Tools
- **Testing**: pytest (backend), Jest (frontend)
- **Property Testing**: Hypothesis (backend), fast-check (frontend)
- **Code Quality**: ESLint, Prettier (frontend), Black, flake8 (backend)
- **Type Checking**: TypeScript (frontend), mypy (backend)