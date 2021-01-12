import hashlib
from datetime import datetime, timedelta
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework import authentication
from rest_framework import exceptions

class CustomAuthentication(authentication.BaseAuthentication):
	def authenticate(self, request):
		uid = request.META.get('HTTP_UID')
		token = request.META.get('HTTP_TOKEN')
		if not uid:
			return None # 認證失敗
		try:
			queryset = CustomUser.objects.get(pk=uid)
			username = queryset.username
			password = queryset.password
			today = str(datetime.today().strftime('%Y-%m-%d'))
			token_md5 = hashlib.md5()
			token_md5.update(
				(username + password + today).encode('utf-8'))  # 設定token
			token_md5 = token_md5.hexdigest()
			if token != token_md5:
				return None
			return (queryset, None) # 認證成功

		except CustomUser.DoesNotExist:
			return None