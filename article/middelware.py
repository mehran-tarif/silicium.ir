import datetime
from .models import IpAddress


class SaveIpAddressMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response
		# One-time configuration and initialization.

	def __call__(self, request):
		# Code to be executed for each request before
		# the view (and later middleware) are called.
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[-1].strip()
		else:
			ip = request.META.get('REMOTE_ADDR')
		try:
			ip_address = IpAddress.objects.get(ip_address=ip)
		except IpAddress.DoesNotExist:             #-----Here My Edit
			ip_address = IpAddress(ip_address=ip, pub_date=datetime.datetime.now())
			ip_address.save()
		request.user.ip_address = ip_address

		response = self.get_response(request)

		# Code to be executed for each request/response after
		# the view is called.

		return response