# SiriusCore

SiriusCore 是 SiriusBot-Plugin 的核心组件，提供基础的国际化支持、API 封装等功能。所有 SiriusBot-Plugin 插件均需要继承 SiriusCore 以获得一致的开发体验。

## 特性

- 🌐 国际化（i18n）混入支持
- 🔌 插件基类，统一生命周期管理
- 🛠️ API 封装与工具方法
- 📦 依赖管理与自动初始化

## 插件指令
|指令|说明| 示例|
| -------------- | ---------------------- | ------------------- |
|订阅|在群/私聊订阅插件| `/订阅 SiriusBot-Plugin-DailyNews`|
|取消订阅|在群/私聊取消订阅插件| `/取消订阅 SiriusBot-Plugin-DailyNews`|
|插件订阅列表|查询群/私聊订阅的插件|`/插件订阅列表`|

## 快速开始

1. **安装依赖**

   请确保已安装 [Ncatbot](https://github.com/liyihao1110/ncatbot) 及其相关依赖。

2. **基于sirius_core的插件开发示例**

   ```python
   from sirius_core import SiriusPlugin

   class MyPlugin(SiriusPlugin):
       name = "MyPlugin"
       version = "1.0.0"

       async def on_load(self):
           super().pre_initialize_plugin()
           # 你的初始化代码

      # 其它内容请参见Ncatbot文档
   ```

3. **国际化支持**

插件的国际化支持由 `i18n.py` 自动生成默认的翻译文件。  

当插件首次加载时，`i18n.py` 会在插件目录下创建 `i18n` 文件夹，并生成如 `zh-CN.json` 的默认语言文件。  

你可以根据需要修改这些 JSON 文件以适配不同语言。例如：

```json
{
  "MyPlugin.command.hello": "你好，世界！"
}
```

无需手动创建文件，系统会自动初始化所需的国际化资源。


## 目录结构

```
plugins/
  sirius_core/
    ├── api.py
    ├── i18n_mixin.py
    ├── sirius_plugin.py
    ├── utils.py
    ├── README.md
    └── ...
```

## 贡献

欢迎提交 Issue 和 Pull Request！  
如有疑问请联系作者：**Sparrived**