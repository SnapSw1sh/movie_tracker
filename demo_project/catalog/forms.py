from django import forms
from .models import Review, ListEntry, Work, Comment

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите вашу рецензию…'
            }),
            'rating': forms.NumberInput(attrs={
                'min': 0,
                'max': 10,
                'placeholder': 'Оценка (0–10)'
            }),
        }
        labels = {
            'text': 'Текст рецензии',
            'rating': 'Оценка',
        }

class ListEntryForm(forms.ModelForm):
    class Meta:
        model = ListEntry
        fields = [
            'work', 'status', 'score', 'progress',
            'start_date', 'finish_date',
            'rewatch_count', 'favorite', 'notes',
        ]
        widgets = {
            'score': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'max': '10',                                        
            }),
            'progress': forms.NumberInput(attrs={'min': 0}),
            'rewatch_count': forms.NumberInput(attrs={'min': 0}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'finish_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows':3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['work'].queryset = Work.objects.exclude(list_entries__user=user)

        entry = self.instance
        if entry and entry.work_id:
            new_choices = []
            for value, label in self.fields['status'].choices:
                film_label, book_label = label.split('/')
                display = book_label if entry.work.type == Work.BOOK else film_label
                new_choices.append((value, display))
            self.fields['status'].choices = new_choices

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Ваш комментарий…'
            }),
        }
        labels = {
            'text': '',
        }
