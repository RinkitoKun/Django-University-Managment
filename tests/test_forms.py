import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from main_app.forms import (
    LoginForm,
    AssignmentSubmissionForm, 
    BookUploadForm,
    PasswordResetForm
)

class TestLoginForm:
    def test_login_form_valid_data(self):
        form = LoginForm(data={
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        assert form.is_valid()

    def test_login_form_invalid_email(self):
        form = LoginForm(data={
            'email': 'invalid-email',
            'password': 'testpassword123'
        })
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_login_form_no_data(self):
        form = LoginForm(data={})
        assert not form.is_valid()
        assert 'email' in form.errors
        assert 'password' in form.errors

class TestAssignmentSubmissionForm:
    def test_assignment_submission_form_valid_file(self):
        file = SimpleUploadedFile("test_file.txt", b"file_content")
        form = AssignmentSubmissionForm(
            files={'file': file}
        )
        assert form.is_valid()

    def test_assignment_submission_form_no_file(self):
        form = AssignmentSubmissionForm(files={})
        assert not form.is_valid()
        assert 'file' in form.errors

class TestBookUploadForm:
    @pytest.fixture
    def valid_form_data(self):
        return {
            'book_name': 'Test Book',
            'book_description': 'Test Description',
            'category': 'COMPUTER_SCIENCE',
            'quantity': 5,
            'status': 'AVAILABLE'  # Add the required status field
        }
    
    @pytest.fixture
    def valid_file_data(self):
        # Use a valid image file content
        cover = SimpleUploadedFile(
            "test_cover.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x0A\x00\x01\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B",
            content_type="image/jpeg"
        )
        return {'book_cover': cover}

    def test_book_upload_form_valid_data(self, valid_form_data, valid_file_data):
        form = BookUploadForm(
            data=valid_form_data,
            files=valid_file_data
        )
        if not form.is_valid():
            print("Form errors:", form.errors)  # For debugging
        assert form.is_valid()

    def test_book_upload_form_missing_required_fields(self):
        form = BookUploadForm(data={})
        assert not form.is_valid()
        assert 'book_name' in form.errors
        assert 'category' in form.errors
        assert 'quantity' in form.errors

    def test_book_upload_form_invalid_quantity(self, valid_form_data):
        valid_form_data['quantity'] = -1  # Invalid negative quantity
        form = BookUploadForm(data=valid_form_data)
        assert not form.is_valid()
        assert 'quantity' in form.errors

    def test_book_upload_form_without_cover(self, valid_form_data):
        # Test that form is valid even without a cover (since it's optional)
        form = BookUploadForm(data=valid_form_data)
        assert form.is_valid()

class TestPasswordResetForm:
    def test_password_reset_form_valid_email(self):
        form = PasswordResetForm(data={
            'email': 'test@example.com'
        })
        assert form.is_valid()

    def test_password_reset_form_invalid_email(self):
        form = PasswordResetForm(data={
            'email': 'invalid-email'
        })
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_password_reset_form_no_data(self):
        form = PasswordResetForm(data={})
        assert not form.is_valid()
        assert 'email' in form.errors

    @pytest.mark.parametrize('email', [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+test@example.com',
    ])
    def test_password_reset_form_valid_email_formats(self, email):
        form = PasswordResetForm(data={'email': email})
        assert form.is_valid()

    @pytest.mark.parametrize('email', [
        '@example.com',
        'test@',
        'test@.com',
        'test@example.',
        'test.example.com',
    ])
    def test_password_reset_form_invalid_email_formats(self, email):
        form = PasswordResetForm(data={'email': email})
        assert not form.is_valid()
