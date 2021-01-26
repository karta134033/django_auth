# Django 權限控管

## 官方教學預設的權限控管方式
* 方法為對username:password做Base64 encoding
* 此方法是可以反推帳號密碼。
* encoding的資訊需要存在client端。

## 自訂義Token 機制
* 在views.py新增類別CustomUserViewSet
  * 此方法結合登入與產生token的功能。
  * 若登入成功則對(使用者名稱+使用者密碼+現在的日期)做md5的加密，產生一組僅限當日使用的token

* 認證設定
  * 新增authentication.py作為views綁定認證用。
  * 方法為取得uid去比對是否可組成相同的token
    * 流程圖
      ![](https://i.imgur.com/yRN1Jh2.png)
    * 此方法是自創內容並根據"django.contrib.auth.models"改寫試出來的，若要新增其他django支援的方法請參考"django.contrib.auth.models"。