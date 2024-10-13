😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭😭

为什么github和huggingface不让我访问！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！

* 下载V2ray ，可以本地下载再上传到linux服务器

```wget
wget https://github.com/v2fly/v2ray-core/releases/download/v5.20.0/v2ray-linux-64.zip
```

* 解压安装包:

```unzip
unzip v2ray-linux-64.zip
```

* 安装v2ray

```install
install ./v2ray /usr/local/bin/v2ray 
install ./v2ctl /usr/local/bin/v2ctl
```

* 配置config.json文件

可以用自己的本地代理导出后上传到同级目录下

* 启动，同级目录下运行

```me
./v2ray -config config.json
```

测试代理，这里的地址根据config.json中的修改，比如我的：

```ce
curl --socks5 127.0.0.1:10808 http://www.google.com
```

* 其它

如果终端或git需要代理可以使用根据自己的config.json修改，细节可以问chatgpt ，比如我的

```me
git config --global http.proxy "socks5://127.0.0.1:10808"
git config --global https.proxy "socks5://127.0.0.1:10808"
```
