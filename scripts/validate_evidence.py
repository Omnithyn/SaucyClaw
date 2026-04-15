#!/usr/bin/env python3
"""
验证 validation_output 中的证据文件完整性与一致性

用途：
- 验证所有场景的 payload 和 evidence 文件是否存在
- 验证 evidence.payload 与 _payload.json 内容一致
- 为 M5-R 提供自动化验证支持

环境变量：
- VALIDATION_OUTPUT_DIR: 验证目录路径（可选，默认 ./validation_output）
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """加载 JSON 文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"✗ 无法加载 {file_path}: {e}")
        return None


def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """标准化 payload（去除时间戳差异）"""
    return {k: v for k, v in payload.items() if k != "timestamp"}


def verify_evidence_consistency(validation_dir: Path) -> bool:
    """验证 evidence 和 payload 文件的一致性"""
    print("\n=== 证据文件验证 ===\n")

    all_pass = True

    # 查找所有 evidence 文件
    evidence_files = list(validation_dir.glob("*_evidence.json"))

    if not evidence_files:
        print("⚠️  未找到任何 evidence 文件")
        return False

    print(f"发现 {len(evidence_files)} 个 evidence 文件:\n")

    for evidence_file in evidence_files:
        scenario = evidence_file.stem.replace("_evidence", "")
        payload_file = validation_dir / f"{scenario}_payload.json"

        # 检查 payload 文件是否存在
        if not payload_file.exists():
            print(f"✗ {scenario}: 缺少 {payload_file.name}")
            all_pass = False
            continue

        # 加载文件
        evidence = load_json(evidence_file)
        payload = load_json(payload_file)

        if evidence is None or payload is None:
            all_pass = False
            continue

        # 验证 evidence 中包含 payload 字段
        if "payload" not in evidence:
            print(f"✗ {scenario}: evidence 缺少 payload 字段")
            all_pass = False
            continue

        # 比较 payload 一致性（去除 timestamp）
        evidence_payload = normalize_payload(evidence["payload"])
        file_payload = normalize_payload(payload)

        if evidence_payload == file_payload:
            print(f"✓ {scenario}: evidence.payload == {payload_file.name}")

            # 显示关键信息
            mode = evidence.get("mode", "unknown")
            success = evidence.get("success", False)
            status = evidence.get("status_code", "N/A")
            print(f"  模式: {mode}, 成功: {success}, 状态码: {status}")
        else:
            print(f"✗ {scenario}: payload 不一致!")
            print(f"  evidence.payload: {list(evidence_payload.keys())}")
            print(f"  {payload_file.name}: {list(file_payload.keys())}")
            all_pass = False

        print()

    return all_pass


def verify_all_payloads_exist(validation_dir: Path) -> bool:
    """验证所有场景都有 payload 文件"""
    print("\n=== Payload 文件存在性验证 ===\n")

    all_pass = True

    # 查找所有 payload 文件
    payload_files = list(validation_dir.glob("*_payload.json"))

    if not payload_files:
        print("⚠️  未找到任何 payload 文件")
        return False

    print(f"发现 {len(payload_files)} 个 payload 文件:\n")

    for payload_file in payload_files:
        scenario = payload_file.stem.replace("_payload", "")
        evidence_file = validation_dir / f"{scenario}_evidence.json"

        if evidence_file.exists():
            print(f"✓ {payload_file.name} (关联 evidence: {evidence_file.name})")
        else:
            print(f"⚠️  {payload_file.name} (缺少关联 evidence 文件)")
            all_pass = False

    print()
    return all_pass


def main():
    """主函数"""
    # 支持从环境变量读取验证目录
    validation_dir_path = os.environ.get("VALIDATION_OUTPUT_DIR", "validation_output")
    validation_dir = Path(validation_dir_path)

    print(f"验证目录: {validation_dir.absolute()}")

    if not validation_dir.exists():
        print(f"✗ 验证目录不存在: {validation_dir.absolute()}")
        return 1

    # 验证 payload 文件存在性
    payload_ok = verify_all_payloads_exist(validation_dir)

    # 验证 evidence 一致性
    consistency_ok = verify_evidence_consistency(validation_dir)

    # 总结
    print("\n=== 验证总结 ===")
    print(f"验证目录: {validation_dir.absolute()}")
    print(f"Payload 文件存在性: {'✓ PASS' if payload_ok else '✗ FAIL'}")
    print(f"Evidence 一致性: {'✓ PASS' if consistency_ok else '✗ FAIL'}")

    if payload_ok and consistency_ok:
        print("\n✅ 所有验证通过！")
        return 0
    else:
        print("\n❌ 验证失败，请检查输出")
        return 1


if __name__ == "__main__":
    exit(main())
