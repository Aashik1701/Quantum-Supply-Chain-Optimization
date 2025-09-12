"""
Unit tests for upload service functionality
"""

import pytest
from unittest.mock import Mock, patch
from services.database_data_service import DatabaseDataService
from utils.exceptions import ValidationError as DomainValidationError


class TestUploadService:
    """Test the upload service functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = DatabaseDataService()

    def test_process_upload_success(self):
        """Test successful file upload processing"""
        # Create a mock file object
        file_content = (
            "id,name,country,latitude,longitude,capacity,operating_cost\n"
            "W1,Test,USA,40.0,-74.0,1000,500"
        )
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.read.return_value = file_content.encode('utf-8')
        mock_file.seek = Mock()

        # Mock the CSV processing method
        with patch.object(
            self.service, 'process_csv_upload'
        ) as mock_process_csv:
            mock_process_csv.return_value = {
                'success': True,
                'count': 1,
                'message': 'Successfully uploaded 1 warehouses'
            }
            
            result = self.service.process_upload(mock_file, 'warehouses')
            
            assert result['success'] is True
            assert result['count'] == 1
            mock_process_csv.assert_called_once_with(
                file_content, 'warehouses'
            )

    def test_process_upload_no_file(self):
        """Test upload with no file"""
        with pytest.raises(DomainValidationError, match="No file provided"):
            self.service.process_upload(None, 'warehouses')

    def test_process_upload_no_filename(self):
        """Test upload with no filename"""
        mock_file = Mock()
        mock_file.filename = None
        
        with pytest.raises(DomainValidationError, match="No file provided"):
            self.service.process_upload(mock_file, 'warehouses')

    def test_process_upload_invalid_extension(self):
        """Test upload with invalid file extension"""
        mock_file = Mock()
        mock_file.filename = "test.txt"
        
        with pytest.raises(
            DomainValidationError, match="Only CSV files are supported"
        ):
            self.service.process_upload(mock_file, 'warehouses')

    def test_process_upload_invalid_data_type(self):
        """Test upload with invalid data type"""
        mock_file = Mock()
        mock_file.filename = "test.csv"
        
        with pytest.raises(DomainValidationError, match="Invalid data type"):
            self.service.process_upload(mock_file, 'invalid_type')

    def test_process_upload_empty_file(self):
        """Test upload with empty file"""
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.read.return_value = b""
        mock_file.seek = Mock()
        
        with pytest.raises(
            DomainValidationError, match="File content is empty"
        ):
            self.service.process_upload(mock_file, 'warehouses')

    def test_process_upload_unicode_decode_error(self):
        """Test upload with invalid encoding"""
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.read.return_value = b'\xff\xfe'  # Invalid UTF-8
        mock_file.seek = Mock()
        
        with pytest.raises(
            DomainValidationError, match="File must be UTF-8 encoded"
        ):
            self.service.process_upload(mock_file, 'warehouses')

    def test_process_upload_file_too_large(self):
        """Test upload with file that's too large"""
        # Create a file content larger than 10MB
        large_content = "a" * (11 * 1024 * 1024)  # 11MB
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.read.return_value = large_content.encode('utf-8')
        mock_file.seek = Mock()
        
        with pytest.raises(
            DomainValidationError, match="File size must be less than 10MB"
        ):
            self.service.process_upload(mock_file, 'warehouses')

    def test_process_upload_csv_processing_error(self):
        """Test upload when CSV processing fails"""
        file_content = "id,name,country\nW1,Test,USA"
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.read.return_value = file_content.encode('utf-8')
        mock_file.seek = Mock()

        # Mock CSV processing to raise an error
        with patch.object(
            self.service, 'process_csv_upload'
        ) as mock_process_csv:
            mock_process_csv.side_effect = DomainValidationError(
                "CSV processing failed"
            )
            
            with pytest.raises(
                DomainValidationError, match="CSV processing failed"
            ):
                self.service.process_upload(mock_file, 'warehouses')
