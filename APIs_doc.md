# 鸟窝习惯-接口文档
## APIs Document

制定者： Faraway \<hzylovelyl@gmail.com\>

**除非特别指出，本文档所有接口 `content-type` 均为 `application/json`**

### 界面
+ Protocol: HTTP
+ Client request format: JSON
+ Server response format: JSON

### General status code
#### Status code
| Code | Detail |
|:----:|--------|
| 200 | OK: 请求正确，返回请求内容。|
| 400 | Bad Request: 不合法的请求，可能是因为请求格式错误。|
| 403 | Forbidden: 请求的资源被拒绝存取。|
| 404 | Not Found: 请求的资源未被找到。|
| 500 | Internal Server Error: 服务端发生了不可预料的错误。|

无论结果如何，状态吗都会按以上格式返回，你需要根据状态吗来确定请求成功与否，只有 200 才是成功

#### Format
Response 以如下形式返回，其中 `error` 字段**当且仅当**存在错误是才会有

```json
{
    "error": "", // 字符串，标示错误原因
    ... // 数据
}
```

### APIs

#### 用户的基本信息如下
```json
{
    "username" : "far",
    "password" : "xxxx", // 用户密码sha1加密，这不会出现在响应体中
    "joined_nests" : [
        {
            "_id" : "59737af8f6ded61e7af0e6b9",
            "kept_days" : 0
        },
        {
            "_id" : "59737af9f6ded61e7af0e6bb",
            "kept_days" : 0
        }
    ], // 加入的鸟窝以及坚持的时间，与后面接口提供的公共信息合并即可展示
    "uploaded_musics" : [
        "597385a6f6ded65832a3c175",
        "597385a6f6deda5f2a3gc165"
    ], // 音乐id，后面接口用一个音乐文件生成
    "alarm_clocks" : [
        "597385a6f6ded65832a3c175",
        "597385aaf6ded65832a3c176"
    ], // 闹钟的 id
    "avatar" : "http://nesthabit.pek3a.qingstor.com/image/759535687779715.png"
}
```

#### 闹钟的基本信息如下

```json
{
    "_id" : "59738251c3e7e5e692429d39",
    "title" : "waaaaaaa",
    "repeat" : [
        0,
        1,
        3,
        5,
        6
    ], // 从零开始代表周日，周一，三，五，六
    "music_id" : "597385a6f6ded65832a3c175", // 为空字符串代表系统
    "duration_level" : 1, // 由高到低五个等级的第二级
    "volume_level" : 1, // 由高到低五个等级的第二级
    "nap_level" : 1, // 由高到低五个等级的第二级
    "bind_to_nest" : "59737af8f6ded61e7af0e6b9", // 鸟窝的id
    "willing_music" : true, // 第一个愿意
    "willing_text" : true, // 第二个愿意
    "created_time" : 1500742155,
    "owner" : "far", // 闹钟拥有者
    "time" : [
        7,
        0
    ] // 代表 07:00
}
```

#### 鸟窝的基本信息如下

```json
{
    "_id" : "5973730bf6ded6013fc37075",
    "name" : "aaaaaaa",
    "desc" : "aaaa",
    "members_limit" : 0, // 代表无限制
    "start_time" : 1499999999,
    "challenge_days" : 1000, // 预计坚持时间
    "cover_image" : "", // 封面图面，是个url
    "open" : true, // 是否开放
    "created_time" : 1400000000,
    "creator" : "far", // 创建者
    "owner" : "far", // 目前管理/拥有者
    "members_amount" : 1 // 总的成员数量
}
```

#### 用户的接口：

##### 登录

* url: '/user/\<username\>/session' 'POST'
* json字段: 'password', 'client_id', 'client_secret'

req:
```json
{
	"password":"8412",
	"client_id":"android_client_87542701",
	"client_secret":"385trd4m"
}
```

res:
```json
{
    "msg": "Logged in successfully!",
    "Authorization": "3bd75cef7ffb3e9692380855e51ed76d3efb87459aeb3be16d1e0479d59565dabf94c134591f4e54f7754144145cf57e"
}
```

##### 登出

* url: '/user/\<username\>/session' 'DELETE'
* 请求头 'Authorization'
* json字段: null

res:
```json
{
    "msg": "Logged out successfully!"
}
```

\> 任何需要验证的接口都需要这个 token

##### info

* url: '/user/\\<username\\>/info' 'GET'
* 请求头 'Authorization'
* json字段: null

res:
```json
{
    "username": "far",
    "joined_nests": [
        {
            "_id": "5973730bf6ded6013fc37076",
            "kept_days": 0
        }
    ],
    "uploaded_musics": [],
    "alarm_clocks": [
        "59738584f6ded65832a3c171",
        "597385a4f6ded65832a3c172"
    ],
    "avatar": ""
}
```

##### 注册

* url: '/user' 'POST'
* 请求头 null
* json字段: 'username', 'password'

