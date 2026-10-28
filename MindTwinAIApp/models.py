# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    LEVEL_CHOICES=[
        ('10','class 10'),
        ('11-12', 'class 11-12'),
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate (Masters)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=10,choices=LEVEL_CHOICES,default='UG')
    learning_goals = models.CharField(blank=True)
    daily_study_hours = models.PositiveIntegerField(default=2)

    def __str__(self):
        return f"{self.user.username}({self.education_level})"

from datetime import date
class Decision(models.Model):
    CATEGORY_CHOICES = [
        ('skill','Skill Development'),
        ('exam', 'Exam Preparation'),
        ('academics', 'Academics'),
        ('project', 'Project'),
        ('personal', 'Personal Development'),
    ]
    STATUS_CHOICES=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('not_completed', 'Not Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decisions')
    goal = models.CharField(max_length=150)
    category = models.CharField(max_length=20,choices=CATEGORY_CHOICES)
    daily_hours = models.DecimalField(max_digits=4,decimal_places=1)
    total_hours = models.DecimalField(max_digits=6,decimal_places=1)
    hours_done = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='in_progress')
    predicted_chance = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.goal} ({self.user.username})"


    def days_left(self):
        return(self.deadline - date.today()).days

    def remaining_hours(self):
        return max(float(self.total_hours - self.hours_done),0)

    def required_daily_hours(self):
        days = self.days_left()
        if days <=0:
            return None
        return round(self.remaining_hours() / days,1)

    def predict(self,daily_hours=None):
        """Goal Poora hone ka chance (%) deta hai.daily_hours badal ke what-if bhi dekh sakta ho."""
        daily = float(daily_hours if daily_hours is not None else self.daily_hours)
        remaining = self.remaining_hours()
        days = self.days_left()
        if remaining == 0:
            return 100
        if days <=0:
            return 0
        # assume ki din ka only 80% plan follow hota hai
        available = daily * days * 0.8
        ratio = available / remaining
        return max(5,min(95,int(ratio*80)))
    