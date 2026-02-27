from django.shortcuts import render
from .forms import AgentForm

# Create your views here.
def agent_query(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            agent_query = form.cleaned_data['agent_query']
            return render(request, 'travel/agent_query.html', {'form': form, 'success': True})
    else:
        form = AgentForm()
    
    return render(request, 'travel/agent_query.html', {'form': form})