req:
```json
{
	"password":"8412",
	"username":"aaaaaaaa"
}
```

res:
```json
{
    "username": "aaaaaaaa",
    "password": "8412",
    "created_time": 1500719922,
    "joined_nests": [],
    "uploaded_musics": [],
    "alarm_clocks": [],
    "avatar": ""
}
```

##### 修改用户信息

* url: '/user' 'POST', 'GET'
* 请求头 'Authorization'
* json字段: 任意用户信息，修改数组有专用的方法，不要在这里修改

req:
```json
{
	"nickname":"a",
	"avatar":"http://a.com/b.jpg"
}
```

res:
完整用户信息


##### 加入鸟窝
url '/user/\<username\>/joined_nests' 'POST'
* 请求头 'Authorization'
* json字段: 'nests \<Array.\<nest_id\>\>'
req:
```json
{
	"nests": ["59737af7f6ded61e7af0e668"]
}
```

res:
```json
{
    "joined_nests": [
        {
            "_id": "59737af7f6ded61e7af0e6b8",
            "name": "aaaaaaa",
            "desc": "aaaa",
            "members_limit": 0,
            "start_time": 1331856000,
            "challenge_days": 1000,
            "cover_image": "",
            "open": true,
            "created_time": 1500711543,
            "creator": "far",
            "owner": "far",
            "members_amount": 1
        },
        ...
    ]
}
```

##### 退出鸟窝
url '/user/\<username\>/joined_nests' 'DELETE'
* 请求头 'Authorization'
* json字段: 'nests \<Array.\<nest_id\>\>'
req:
```json
{
	"nests": ["59737af7f6ded61e7af0e668"]
}
```

res:
鸟窝列表，和上面一样

##### 列出鸟窝
url '/user/\<username\>/joined_nests' 'GET'
* 请求头 'Authorization'

res:
鸟窝列表，和上面一样


##### 上传一个资源
url '/user/\<username\>/\<type\>/\<name\>' 'POST'
* 请求头 'Authorization', 'X-Mime-Type'
* 请求体 整个请求体就是文件

注：type: 'uploaded_musics' | 'avatar'

注：name: music的时候给一个有意义的值，可重复。avatar可以随意给但是不能缺省，推荐'default'


res:

type为前者:
```json
{
    "_id": "59742ce5f6ded67422b9ffa3",
    "url": "http://nesthabit.pek3a.qingstor.com/music/670820590810712.png"
}
```

为后者:
完整用户信息

#### 鸟窝的接口

##### 添加鸟窝
* url '/nest' 'POST'
* 请求头 'Authorization'
* 请求体json 'name', 'desc', 'members_limit', 'start_time', 'challenge_days', 'open'

req:
```json
{
	"name":"aaaaa",
	"desc":"bbbbb",
	"members_limit":0,
	"start_time": 1456789000,
	"challenge_days": 10000,
	"open":true
}
```

res:
```json
{
    "name": "aaaaa",
    "desc": "bbbbb",
    "members_limit": 0,
    "start_time": 1456789000,
    "challenge_days": 10000,
    "cover_image": "",
    "open": true,
    "created_time": 1500757500,
    "creator": "far",
    "owner": "far",
    "members_amount": 1,
    "_id": "59742e7cf6ded67422b9ffa4"
}
```

##### 修改鸟窝
* url '/nest/\<id\>' 'POST' id就是上面的_id
* 请求头 'Authorization'
* 请求体 要修改的数据

req:
```json
{
    "open": false
}
```

res:
完整鸟窝信息

##### 删除鸟窝
* url '/nest/\<id\>' 'DELETE' id就是上面的_id
* 请求头 'Authorization'

res:
```json
{
    "msg": "Delete successfully!"
}
```

##### 获取鸟窝信息
* url '/nest/\<id\>?list_members=1' 'GET' id就是上面的_id
* 请求头 'Authorization'

注：当list_members为非空字符串时，会列出所有成员

res:
```json
{
    "_id": "597431a9f6ded6062862d268",
    "name": "aaaaaaa",
    "desc": "aaaa",
    "members_limit": 0,
    "start_time": 1331856000,
    "challenge_days": 1000,
    "open": true,
    "cover_image": "",
    "created_time": 1500758313,
    "creator": "far",
    "owner": "far",
    "members_amount": 1,
    "members": [
        {
            "username": "far",
            "joined_nests": [
                {
                    "_id": "59737af7f6ded61e7af0e6b8",
                    "kept_days": 0
                },
                {
                    "_id": "597431a9f6ded6062862d268",
                    "kept_days": 0
                }
            ],
            "uploaded_musics": [
                "59742ce5f6ded67422b9ffa3"
            ],
            "alarm_clocks": [
                "597385a6f6ded65832a3c175",
                "597385aaf6ded65832a3c176"
            ],
            "avatar": "http://nesthabit.pek3a.qingstor.com/image/581583075164355.png",
            "nickname": "a"
        }
    ]
}
```

