from django import forms

# Django form to handle user input for trip planning query
class AgentForm(forms.Form):
    agent_query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter travel plan here...',
            'aria-label': 'Text input'
        }), 
        label=""
    )