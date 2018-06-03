from django import forms
from django.core.exceptions import ValidationError
from material import Layout, Row

from accounts.models import Patient
from deceases.models import PatientDecease, Decease


class PatientDeceaseForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}), required=False)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), widget=forms.HiddenInput(), required=False)
    decease = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'decease-input', 'placeholder': 'Start input decease'}))

    class Meta:
        model = PatientDecease
        fields = ['patient', 'start_date', 'end_date', 'cured']

    layout = Layout(Row('decease', 'start_date', 'end_date', 'cured'))

    def clean_decease(self):
        if self.prefix:
            decease_name = self.data[self.prefix + '-decease']
        else:
            decease_name = self.data['decease']
        if not Decease.objects.filter(name=decease_name).exists():
            raise ValidationError('no such decease')
        return decease_name
