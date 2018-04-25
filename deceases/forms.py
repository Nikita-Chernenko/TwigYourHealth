from django import forms
from material import Layout, Row

from accounts.models import Patient
from deceases.models import PatientDecease


class PatientDeceaseForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), widget=forms.HiddenInput(), required=False)
    decease = forms.CharField(widget=forms.TextInput(attrs={'class':'decease-input'}))
    class Meta:
        model = PatientDecease
        fields = ['patient', 'start_date', 'cured']

    layout = Layout(Row('decease', 'start_date', 'cured'))
