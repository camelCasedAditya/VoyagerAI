from django import forms

class AgentForm(forms.Form):
    agent_query = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label="Tell us about yourself", help_text="Write a few paragraphs.")