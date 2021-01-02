from django.shortcuts import redirect
from django.contrib.auth import logout

# Create your views here.
def logout_view(request):
	logout(request)
	if request.GET.get("next"):
		return redirect(request.GET.get("next"))
	else:
		return redirect('/')