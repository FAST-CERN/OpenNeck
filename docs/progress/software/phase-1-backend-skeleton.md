# software phase-1-backend-skeleton 进度

[计划](../../plan/software/phase-1-backend-skeleton.md) · [状态](../../STATUS.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md)

执行方式：subagent-driven（SDD）。分支 `feat/twist2-dynamixel`，基线 af3d1c2 → c389f40。

## 改动概览

- 新增 `openneck/_backends/`（`__init__.py`/`protocol.py`/`_port.py`/`factory.py`/`feetech.py`）：引入 `ServoBackend` Protocol 与 `make_backend(config, *, enable_torque_on_connect=True)` 工厂；Feetech 驱动由 `_driver.py` 迁入 `_backends/feetech.py`（`ServoDriver`→`FeetechBackend`），仅做 brief 指定的改动（类名、`..` 导入、`find_servo_port` 来源、docstring、`__enter__` 注解）。
- `api.py` 改用 `openneck.api._make_backend`（`self._driver`→`self._backend`，6 处方法）。
- `cli.py` 校准路径改用 `make_backend`，`record_axis_limits` 类型改为 `ServoBackend`。
- 删除旧 `openneck/_driver.py`。
- 测试：`tests/test_driver.py` 迁至 `tests/test_backends/test_feetech_backend.py`；新增 `tests/test_backends/test_factory.py`；`tests/test_api.py` patch 目标更新为 `openneck.api._make_backend`。

## 命令与结果

- `F:\Anaconda\python.exe -m pytest -q` → 24 passed（每个子任务后均全绿）。
- `grep -rn "_driver" openneck/ tests/` → 无匹配（删除后确认无残留引用）。

## 提交

- af3d1c2 → c389f40：Task A `2ea6dfb`（包+Feetech 迁移）、Task B `492afdd`（api.py）、Task C `c7902e5`（cli.py）、Task D c389f40（删除 _driver.py）。

## 偏离

- 计划 Task 1+2 因强耦合（factory/test 依赖 `FeetechBackend`）合并为单次派发（SDD Task A），符合 SDD 任务粒度规则。
- Minor（延后）：`tests/test_api.py` 局部变量名 `self.driver_patch`/`driver` 未随重命名，属 brief 范围外，审查员建议保留。
