# firewalld_jponly
firewalldでhttpを日本のIPアドレスのみ許可する

## 概要

- 日本のIPアドレスを取得しfirewalldのゾーンに設定する
- IPの取得先は「https://ipv4.fetus.jp/jp」から
- ゾーンに設定するときはsourceとしてIPを設定する

※設定時に既存のsource設定内容をクリアしたかったが、firewall-cmdでどうやって一括して消すか不明だっため、
ゾーンのxmlファイルを直接修正することにした。

※firewall-cmdで既に登録してある同じ設定を実行してもコマンド側で既に登録済みと判断してくれる様子。  

## 環境

| - | バージョン |
|:------|:------|
| CentOS | 7.2 |
| firewalld | 0.3.9 |
| Python | 2.7.5 |

## 前準備

日本のIPアドレスのみを設定するゾーンファイルをあらかじめ作成しておく
```
cp -a /usr/lib/firewalld/zones/public.xml /etc/firewalld/zones/jponly.xml
chmod 644 /etc/firewalld/zones/jponly.xml
firewall-cmd --reload
```

不要なサービスを削除
```
firewall-cmd --permanent --remove-service=dhcpv6-client --zone=jponly
firewall-cmd --permanent --remove-service=ssh --zone=jponly
firewall-cmd --reload

## 確認
firewall-cmd --list-services --zone=jponly

## 今回はhttpだけが残っていればOK
[root@localhost ~]# firewall-cmd --list-services --zone=jponly
http
```


## コマンド

##### 以下の作業は念のためコンソールで作業したほうがよい

「jp.txt」のダウンロード
```
wget --no-check-certificate https://ipv4.fetus.jp/jp.txt
```

jp.txtからIPv4のCIDRを抜き取り、ゾーンファイル(jponly)へSourceとして書き込む  
```
python create_ipv4jp_zone.py

## 実行するとfirewall-cmd-jponly.shも一緒に作成している(firewall-cmdでsourceを追加するシェル)
## 特に使う必要はないと思うがゾーンの設定が上手くいかない場合に、後で手動で実行できるように作成した。
```

ゾーンのxmlファイルを修正しただけなのでまだ設定は有効ではない。


ゾーンの設定内容を確認  
※permanentオプションをつけているのでここで表示されるのは再起動後に有効になる設定内容

```
firewall-cmd --permanent --zone=jponly --list-all
```


設定内容のリロードの前に以下を必ず行う。  
```
firewall-cmd --permanent --add-service=http --zone=jponly

## 既にゾーンにhttpサービスは登録してあっても必ず実行する。
## firewall-cmdで実行することでゾーンXMLファイルを整理・最適化してくれる。
## ※ファイルサイズが減り中身を見ると余計な改行や空白を除去している。
## また、必ずsourceタグの後にserviceタグが並ぶようになる。
## ※実行しないままリロードすると以下のエラーが出て起動しなくなった。(反応が遅かっただけ？)
ERROR:dbus.proxies:introspect error on :1.2:/org/fedoraproject/FirewallD1/config:
dbus.exceptions.DBusException: org.freedesktop.DBus.Error.NoReply: 
Did not receive a reply. Possible causes include: the remote application did not send a reply,
the messeage bus security policy blocked the reply, the reply timeout expired or the network connection was broken.

```


リロードすることで設定内容を反映する
※量が多い為か、かなり時間がかかった(３分〜５分)
```
firewall-cmd --reload
```

ゾーンの設定内容を確認
```
firewall-cmd --zone=jponly --list-all
```

## 課題・検討

* --reloadの時に時間がかかる
* jp.txtは手動でなくcreate_ipv4jp_zone.py内でダウンロード

