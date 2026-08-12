# 将 OpenNeck 部署到既有环境（如 `teleopit`）

把当前 OpenNeck 版本（v0.2.x，含可选 Dynamixel 后端）安装进你已在运行的环境——例如 `teleopit` conda 环境——的迁移运维手册。覆盖全新安装与升级，Linux 与 Windows 通用。

完整的配置字段参考与标定流程见 [`software.md`](software.md)。本指南只链接这些值，不复述。

---

## 为什么需要这份指南

`pip install` **不会**把 OpenNeck 的运行时参数一起带来。配置文件 `active_vision_config.json` 被 gitignore，且运行时按**当前工作目录**解析，而非安装位置。因此把 OpenNeck 迁进新环境是三件互相独立的事：

| # | 内容 | 随 `pip install` 自动来吗？ |
|---|------|------------------------------|
| 1 | Python 包（含你的后端改动） | 是——来自本仓库 |
| 2 | Dynamixel SDK（用于 `servo_backend: "dynamixel"`） | 仅当安装 `dynamixel` extra 时 |
| 3 | 运行时配置 `active_vision_config.json` | **否**——需手动迁移 |

## 第 0 步——确认目标解释器

OpenNeck 与 SDK 必须装进**实际 `import openneck` 的那个解释器**。裸 `pip` 常常绑到别的环境。务必先激活目标环境，再用 `python -m pip`。

```bash
# 先激活你的环境，例如：
conda activate teleopit          # conda
# 或:  source .venv/bin/activate   # Linux venv
# 或:  .venv\Scripts\activate      # Windows venv / cmd
# 或:  .venv\Scripts\Activate.ps1  # Windows PowerShell

# 确认这就是 teleopit 将使用的解释器：
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

Windows 上 `where python`（cmd）或 `Get-Command python`（PowerShell）会列出 `PATH` 上所有 `python`——确认第一条在目标环境内。

## 第 1 步——获取代码（含 Dynamixel 子模块）

```bash
# 全新克隆（SDK 是子模块，必须带 --recurse-submodules）：
git clone --recurse-submodules <repo>
cd OpenNeck

# 已克隆过？确保子模块就位且为最新：
git submodule update --init --recursive

# 把既有检出升级到当前版本：
git pull
git submodule update --recursive
```

## 第 2 步——安装包

用第 0 步确认的解释器安装：

```bash
# 仅 Feetech（自动拉取 pyserial + ftservo-python-sdk）：
python -m pip install .

# Dynamixel 版——一条命令，同时拉取内置 SDK：
python -m pip install ".[dynamixel]"

