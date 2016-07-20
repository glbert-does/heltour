from django.shortcuts import render, redirect
from .models import *
from .forms import *

def pairings(request):
    try:
        season = Season.objects.order_by('-start_date')[0]
        round_ = Round.objects.filter(season=season).order_by('-number')[0]
    except IndexError:
        return no_pairings_available(request)
    return pairings_by_season(request, season.id, round_.number)

def pairings_by_round(request, round_number):
    try:
        season = Season.objects.order_by('-start_date')[0]
    except IndexError:
        return no_pairings_available(request)
    return pairings_by_season(request, season.id, round_number)

def pairings_by_season(request, season_id, round_number):
    team_pairings = TeamPairing.objects.filter(round__number=round_number, round__season__id=season_id)
    if len(team_pairings) == 0:
        return no_pairings_available(request)
    pairing_lists = [team_pairing.pairing_set.order_by('board_number') for team_pairing in team_pairings]
    context = {
        'round_number': round_number,
        'pairing_lists': pairing_lists
    }
    return render(request, 'tournament/pairings.html', context)

def no_pairings_available(request):
    context = {
    }
    return render(request, 'tournament/no_pairings.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return redirect('/register_success/')
    else:
        form = RegistrationForm()
    return render(request, 'tournament/register.html', {'form': form})

def register_success(request):
    context = {
    }
    return render(request, 'tournament/register_success.html', context)

def home(request):
    return redirect('/pairings/')

def faq(request):
    context = {
    }
    return render(request, 'tournament/faq.html', context)

def rosters(request):
    context = {
    }
    return render(request, 'tournament/rosters.html', context)

def standings(request):
    context = {
    }
    return render(request, 'tournament/standings.html', context)

def crosstable(request):
    context = {
    }
    return render(request, 'tournament/crosstable.html', context)

def stats(request):
    context = {
    }
    return render(request, 'tournament/stats.html', context)