##### 踢人
* url '/nest/\<id\>/members/\<member_username\>' 'DELETE'
* 请求头 'Authorization'

req:
修改后的完整鸟窝信息



#### 闹钟的接口

##### 新建闹钟
* url '/nest/\<id\>/members/\<member_username\>' 'DELETE'
* 请求头 'Authorization'
* 请求体json 'title', 'time', 'repeat', 'music_id', 'duration_level',
'nap_level', 'volume_level', 'bind_to_nest', 'willing_music',
'willing_text'

req:
```json
{
    "title" : "waaaaaaa",
    "repeat" : [
        0,
        1,
        3,
        5,
        6
    ],
    "music_id" : "",
    "duration_level" : 1,
    "volume_level" : 1,
    "nap_level" : 1,
    "bind_to_nest" : "",
    "willing_music" : true,
    "willing_text" : true,
    "time" : [
        7,
        0
    ]
}
```

res:
```json
{
    "title": "waaaaaaa",
    "time": [
        7,
        0
    ],
    "repeat": [
        0,
        1,
        3,
        5,
        6
    ],
    "music_id": "",
    "duration_level": 1,
    "nap_level": 1,
    "volume_level": 1,
    "bind_to_nest": "",
    "willing_music": true,
    "willing_text": true,
    "created_time": 1500775910,
    "owner": "far",
    "_id": "59747666f6ded6056e2499ec"
}
```


##### 根据id 获取
* url '/api/v1/alarm_clock/\<id\>' 'GET'
* 请求头 'Authorization'

res:
```json
{
    "_id": "59747666f6ded6056e2499ec",
    "title": "waaaaaaa",
    "time": [
        7,
        0
    ],
    "repeat": [
        0,
        1,
        3,
        5,
        6
    ],
    "music_id": "",
    "duration_level": 1,
    "nap_level": 1,
    "volume_level": 1,
    "bind_to_nest": "",
    "willing_music": true,
    "willing_text": true,
    "created_time": 1500775910,
    "owner": "far"
}
```

##### 删除修改和nest一样

* url '/api/v1/alarm_clock/\<id\>' 'PUT' 'POST' 'DELETE'
* 请求头 'Authorization'


##### 特殊！根据目标用户名和目标鸟窝id获取闹钟

这个功能是用来检验某用户是否有绑定到指定鸟窝的闹钟，从而确定能否设置提醒

* url '/api/v1/alarm_clock?target_user=<target_username>&target_nest=<target_nest_id>' 'GET'
* 请求头 'Authorization'

如果没有返回400，如果有返回200和闹钟信息



#### 提醒相关

##### 新建提醒
* url '/api/v1/remind' 'POST'
* 请求头 'Authorization'
* 请求体json 'music_id', 'text', 'target_username',
            'target_alarm_clock', 'start_time',
            'end_time', 'from_nest'


req:

我要先恢复数据库

res:

完整提醒信息

##### 移除提醒
* url '/api/v1/remind/\<id\>' 'GET'
* 请求头 'Authorization'

res:
```json
{
    "msg": "Delete successfully!"
}
```

##### 我的提醒(被)
* url '/api/v1/user/<username>/reminds_on_me', 'GET'
* 请求头 'Authorization'

res:
```
    'reminds': [
        {},
        // 提醒完整信息列表
    ]
```

##### 我创建的提醒
* url '/api/v1/user/<username>/reminds_by_me', 'GET'
* 请求头 'Authorization'

res:
```
    'reminds': [
        {},
        // 提醒完整信息列表
    ]
```

#### 消息相关

##### 发送一条消息
* url '/api/v1/chat_log' 'POST'
* 请求头 'Authorization'
* 请求体json 'value', 'target_nest'

req:
```
{
    "value": "hehehe",
    "target_nest": "" // 一长串id
}
```

res:

消息的完整内容

##### 获取某个鸟窝所有的消息
* url '/api/v1/nest/<id>/chat_log', 'GET'
* 请求头 'Authorization'


res:
```
{
    "chat_log": [
        {},
        {},
        {} // 消息内容
    ]
}
```

#### 打卡相关

##### 打卡
* url /api/v1/punch','POST'
* 请求头 'Authorization'
* 请求体json 'target_nest'

req:
```
{
    "target_nest": "" //nest id
}
```

res:

这次打卡的详情消息

```js
{
    'target_nest': 'id'
    'operate_time': time // 打卡时间,
    'username': '',
    'day': '%Y%m%d' // 格式时间
}
```

##### 获取某鸟窝打卡日期数组

* url /api/v1/user/<username>/nest/<nest_id>/punches, GET
* 请求头 'Authorization'

res
```js
{
    'days': [
        '%Y%m%d',
        '%Y%m%d',
        ...
    ]
}
```

