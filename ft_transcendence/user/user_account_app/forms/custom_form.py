from django import forms
import re


class TwoFaForm(forms.Form):
    token = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter 6-digit code",
                "class": "form-control form-control-user",
            }
        ),
    )

    def clean_token(self):
        token = self.cleaned_data.get("token")
        # Check if the token is a 6-digit number
        if not re.match(r"^\d{6}$", token):
            raise forms.ValidationError("Please enter a valid 6-digit code.")
        return token
