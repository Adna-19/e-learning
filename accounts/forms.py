from django import forms
from .models import StudentProfile, InstructorProfile, User

class SignUpForm(forms.Form):
	username  				= forms.CharField(max_length=20)
	gender  					= forms.ChoiceField(choices=(('M','Male'),('F', 'Female')))
	email  					  = forms.EmailField()
	password 					= forms.CharField(widget=forms.PasswordInput)
	confirm_password  = forms.CharField(widget=forms.PasswordInput)

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)
		for field_name in self.fields.keys():
			self.fields[field_name].widget.attrs.update({'class': 'form-control'})

	def clean_username(self):
		username = self.cleaned_data.get('username')
		alread_used_usernames = [user.username for user in User.objects.all()]
  
		if username in alread_used_usernames:
			raise forms.ValidationError("Username already in use.")
		return username

	def clean_confirm_password(self):
		passowrd1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('confirm_password')

		if passowrd1 != password2:
			raise forms.ValidationError('Mismatched Password')
		return password2

class StudentProfileSettingForm(forms.ModelForm):
	username   = forms.CharField(max_length=50)
	first_name = forms.CharField(max_length=20)
	last_name  = forms.CharField(max_length=20)
	email      = forms.EmailField()

	def __init__(self, user, *args, **kwargs):
		super(StudentProfileSettingForm, self).__init__(*args, **kwargs)
		self.fields['username'].initial = user.username
		self.fields['first_name'].initial = user.first_name
		self.fields['last_name'].initial = user.last_name
		self.fields['email'].initial = user.email

	class Meta:
		model = StudentProfile
		fields = ('username', 'first_name', 'last_name', 'email', 'bio')

class IntructorProfileSettingForm(forms.ModelForm):
	username   = forms.CharField(max_length=50)
	first_name = forms.CharField(max_length=20)
	last_name  = forms.CharField(max_length=20)
	email      = forms.EmailField()

	def __init__(self, user, *args, **kwargs):
		super(IntructorProfileSettingForm, self).__init__(*args, **kwargs)
		self.fields['username'].initial = user.username
		self.fields['first_name'].initial = user.first_name
		self.fields['last_name'].initial = user.last_name
		self.fields['email'].initial = user.email

	class Meta:
		model  = InstructorProfile
		fields = ('username', 'first_name', 'last_name', 'email', 'about')
