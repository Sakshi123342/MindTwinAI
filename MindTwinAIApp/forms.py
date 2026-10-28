from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from.models import Profile,Decision
from datetime import date

class SignupForm(UserCreationForm):
    username= forms.CharField(max_length=30,label='Username',help_text='Only letters are allowed.',)
    email = forms.EmailField(required=True)
    education_level = forms.ChoiceField(choices=Profile.LEVEL_CHOICES)
    field_order = ['username', 'email', 'education_level', 'password1', 'password2']
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Use letters, numbers and a special character (min 8).'
        self.fields['password2'].help_text = ''

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username.isalpha():
            raise forms.ValidationError('Only letters are allowed in username.')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            has_letter = any(ch.isalpha() for ch in password)
            has_number = any(ch.isdigit() for ch in password)
            has_special = any(not ch.isalnum() for ch in password)
            if not (has_letter and has_number and has_special):
                raise forms.ValidationError(
                    'Password must contain a letter, a number and a special character.'
                )
        return password


    def save(self,commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                education_level=self.cleaned_data['education_level'],
            )
        return user
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')

class DecisionForm(forms.ModelForm):
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))

    class Meta:
        model = Decision
        fields = ['goal','category','daily_hours','total_hours','deadline']

    def clean_deadline(self):
        d = self.cleaned_data['deadline']
        if d <= date.today():
            raise forms.ValidationError('Deadline must be a future date.')
        return d

    def clean_daily_hours(self):
        h = self.cleaned_data['daily_hours']
        if h <= 0 or h>16:
            raise forms.ValidationError('Daily hours must be more than 0 and at most 16.')
        return h 

    def clean_total_hours(self):
        h = self.cleaned_data['total_hours']
        if h<=0:
            raise forms.ValidationError('Total hours must be more than 0.')
        return h

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['education_level','learning_goals', 'daily_study_hours']
        widgets = {
            'learning_goals': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Your goals will appear here automatically',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['learning_goals'].disabled = True   # user edit nahi karega, automatic bharega

    def clean_daily_study_hours(self):
        h = self.cleaned_data['daily_study_hours']
        if h > 16:
            raise forms.ValidationError('Daily study hours must be at most 16.')
        return h