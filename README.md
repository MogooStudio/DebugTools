# DebugTools
 使用python开发的工具集
- 游戏包敏感词检测
- 打包ipa
- 解析崩溃日志（开发中）

# 感谢 [JetBrains](https://www.jetbrains.com/shop/eform/opensource) 的工具支持
![jetbrains](https://user-images.githubusercontent.com/3353611/119081825-6b381980-ba2f-11eb-85cc-002b466526ba.png)

## 开发环境
- 软件
```
python 3.10
```
- 插件
```
PyQt5
pyinstaller
```

## 相关命令
- ui生成代码
```
cd tools 
python convert_ui
```

- 打包
```
pyinstaller -n DebugTools -i ./icon/256.ico --windowed --onefile --clean --noconfirm main.py
```

# 开发日志

- 2021.7.15：完成基本框架（mac演示）
[![Wm2B2n.md.png](https://z3.ax1x.com/2021/07/15/Wm2B2n.md.png)](https://imgtu.com/i/Wm2B2n)

- 2021.7.16：实现sql模块，支持SQLite数据库基本操作
[![WJDcoq.md.png](https://z3.ax1x.com/2021/07/19/WJDcoq.md.png)](https://imgtu.com/i/WJDcoq)

- 2021.7.19：实现config模块，支持基础类型数据、自定义类型数据的序列化和反序列化操作
[![WJD6wn.md.png](https://z3.ax1x.com/2021/07/19/WJD6wn.md.png)](https://imgtu.com/i/WJD6wn)

- 2021.7.30：重构ui（pc演示）
[![WLFLqA.md.png](https://z3.ax1x.com/2021/07/30/WLFLqA.md.png)](https://imgtu.com/i/WLFLqA)

- 2021.9.22：删减ui功能，优化ui转换脚本（pc演示）
[![4UXvm8.md.png](https://z3.ax1x.com/2021/09/22/4UXvm8.md.png)](https://imgtu.com/i/4UXvm8)

- 2021.10.9：调试功能基本完成（pc演示）
[![5klf9H.md.png](https://z3.ax1x.com/2021/10/09/5klf9H.md.png)](https://imgtu.com/i/5klf9H)

- 2021.12.17：增加消息框功能（pc演示）
[![TixWUe.md.png](https://s4.ax1x.com/2021/12/17/TixWUe.md.png)](https://imgtu.com/i/TixWUe)

- 2024.8.21：重构UI，增加游戏包敏感词检查功能
[![pAitVpT.png](https://s21.ax1x.com/2024/08/21/pAitVpT.png)](https://imgse.com/i/pAitVpT)

- 2024.8.22：增加三个功能（代码检测、资源加密检测、密钥生成）
[![pAi79Rx.png](https://s21.ax1x.com/2024/08/22/pAi79Rx.png)](https://imgse.com/i/pAi79Rx)
[![pAi7pJ1.png](https://s21.ax1x.com/2024/08/22/pAi7pJ1.png)](https://imgse.com/i/pAi7pJ1)
[![pAi7SiR.png](https://s21.ax1x.com/2024/08/22/pAi7SiR.png)](https://imgse.com/i/pAi7SiR)

## 许可
[MIT License](https://github.com/MogooStudio/MogooPy/blob/master/LICENSE)

## 联系方式 
- email：dadalepai@163.com  
