# Django 權限控管

## Setup (官方文件的方式)

* 安裝Django 相關套件
    * pip install django 
    * pip install djangorestframework

* 起一個新的專案
    * django-admin startproject django_auth
    * cd django_auth
    * django-admin startapp auth

* 同步資料庫 
    * python manage.py migrate

* 新增一個使用者
    * python manage.py createsuperuser --email admin@example.com --username admin 

* 新增Serializers
     * 在auth資料夾底下新增 serializers.py
        ```python
        from django.contrib.auth.models import User, Group
        from rest_framework import serializers

        class CustomUserSerializer(serializers.ModelSerializer):
            class Meta:
                model = CustomUser
                fields = '__all__'


        class UserSerializer(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'url', 'username', 'password', 'email', 'groups']
        ```

* 新增Views
    * 在auth資料夾底下新增 views.py
        ```python
        from django.contrib.auth.models import User, Group
        from rest_framework import viewsets
        from rest_framework import permissions
        from .serializers import UserSerializer, GroupSerializer
        
        class UserViewSet(viewsets.ModelViewSet):
            """
            API endpoint that allows users to be viewed or edited.
            """
            queryset = User.objects.all().order_by('-date_joined')
            serializer_class = UserSerializer
            permission_classes = [permissions.IsAuthenticated]

        class GroupViewSet(viewsets.ModelViewSet):
            """
            API endpoint that allows groups to be viewed or edited.
            """
            queryset = Group.objects.all()
            serializer_class = GroupSerializer
            permission_classes = [permissions.IsAuthenticated]
        ```

* 設定URLs
    * 在auth資料夾底下找到 urls.py
    * 新增以下內容
        ```python
        from django.contrib import admin
        from django.urls import include, path
        from rest_framework import routers
        from auth import views

        router = routers.DefaultRouter()
        router.register(r'users', views.UserViewSet)
        router.register(r'groups', views.GroupViewSet)

        urlpatterns = [
            path('', include(router.urls)),
            path('admin/', admin.site.urls),
            path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
        ]
        
        ```
        
* 設定Settings
    * 在auth資料夾底下找到 settings.py
    * 找到” INSTALLED_APPS” 新增’rest_framework’
        ```python
        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework'
        ]
        ```
        
* 啟動server
    * 執行python manage.py runserver


## 自訂義Token 機制

### 設定model
* 新增一個自訂義的 models.py 類別CustomUser
    ```python 
    from django.db import models
    from django.contrib.auth.base_user import AbstractBaseUser

    class CustomUser(AbstractBaseUser, models.Model):
        username = models.CharField(max_length=50)
        password = models.CharField(max_length=50)
        update_time = models.DateTimeField(auto_now=True)
        created_time = models.DateTimeField(auto_now_add=True)

        class Meta:
            db_table = 'custom_user'
            constraints = [
                models.UniqueConstraint(
                    fields=['username'], name='unique_username')
            ]
    ```

    * 為了要使用權限控管的機制，必須加入”AbstractBaseUser”

* 設定完model後需要下
    * python manage.py makemigrations 你的服務名稱
    * python manage.py migrate 你的服務名稱
    
    例: 我的服務名稱為”apps” 則需下
    * python manage.py makemigrations apps
    * python manage.py migrate apps

