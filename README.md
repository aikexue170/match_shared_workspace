# match_shared_workspace

为电赛备赛准备的专用仓库，各个实现的模块和技术均可以上传至本仓库。

## 项目结构导航

```
match_shared_workspace/
├── IMU/                          # 惯性测量单元（IMU）模块
│   ├── imu.py                    # IMU 类封装 — 多线程串口读取，支持 with 语句，线程安全
│   ├── yis_std_dec.py            # 官方解码器（元生创新 Yesense）— 协议解析、CRC 校验
│   ├── SINS.py                   # SINS+ZUPT 纯惯导可视化 Demo（已放弃，代码留档）
│   └── QT_learning/              # QT / PyQtGraph 学习代码
│       └── 1.py                  # 第一个 PyQtGraph 程序：创建窗口并绘制平方曲线（红线+蓝点）
├── LICENSE                       # 开源许可证
├── .gitignore                    # 忽略 __pycache__/ 和 .vscode/
└── README.md                     # 本文件 — 项目导航
```

## 模块说明

### IMU — 惯性测量单元

| 文件 | 说明 |
|------|------|
| `imu.py` | 面向对象封装的 IMU 类，通过串口读取 Yisense 姿态数据。后台线程持续读取，`get_data()` 线程安全返回最新帧。支持 `with` 上下文管理器自动开关串口。 |
| `yis_std_dec.py` | 元生创新（Yesense）官方解码库，实现 YIS 协议解析、CRC 校验、加速度/角速度/四元数/欧拉角/时间戳等数据的解包。 |
| `SINS.py` | 纯捷联惯导 + ZUPT（零速修正）可视化程序，基于 PyQt5 + pyqtgraph OpenGL 3D 显示。因纯惯导漂移过大，方案已放弃，代码留档备查。 |

### QT_learning

PyQtGraph 入门学习代码。
