from django import forms
from material import Layout, Row

from deceases.models import PatientDecease


class PatientDeceaseForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = PatientDecease
        fields = ['decease', 'start_date', 'cured']

    layout = Layout(Row('decease', 'start_date', 'cured'))