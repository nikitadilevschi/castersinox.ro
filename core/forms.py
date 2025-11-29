from django import forms
from .models  import Category

class ContactForm(forms.Form):
    fullname = forms.CharField(
        label="Nume",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-input", "id": "fullname"})
    )
    email = forms.EmailField(
        label="Adresa de Email",
        widget=forms.EmailInput(attrs={"class": "form-input", "id": "email", "required": True})
    )
    phone = forms.CharField(
        label="Nr Telefon",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "id": "phone"})
    )
    company = forms.CharField(
        label="Nume Companie",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "id": "company"})
    )
    message = forms.CharField(
        label="Mesaj",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-textarea", "id": "message", "rows": 3})
    )

    features_used = forms.ModelMultipleChoiceField(
        label="Vreau ofertă pentru",
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-checkbox"}),
        required=True
    )

    testimonial_consent = forms.BooleanField(
        label="Sunt de acord cu prelucrare a datelor cu caracter personal în sistemul CRM al CASTERS RODISTRIBUTION SRL.",
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox", "id": "testimonial-consent"})
    )