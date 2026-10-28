from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout
# from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignupForm,LoginForm,DecisionForm,ProfileForm
from .models import Decision,Profile
from .assistant import assistant_reply

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request,'signup.html',{'form':form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            login(request,form.get_user())
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request,'login.html',{'form':form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    decisions = request.user.decisions.all()
    finished = decisions.exclude(status='in_progress')
    correct= sum(
        1 for d in finished
        if(d.predicted_chance >=50) == (d.status == 'completed')
    )
    accuracy = f"{round(correct * 100 / finished.count())}%" if finished.exists() else '--' 
    stats = {
        'total': decisions.count(),
        'completed':decisions.filter(status='completed').count(),
        'in_progress':decisions.filter(status='in_progress').count(),
        'accuracy':accuracy,
    }
    recent = decisions.first()
    return render(request, 'dashboard.html',{
        'stats':stats,
        'username':request.user.username,
        'recent':recent,
    })

@login_required
def new_decision(request):
    if request.method == 'POST':
        form = DecisionForm(request.POST)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.user=request.user
            decision.predicted_chance=decision.predict()
            decision.save()
            sync_learning_goals(request.user)
            return redirect('decision_detail',pk=decision.pk)
    else:
        form = DecisionForm()
    return render(request,'new_decision.html',{'form':form})

@login_required
def decision_detail(request,pk):
    decision = get_object_or_404(Decision,pk=pk,user=request.user)
    whatif = None
    try:
        h=float(request.GET.get('hours', ''))
        if 0 < h <= 16:
            whatif = {'hours': h, 'chance': decision.predict(daily_hours=h)}
    except ValueError:
        pass
    return render(request, 'decision_detail.html', {
        'decision': decision,
        'chance': decision.predict(),
        'required': decision.required_daily_hours(),
        'whatif':whatif,
    })


@login_required
def whatif_view(request):
    decisions= request.user.decisions.filter(status='in_progress')
    selected=None
    scenarios=[]
    pk = request.GET.get('decision', '')
    if pk.isdigit():
        selected = decisions.filter(pk=pk).first()
    if selected:
        for h in [1,2,3,4,5,6]:
            scenarios.append({'hours':h, 'chance':selected.predict(daily_hours=h)})
    return render(request, 'whatif.html', {
        'decisions': decisions,
        'selected': selected,
        'scenarios':scenarios,
    })

@login_required
def decision_list(request):
    decisions = request.user.decisions.all()
    return render(request, 'decision_list.html', {'decisions':decisions})

@login_required
def update_status(request, pk):
    
    decision = get_object_or_404(Decision, pk=pk, user=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        
        if status in ('in_progress', 'completed', 'not_completed'):
            decision.status = status
            decision.save()
            
    return redirect('decision_detail', pk=pk)


def sync_learning_goals(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.learning_goals = ", ".join(user.decisions.values_list('goal', flat=True))
    profile.save()
    return profile


@login_required
def profile_view(request):
    profile=sync_learning_goals(request.user)
    saved = False
    if request.method == 'POST':
        form = ProfileForm(request.POST,instance=profile)
        if form.is_valid():
            form.save()
            saved = True
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form, 'saved':saved})

@login_required
def assistant_view(request):
    question = ''
    answer = None
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            answer = assistant_reply(request.user,question)
    return render(request, 'assistant.html', {'question': question, 'answer':answer})
