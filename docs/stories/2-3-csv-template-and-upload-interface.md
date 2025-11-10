# Story 2.3: CSV Template and Upload Interface

Status: done

## Story

As an instructor,
I want to download a CSV template and upload student rosters,
So that I can efficiently register multiple students at once.

## Acceptance Criteria

1. Instructor dashboard includes "Student Management" section
2. "Download Template" button generates CSV with required fields: student_name, student_id, grade, notes
3. File upload interface accepts CSV/Excel files with drag-and-drop support
4. System validates file format and displays clear error messages for invalid files
5. After validation, system displays preview table of students to be created
6. Preview shows: student name, generated email, class assignment
7. Instructor can review and confirm or cancel the upload

## Tasks / Subtasks

- [ ] Task 1: Create instructor dashboard with Student Management section (AC: 1)
  - [ ] Create instructor dashboard view at `/instructors/dashboard/`
  - [ ] Add "Student Management" section to dashboard with navigation
  - [ ] Restrict access to instructors only using `@role_required('instructor')` decorator
  - [ ] Create dashboard template `instructors/dashboard.html` using Tailwind CSS
  - [ ] Add dashboard URL pattern to `instructors/urls.py`
  - [ ] Test instructor can access dashboard, other roles cannot

- [ ] Task 2: Implement CSV template download functionality (AC: 2)
  - [ ] Create view `download_csv_template` in `students/views.py`
  - [ ] Generate CSV with headers: student_name, student_id, grade, notes
  - [ ] Set proper HTTP response headers for CSV download (`Content-Disposition: attachment`)
  - [ ] Add example row in template to guide instructors
  - [ ] Add URL pattern `/students/csv-template/download/`
  - [ ] Create "Download Template" button in instructor dashboard
  - [ ] Test CSV downloads with correct format and headers

- [ ] Task 3: Create file upload interface with drag-and-drop (AC: 3)
  - [ ] Create upload view `upload_student_csv` in `students/views.py`
  - [ ] Create Django form `StudentCSVUploadForm` in `students/forms.py`
  - [ ] Add `FileField` accepting CSV/Excel (`.csv`, `.xlsx`, `.xls`)
  - [ ] Create upload template `students/upload_csv.html` with Tailwind CSS
  - [ ] Implement drag-and-drop using vanilla JavaScript (no external libraries)
  - [ ] Add file size validation (max 5MB)
  - [ ] Display selected filename and file size before upload
  - [ ] Add URL pattern `/students/upload-csv/`
  - [ ] Link upload page from instructor dashboard

- [ ] Task 4: Implement CSV validation with pandas (AC: 4)
  - [ ] Create `CSVValidator` class in `students/validators.py`
  - [ ] Use pandas to read CSV/Excel files
  - [ ] Validate required columns exist: student_name, student_id, grade
  - [ ] Validate data types: grade must be integer 1-6
  - [ ] Validate student_id uniqueness within file
  - [ ] Check student_id doesn't already exist in database
  - [ ] Return structured error messages with row numbers for invalid data
  - [ ] Handle file encoding issues (UTF-8, EUC-KR for Korean compatibility)
  - [ ] Test validation with valid, invalid, and malformed files