* 檢查資料庫有沒有新增”custom_user” 的table
![](https://i.imgur.com/mxinxly.png)

### 設定serializer
* 在serializers.py 新增類別CustomUserSerializer
    ```python 
    from rest_framework import serializers
    from .models import CustomUser


    class CustomUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = CustomUser
            fields = '__all__'
    ```

### 設定view
* 在views.py 新增類別CustomUserViewSet
    ```python
    import hashlib
    from datetime import datetime, timedelta

    class CustomUserViewSet(viewsets.ViewSet):
        queryset = CustomUser.objects.all()
        serializer_class = CustomUserSerializer

        @action(detail=False, methods=['post'])
        def get_user(self, request, *args, **kwargs):
            response = {}
            response['status'] = False
            username = request.data['username']
            password = request.data['password']
            try:
                queryset = CustomUser.objects.get(
                    username=username, password=password)
                serializer = CustomUserSerializer(queryset, many=True)
                today = str(datetime.today().strftime('%Y-%m-%d'))
                token_md5 = hashlib.md5()
                token_md5.update(
                    (username + password + today).encode('utf-8'))  # 設定token
                response['status'] = True
                response['token'] = token_md5.hexdigest()
                response['uid'] = queryset.id
                response['username'] = queryset.username
                response['msg'] = "登入成功"
                return Response(response)
            except:
                response['msg'] = "帳號不存在或密碼錯誤"
                return Response(response)
    ```
    
    * 此方法結合登入與產生token的功能。
    * 若登入成功則對(使用者名稱+使用者密碼+現在的日期)做md5的加密，產生一組僅限當日使用的token

### 設定url
* 在urls.py 綁定新增的View
    ```python
    from django.contrib import admin
    from django.urls import include, path
    from rest_framework import routers
    from apps import views

    router = routers.DefaultRouter()
    router.register(r'custom_users', views.CustomUserViewSet)  #新增的部分
    router.register(r'users', views.UserViewSet)
    router.register(r'groups', views.GroupViewSet)

    urlpatterns = [
        path('', include(router.urls)),
        path('admin/', admin.site.urls),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]

    ```
### 新增幾筆帳號
* 到http://localhost:8000/custom_users/ 新增幾筆使用者資訊
    ![](https://i.imgur.com/VtWJrlm.png)

* 此教學版本需要自行md5  hash後再發POST請求，避免密碼以明碼的形式儲存。線上hash網站https://passwordsgenerator.net/md5-hash-generator/


### 設定view
* 將ModelViewSet改為ViewSet
![](https://i.imgur.com/xP2iKQq.png)

* 此方法請務必要做，避免靠list與retrieve的方法試出使用者id與帳密(雖然密碼是有md5 hash過，但有帳密後有可能被試出token)。

### 認證設定
* 新增authentication.py
    ```python
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
    ```
    
* 圖解認證方法
![](https://i.imgur.com/PBFksIR.png)

### 認證設定
* 修改在views.py做的token防護機制，把自訂義的防護機制加到api
![](https://i.imgur.com/7GgAhoO.png)

### 測試
* 先從 http://localhost:8000/custom_users/get_user/ 發POST取得token
    ![](https://i.imgur.com/yHawM3a.png)
* 把token與uid記錄下來，
    * uid    是解鎖token內容的鑰匙
    * token是後端比對用的認證

* http://127.0.0.1:8000/groups/ 發GET前先在header塞入uid與token的資訊。
    ![](https://i.imgur.com/cUXIobQ.png)

* 檢查修改uid或是token的資訊還能不能取得資料
    ![](https://i.imgur.com/GKU1N9m.png)
    若能成功擋下請求則代表防護成功。

* 檢查在Group底下新增一個簡單的街口能不能防護
    ![](https://i.imgur.com/8ZrnaCH.png)
    * 對http://127.0.0.1:8000/groups/get_groups/ 發請求
        ![](https://i.imgur.com/dBMnYvb.png)


### 優缺點
* 優點:
    * 不需要額外的資料表儲存
    * Token只有當日有效
    * 可以任意修改Token產生的方式
    * 因為Token會變動所以安全性較佳
* 缺點:
    * 因為此教學版本是使用md5做hash，屬於不可逆的加密方式，因此需要使用者保存uid作為資料庫對應用的金鑰。
    * 結合django rest_framework的認證功能非常麻煩，需要去閱讀套件內認證做法的細節。
    * 官網沒有仔細說明客製化認證的做法，只有小篇幅帶過，除錯上有時候異常的麻煩。官網連結: https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication 
