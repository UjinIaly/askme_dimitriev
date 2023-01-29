from django import forms
from app.models import Question, Profile, Answer
from django.contrib.auth.models import User


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_name', 'email', 'image']


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget = forms.ClearableFileInput()


class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    repeat_password = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['repeat_password'].widget = forms.PasswordInput()

    def clean(self):
        cleaned_data = super(CreateUserForm, self).clean()
        psw = cleaned_data.get('password')
        repeat_psw = cleaned_data.get('repeat_password')

        if repeat_psw != psw:
            msg = "Passwords do not match"
            self.add_error('password', msg)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


# TODO: добавить возможность добавить свой тэг (создание тэга)
class AskForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None);
        super().__init__(*args, **kwargs);

    def save(self, commit=True, tags=None):
        question = super().save(commit=False)
        question.author = self.user.profile;

        if commit == True:
            question.save()
            if tags is not None:
                question.tags.set(tags)
        return question;


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None);
        self.question_pk = kwargs.pop('question_pk', None);
        super().__init__(*args, **kwargs);

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.user.profile;
        answer.question = Question.objects.get(pk=self.question_pk)
        if commit == True:
            answer.save()
        return answer;
