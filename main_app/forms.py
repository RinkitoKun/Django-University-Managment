from django import forms
from .models import AssignmentSubmission, Library


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file']

class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = ['book_name', 'book_description', 'category', 'quantity', 'book_cover']


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)