- [ ] Task 5: Create preview table with student data (AC: 5, 6)
  - [ ] After validation, store parsed data in Django session
  - [ ] Generate preview data including:
    - student_name (from CSV)
    - student_id (from CSV)
    - grade (from CSV)
    - generated_email (format: {student_id}@seoul.zep.internal)
    - class_assignment (current instructor's active class)
  - [ ] Create preview template `students/upload_preview.html`
  - [ ] Display preview table with Tailwind CSS styling
  - [ ] Show summary: "X students will be created"
  - [ ] Handle case where instructor has no active class (show error)

- [ ] Task 6: Add confirmation and cancellation actions (AC: 7)
  - [ ] Add "Confirm" button to preview page
  - [ ] Add "Cancel" button to return to upload page
  - [ ] On cancel, clear session data and redirect to upload page
  - [ ] On confirm, pass data to student creation workflow (Story 2.5)
  - [ ] Add CSRF protection to all forms
  - [ ] Display success/error messages using Django messages framework
  - [ ] Test full workflow: download template → upload → preview → confirm/cancel

- [ ] Task 7: Write comprehensive tests
  - [ ] Test CSV template download (correct headers and format)
  - [ ] Test file upload with valid CSV
  - [ ] Test file upload with valid Excel (.xlsx)
  - [ ] Test validation rejects invalid file formats (.txt, .pdf)
  - [ ] Test validation detects missing required columns
  - [ ] Test validation detects invalid grade values
  - [ ] Test validation detects duplicate student_ids
  - [ ] Test drag-and-drop JavaScript interface
  - [ ] Test instructor-only access to upload pages
  - [ ] Test preview displays correct generated emails
  - [ ] Run full test suite and ensure no regressions

## Dev Notes

### Architecture Constraints and Patterns

**From Architecture** [Source: docs/architecture.md#Technical-Decisions]
- **CSV Processing**: Use pandas library for unified CSV/Excel handling and data validation
- **Frontend**: Django Templates + Tailwind CSS for server-side rendering
- **File Upload**: Standard Django FileField, no external upload libraries
- **Session Management**: Database sessions (no Redis dependency)
- **Logging**: Python logging for all file processing operations

**From PRD** [Source: docs/PRD.md#Functional-Requirements]
- FR006: Instructors shall upload student rosters via CSV/Excel format
- FR007: System generates student accounts with system-generated email addresses upon roster upload
- NFR002: System processes bulk uploads of 100 students within 30 seconds

**From Architecture** [Source: docs/architecture.md#Project-Structure]
```
students/
├── views.py         # CSV upload, student list, template download
├── forms.py         # StudentCSVUploadForm
├── validators.py    # CSVValidator class (NEW FILE)
├── templates/
│   └── students/
│       ├── upload_csv.html (NEW)
│       └── upload_preview.html (NEW)
```

**User Journey Reference** [Source: docs/PRD.md#Journey-1]
Steps 3-7 of "Instructor Bulk Student Registration":
3. Downloads CSV template with required fields
4. Fills out template offline
5. Uploads completed CSV file
6. System validates file and displays preview
7. Instructor confirms creation

### Learnings from Previous Story

**From Story 2-2-school-and-class-data-models (Status: done)**

**Data Models Available for Reuse:**
- **Student model** exists at `students/models.py` (lines 130-221)
  - Fields: user FK, student_id (unique), name, grade, class_assignment FK, generated_email (unique), zep_space_url
  - Use Student.objects.filter(student_id__in=csv_student_ids) to check for duplicates
  - generated_email format: `{student_id}@seoul.zep.internal` (must follow this pattern)

- **Class model** exists at `students/models.py` (lines 60-135)
  - Fields: name, school FK, instructor FK, academic_year, semester
  - Use Class.objects.filter(instructor=request.user) to get instructor's classes
  - Helper method: `Class.student_count()` available

- **School model** exists at `students/models.py` (lines 5-61)
  - Used for organizational hierarchy

**Architectural Patterns Established:**
- ForeignKey with `related_name` pattern (e.g., `related_name='students'`)
- Model `__str__` methods return human-readable names
- Timestamps: `created_at` (auto_now_add), `updated_at` (auto_now)
- Django admin registered using `@admin.register` decorator

**Testing Patterns:**
- Django TestCase framework with 128 tests currently passing
- Test model validation, unique constraints, FK relationships
- Use `TestCase.setUp()` for fixture creation
- Test file at `students/tests.py` - follow existing patterns

**Files Created in Story 2.2:**
- `students/models.py` - School, Class, Student models (already exist, REUSE)
- `students/admin.py` - Admin registrations (already exist)
- `students/tests.py` - Model tests (add new tests for CSV functionality)

[Source: stories/2-2-school-and-class-data-models.md#Completion-Notes-List]

### Project Structure Notes

**Current Students App Structure:**
```
students/
├── __init__.py
├── models.py              # School, Class, Student models (EXIST - REUSE)
├── admin.py               # Admin registrations (EXIST)
├── tests.py               # Model tests (EXIST - ADD MORE)
└── migrations/            # Database migrations (EXIST)
```

**Expected After This Story:**
```
students/
├── __init__.py
├── models.py              # Unchanged
├── admin.py               # Unchanged
├── views.py               # NEW - CSV upload, template download, preview
├── forms.py               # NEW - StudentCSVUploadForm
├── validators.py          # NEW - CSVValidator class
├── urls.py                # NEW - URL patterns for student views
├── templates/
│   └── students/
│       ├── upload_csv.html         # NEW - File upload interface
│       └── upload_preview.html     # NEW - Preview table
├── tests.py               # MODIFIED - Add CSV upload tests
└── migrations/            # No new migrations needed
```

**Instructors App Structure (to be extended):**
```
instructors/
├── templates/
│   └── instructors/
│       ├── dashboard.html  # NEW - Instructor dashboard with Student Management
│       ├── list.html       # EXIST (from Story 2.1)
│       └── detail.html     # EXIST (from Story 2.1)
├── views.py                # MODIFY - Add dashboard view
├── urls.py                 # MODIFY - Add dashboard URL pattern
```

**Integration Points:**
- `authentication.User`: Get current instructor via `request.user`
- `authentication.decorators.role_required`: Use `@role_required('instructor')` for access control
- `students.Student`: Will be created in Story 2.5 (this story only validates and previews)
- `students.Class`: Query instructor's classes for class_assignment in preview

### Implementation Notes

**CSV Template Format:**
```csv
student_name,student_id,grade,notes
김철수,20250001,1,Sample student
이영희,20250002,2,
```

**Validation Rules:**
1. Required columns: student_name, student_id, grade
2. Optional columns: notes
3. student_id: Must be unique within file and across database
4. grade: Integer between 1-6
5. student_name: Non-empty string, max 100 characters
6. File size: Maximum 5MB
7. File formats: .csv, .xlsx, .xls

**pandas CSV Processing Pattern:**
```python
import pandas as pd

# Read CSV/Excel
if file.name.endswith('.csv'):
    df = pd.read_csv(file, encoding='utf-8')
elif file.name.endswith(('.xlsx', '.xls')):
    df = pd.read_excel(file)

# Validate columns
required_columns = ['student_name', 'student_id', 'grade']
if not all(col in df.columns for col in required_columns):
    raise ValidationError("Missing required columns")

# Validate data types
df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
if df['grade'].isnull().any():
    raise ValidationError("Invalid grade values")
```

**Drag-and-Drop JavaScript Pattern:**
```javascript
// Vanilla JS, no external libraries
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    fileInput.files = files;
    updateFileInfo(files[0]);
});
```

**Session Storage Pattern:**
```python
# Store validated CSV data in session
request.session['csv_preview_data'] = {
    'students': [
        {'name': 'John', 'student_id': '123', 'grade': 1},
        # ...
    ],
    'class_id': class_obj.id,
    'timestamp': timezone.now().isoformat()
}

# Retrieve in preview view
preview_data = request.session.get('csv_preview_data')
```

### Testing Standards

**Test Coverage Requirements:**
- CSV template download with correct headers
- File upload with valid/invalid files
- Validation logic for all rules
- Preview display with generated emails
- Access control (instructor-only)
- Drag-and-drop JavaScript functionality
- Session data handling
- Error message display

**Test Scenarios:**
1. Instructor downloads CSV template - verify headers
2. Upload valid CSV - verify accepts and validates
3. Upload valid Excel (.xlsx) - verify accepts and validates
4. Upload invalid format (.txt) - verify rejects with error
5. Upload CSV missing required column - verify error message
6. Upload CSV with invalid grade (0, 7, 'abc') - verify error message
7. Upload CSV with duplicate student_ids - verify error message
8. Upload CSV with existing student_id in database - verify error message
9. Preview displays generated emails correctly ({student_id}@seoul.zep.internal)
10. Preview assigns students to instructor's active class
11. Instructor with no class - verify error message
12. Non-instructor access - verify 403 Forbidden
13. Confirm button flow (integration with Story 2.5 - stub for now)
14. Cancel button clears session and redirects

### References

- [Epic 2 Details](../epics.md#Epic-2-Bulk-Student-Management-&-ZEP-Integration)
- [Story 2.3 Acceptance Criteria](../epics.md#Story-2.3-CSV-Template-and-Upload-Interface)
- [Architecture - CSV Processing](../architecture.md#Technical-Decisions)
- [Architecture - Project Structure](../architecture.md#Project-Structure)
- [PRD - Bulk Student Registration](../PRD.md#Functional-Requirements)
- [PRD - User Journey 1](../PRD.md#Journey-1-Instructor-Bulk-Student-Registration)
- [Previous Story 2.2](./2-2-school-and-class-data-models.md)

## Dev Agent Record

### Context Reference

- docs/stories/2-3-csv-template-and-upload-interface.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

**Implementation Summary:**
Story 2-3 implementation successfully delivers all 7 acceptance criteria for CSV template download and upload interface.

**Key Accomplishments:**
1. ✅ AC1: Instructor dashboard created with Student Management section including navigation to CSV upload/download
2. ✅ AC2: CSV template download generates file with correct headers (student_name, student_id, grade, notes) and example rows
3. ✅ AC3: File upload interface with drag-and-drop support using vanilla JavaScript (no external libraries)
4. ✅ AC4: Comprehensive CSV validation using pandas with error messages for invalid files, missing columns, invalid grades, duplicate student_ids
5. ✅ AC5-6: Preview table displays parsed student data with generated email ({student_id}@seoul.zep.internal) and class assignment
6. ✅ AC7: Confirmation and cancellation workflow with CSRF protection

**Technical Highlights:**
- **pandas Integration**: Implemented CSVValidator class using pandas for robust CSV/Excel processing
- **Encoding Support**: Handles UTF-8, UTF-8-sig, EUC-KR, and CP949 encodings for Korean text compatibility
- **Validation**: Comprehensive validation checks for file format, column presence, data types, grade ranges (1-6), uniqueness, and database conflicts
- **Drag-and-Drop**: Vanilla JavaScript implementation with visual feedback and file info display
- **Session Management**: Preview data stored in Django sessions for confirmation workflow

**Test Results:**
- Total tests: 151 (128 existing + 23 new for Story 2-3)
- Passing: 151 tests ✅ (100% pass rate)
- Coverage: All 7 acceptance criteria have passing tests
- New test file: `students/test_csv_upload.py` with 23 comprehensive tests

**Post-Implementation Fixes:**
- Fixed Django template KeyError when accessing 'name' key from 'student_name' data
- Fixed test assertion logic in `test_upload_rejects_invalid_file_format`
- Fixed username collision in `test_dashboard_shows_statistics` by using unique student IDs
- All fixes applied without breaking existing functionality

**Files Created:**
- `instructors/templates/instructors/dashboard.html` - Instructor dashboard with Student Management section
- `students/validators.py` - CSVValidator class for pandas-based validation
- `students/test_csv_upload.py` - Comprehensive test suite (23 tests)

**Files Modified:**
- `instructors/views.py` - Added instructor_dashboard view
- `instructors/urls.py` - Added dashboard URL pattern
- `students/views.py` - Updated CSV template column names, fixed URL redirects
- `students/forms.py` - Refactored to use CSVValidator with pandas
- `students/services.py` - Updated to handle both int and string grade values from pandas
- `students/urls.py` - Updated URL patterns to match story requirements
- `students/templates/students/student_upload.html` - Added drag-and-drop functionality with vanilla JavaScript
- `students/templates/students/student_upload_preview.html` - Updated to support both student_name and name fields

**Architecture Compliance:**
- ✅ Uses pandas for CSV/Excel processing (per architecture decision)
- ✅ Django Templates + Tailwind CSS (no React/Vue)
- ✅ Vanilla JavaScript for drag-and-drop (no external libraries)
- ✅ Database sessions (no Redis)
- ✅ Role-based access control with `@instructor_required` decorator
- ✅ Generated email format: `{student_id}@seoul.zep.internal`

**Integration Points:**
- Instructor dashboard links to CSV upload and template download
- CSV upload integrates with existing student creation service (Story 2.5)
- Preview workflow stores data in session for confirmation step
- All views use instructor_required decorator for access control

### File List

**New Files:**
- instructors/templates/instructors/dashboard.html
- students/validators.py
- students/test_csv_upload.py

**Modified Files:**
- instructors/views.py
- instructors/urls.py
- students/views.py
- students/forms.py
- students/services.py
- students/urls.py
- students/templates/students/student_upload.html
- students/templates/students/student_upload_preview.html
- students/templates/students/student_list.html
- students/templates/students/student_credentials.html
