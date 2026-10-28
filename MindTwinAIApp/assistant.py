def _accuracy(decision):
    finished = decision.exclude(status ='in_progress')
    if not finished.exists():
        return None
    correct = sum(
        1 for d in finished
        if (d.predicted_chance >= 50) == (d.status == 'completed')
    )
    return round(correct * 100 / finished.count())

def assistant_reply(user,question):
    q = question.lower()
    decisions = user.decisions.all()
    active = list(decisions.filter(status='in_progress'))

    if not decisions.exists():
        return "You have no goals yet. Add one from New Decision and I can help you plan it."

    # Most at-risk goal
    if any(w in q for w in ['risk', 'behind', 'worst', 'lowest']):
        if not active:
            return "You have no goals in progress right now."
        d = min(active, key=lambda x: x.predict())
        return (f"Your most at-risk goal is '{d.goal}' with a {d.predict()}% chance)"
                 f"of finishing on time. It has {d.days_left()} days left.")

    # Hours needed per day
    if any(w in q for w in ['hour', 'daily', 'how much', 'study' ]):
        if not active:
            return "You have no goals in progress right now."
        lines = []
        for d in active:
            need = d.required_daily_hours()
            if need is None:
                lines.append(f"'{d.goal}': the deadline has passed.")
            else:
                lines.append(f"'{d.goal}': needs {need} hours/day (you planned {d.daily_hours}).")
        return "".join(lines)

    # nearest deadline
    if any(w in q for w in ['deadline', 'due', 'soon', 'urgent', 'first']):
        if not active:
            return "You have no goals in progress right now."
        d = min(active, key=lambda x: x.deadline)
        return f"Your nearest deadline is '{d.goal}' on {d.deadline}, which is {d.days_left()} days away."

    # Accuracy
    if any(w in q for w in ['accuracy', 'correct', 'right', 'reliable']):
        acc = _accuracy(decisions)
        if acc is None:
            return ("I can't measure accuracy yet. Mark a goal as Completed or Not Completed"
                    "and I will compare it with my prediction.")
        return f"My predictions matched the real result {acc}% of thr time on your finished goals."
    
    # summary
    if any(w in q for w in ['summary', 'progress', 'status', 'overview']):
        done = decisions.filter(status='completed').count()
        return (f"You have {decisions.count()} goals: {len(active)} in progress "
                f"and {done} completed.")

    return ("I can answer questions about your goals. Try:"
            "Which goal is most at risk?', 'How many hours do I need per day?,"
            "Which deadline is nearest?' or 'How accurate are you?'")