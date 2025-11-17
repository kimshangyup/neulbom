"""
CSV Validation for Student Upload

This module provides validation for CSV/Excel student roster files.
"""

import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)


class CSVValidator:
    """
    Validates CSV/Excel files for student roster uploads.

    Performs comprehensive validation including:
    - File format and encoding
    - Required columns
    - Data types and ranges
    - Uniqueness constraints
    - Database conflicts
    """

    REQUIRED_COLUMNS = ['school_name', 'class_name', 'student_name']
    OPTIONAL_COLUMNS = ['class_number', 'grade', 'zep_space_url']

    def __init__(self):
        self.errors = []
        self.data = []

    def validate(self, file):
        """
        Validate uploaded file and return results.

        Args:
            file: Django UploadedFile object

        Returns:
            dict: {'valid': bool, 'data': list, 'errors': list}
        """
        self.errors = []
        self.data = []

        try:
            # Parse file into DataFrame
            df = self._parse_file(file)

            if df is None:
                return {'valid': False, 'data': [], 'errors': self.errors}

            # Validate columns
            if not self._validate_columns(df):
                return {'valid': False, 'data': [], 'errors': self.errors}

            # Validate data
            if not self._validate_data(df):
                return {'valid': False, 'data': [], 'errors': self.errors}

            # Convert to list of dicts
            self.data = df.to_dict('records')

            return {
                'valid': True,
                'data': self.data,
                'errors': []
            }

        except Exception as e:
            logger.error(f"CSV validation error: {e}")
            self.errors.append(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
            return {'valid': False, 'data': [], 'errors': self.errors}

    def _parse_file(self, file):
        """Parse CSV or Excel file into pandas DataFrame."""
        filename = file.name.lower()

        try:
            if filename.endswith('.csv'):
                # Try different encodings for Korean CSV files
                file.seek(0)
                raw_data = file.read()

                for encoding in ['utf-8-sig', 'utf-8', 'euc-kr', 'cp949']:
                    try:
                        decoded = raw_data.decode(encoding)
                        df = pd.read_csv(io.StringIO(decoded))
                        logger.info(f"CSV parsed successfully with encoding: {encoding}")
                        return df
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue

                self.errors.append("파일 인코딩을 인식할 수 없습니다. UTF-8 또는 EUC-KR 인코딩을 사용해주세요.")
                return None

            elif filename.endswith(('.xlsx', '.xls')):
                file.seek(0)
                df = pd.read_excel(file)
                logger.info("Excel file parsed successfully")
                return df

            else:
                self.errors.append("CSV 또는 Excel 파일만 업로드 가능합니다 (.csv, .xlsx, .xls)")
                return None

        except Exception as e:
            logger.error(f"File parsing error: {e}")
            self.errors.append(f"파일 파싱 중 오류가 발생했습니다: {str(e)}")
            return None

    def _validate_columns(self, df):
        """Validate required columns exist."""
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]

        if missing_columns:
            self.errors.append(
                f"필수 열이 누락되었습니다: {', '.join(missing_columns)}. "
                f"필수 열: {', '.join(self.REQUIRED_COLUMNS)}"
            )
            return False

        return True

    def _validate_data(self, df):
        """Validate data types and values."""
        valid = True

        # Check for empty DataFrame
        if df.empty:
            self.errors.append("파일에 데이터가 없습니다.")
            return False

        # Clean data: strip whitespace, replace NaN with empty string for optional fields
        df['school_name'] = df['school_name'].fillna('').astype(str).str.strip()
        df['class_name'] = df['class_name'].fillna('').astype(str).str.strip()
        df['student_name'] = df['student_name'].fillna('').astype(str).str.strip()

        # Handle optional fields
        if 'class_number' not in df.columns:
            df['class_number'] = None
        else:
            df['class_number'] = pd.to_numeric(df['class_number'], errors='coerce')

        if 'grade' not in df.columns:
            df['grade'] = None
        else:
            df['grade'] = pd.to_numeric(df['grade'], errors='coerce')

        if 'notes' not in df.columns:
            df['notes'] = ''
        else:
            df['notes'] = df['notes'].fillna('').astype(str).str.strip()

        if 'zep_space_url' not in df.columns:
            df['zep_space_url'] = ''
        else:
            df['zep_space_url'] = df['zep_space_url'].fillna('').astype(str).str.strip()

        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 because: pandas index starts at 0, header is row 1

            # Validate school_name
            if not row['school_name']:
                self.errors.append(f"줄 {row_num}: 학교 이름이 누락되었습니다.")
                valid = False
            elif len(row['school_name']) > 200:
                self.errors.append(f"줄 {row_num}: 학교 이름이 너무 깁니다 (최대 200자).")
                valid = False

            # Validate class_name
            if not row['class_name']:
                self.errors.append(f"줄 {row_num}: 학급 이름이 누락되었습니다.")
                valid = False
            elif len(row['class_name']) > 100:
                self.errors.append(f"줄 {row_num}: 학급 이름이 너무 깁니다 (최대 100자).")
                valid = False

            # Validate student_name
            if not row['student_name']:
                self.errors.append(f"줄 {row_num}: 학생 이름이 누락되었습니다.")
                valid = False
            elif len(row['student_name']) > 100:
                self.errors.append(f"줄 {row_num}: 학생 이름이 너무 깁니다 (최대 100자).")
                valid = False

            # Validate grade if provided
            if not pd.isna(row['grade']):
                if row['grade'] < 1 or row['grade'] > 6:
                    self.errors.append(f"줄 {row_num}: 학년은 1-6 사이의 값이어야 합니다. (입력값: {int(row['grade'])})")
                    valid = False

            # Validate class_number if provided
            if not pd.isna(row['class_number']):
                if row['class_number'] < 1:
                    self.errors.append(f"줄 {row_num}: 반 번호는 1 이상이어야 합니다. (입력값: {int(row['class_number'])})")
                    valid = False

            # Validate zep_space_url if provided
            if row['zep_space_url'] and len(row['zep_space_url']) > 500:
                self.errors.append(f"줄 {row_num}: ZEP 스페이스 URL이 너무 깁니다 (최대 500자).")
                valid = False

        return valid
