from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class UserPasswordChangeForm(PasswordChangeForm):
    """
    Form allowing any authenticated user to change their account password.
    Provides Sinhala and English labels, Bootstrap/clean CSS classes,
    and localized error messages.
    """
    error_messages = {
        'password_incorrect': 'ඔබගේ පැරණි මුරපදය වැරදිය. කරුණාකර නැවත ඇතුළත් කරන්න. (Your old password was entered incorrectly.)',
        'password_mismatch': 'ඇතුළත් කළ නව මුරපද දෙක එකිනෙකට නොගැළපේ. (The two new password fields did not match.)',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'වත්මන් මුරපදය (Current Password)'
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'වත්මන් මුරපදය ඇතුළත් කරන්න',
            'autocomplete': 'current-password',
            'required': True,
        })
        self.fields['new_password1'].label = 'නව මුරපදය (New Password)'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'අවම වශයෙන් අක්ෂර 8 ක නව මුරපදයක් ඇතුළත් කරන්න',
            'autocomplete': 'new-password',
            'required': True,
        })
        self.fields['new_password2'].label = 'නව මුරපදය නැවත තහවුරු කරන්න (Confirm New Password)'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'නව මුරපදය නැවත ඇතුළත් කරන්න',
            'autocomplete': 'new-password',
            'required': True,
        })