# 可编辑 / 开发安装：
python -m pip install -e .
python -m pip install -e thirdparty/DynamixelSDK/python   # SDK 可编辑
```

`".[dynamixel]"` 加引号是为避免方括号被 shell 当作 glob；POSIX shell 与 Windows cmd 下都安全。

**在代理后面？** 若 pip 构建隔离无法访问 PyPI，加 `--no-build-isolation`（宿主环境需已装有 `setuptools` + `wheel`）。

**Linux 串口权限**（机器人主机）：把当前用户加入 dialout 组后重新登录，或装一条 udev 规则：

```bash
sudo usermod -aG dialout "$USER"   # 然后注销重新登录
```

**验证安装：**

```bash
python -c "import openneck; print(openneck.__version__)"      # -> 0.2.0
# 仅 Dynamixel 版：
python -c "from dynamixel_easy_sdk import Connector; print('sdk ok')"
```

## 第 3 步——迁移运行时配置

按你的硬件选一份模板复制，再编辑：

```bash
# Linux / macOS：
cp active_vision_config.dynamixel.example.json active_vision_config.json
# Windows cmd：
copy active_vision_config.dynamixel.example.json active_vision_config.json
# Windows PowerShell：
Copy-Item active_vision_config.dynamixel.example.json active_vision_config.json
```

然后区分文件里的两类字段：

- **可跨机器复用**（同一套硬件装配）——直接照搬：
  `servo_backend`、`baudrate`、`yaw_id`、`pitch_id`、`yaw_step_sign`、
  `pitch_step_sign`、`operating_mode`、`profile_velocity`、
  `profile_acceleration`、`yaw_kp`/`ki`/`kd`、`pitch_kp`/`ki`/`kd`。
- **跟物理机构绑定**——这些来自对**具体那台机构**的标定，跨颈部不要照信：
  `yaw_center_step`、`yaw_min_step`、`yaw_max_step`、`pitch_center_step`、
  `pitch_min_step`、`pitch_max_step`。在真实机构上重跑：

  ```bash
  openneck calibrate --port /dev/ttyUSB0      # Linux
  openneck calibrate --port COM3              # Windows
  ```

**文件应放在哪：** 默认加载器按宿主程序**当前工作目录**读取
`./active_vision_config.json`。若 `teleopit` 并非从固定 CWD 启动，请改用
[集成方式](#集成方式)中的显式模式，而不是依赖 CWD。

> 从 0.1.x 升级？旧的归一化幅值字段无法换算成 0.2.x 的角度方向，需重跑
> `openneck calibrate`。详见 [`software.md`](software.md)。

## 第 4 步——真机验证

激活环境（使 `openneck` 命令在 `PATH` 上）后：

```bash
openneck config                       # 打印已加载的配置
openneck ports                        # 列出串口
openneck voltage --port /dev/ttyUSB0  # 非运动冒烟测试：电压 + 角度
```

`openneck voltage` 不驱动机构，是硬件上安全的第一步检查。

## 集成方式

`teleopit`（或任何宿主）如何使用 OpenNeck。公开 API 是
`OpenNeckController`；唯一不同的是后端选择。

```python
from openneck import OpenNeckController

# 模式 A——宿主程序 CWD 下的 JSON 文件（默认查找路径）：
with OpenNeckController(port="/dev/ttyUSB0") as neck:
    neck.center()
    neck.move_deg(5.0, 0.0)

# 模式 B——显式配置路径（不依赖 CWD）：
with OpenNeckController(
    config="/etc/openneck/active_vision_config.json",
    port="/dev/ttyUSB0",
) as neck:
    neck.move_deg(5.0, 0.0)

# 模式 C——纯代码，无需 JSON 文件（后端在代码里选）：
with OpenNeckController(
    servo_backend="dynamixel",
    baudrate=57600,
    port="/dev/ttyUSB0",
) as neck:
    neck.center()
```

`servo_backend`、`baudrate`、`operating_mode` 是 keyword-only 覆盖参数；非法值会走与配置文件相同的校验抛错。更深的字段（PID 增益、profile velocity/acceleration）仍由 JSON 提供。

## 排错

| 症状 | 原因 / 处理 |
|---|---|
| `import openneck` 仍加载旧版本 | 解释器不对。复查 `sys.executable`，然后用 `python -m pip install ...` 在该环境内重装。 |
| `ModuleNotFoundError: dynamixel_easy_sdk` | 你装的是 Feetech-only。用 `python -m pip install ".[dynamixel]"` 重装。 |
| 打开串口报 `PermissionError`（Linux） | 用户不在 `dialout` 组（见第 2 步），或端口被其他进程占用。 |
| 代理后 pip 拉不到 setuptools/wheel | 加 `--no-build-isolation`（宿主环境需已装 `setuptools` + `wheel`）。 |
| 迁移后机构方向不对 / 角度偏 | 复制来的标定步进与本机构不匹配。重跑 `openneck calibrate`。 |
| 找不到 `active_vision_config.json` | 宿主运行的 CWD 下没有该文件。改用模式 B（显式路径）或模式 C（纯代码）。 |

## 参考

- 安装 + 完整配置字段参考 + 标定：[`software.md`](software.md)
- 配置为何按 CWD 解析、override 与后端选择如何工作：[`../knowledge/config-dataflow.md`](../knowledge/config-dataflow.md)
- TWIST2 舵机硬件取值（ID、零位、限位）：[`../knowledge/twist2-servo-config.md`](../knowledge/twist2-servo-config.md)
