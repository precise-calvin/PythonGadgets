#!/usr/bin/env python3
"""
autowrite_multitool.py

macOS 版本 —— 当在局域网中扫描到名为 multitool (multitool.lan) 的主机时：
    1) 取到该主机的 IP（通过 ping 解析）
    2) 执行：
       cat IMAGE | ssh root@<found_ip> -o StrictHostKeyChecking=accept-new \
           "dd of=/dev/mmcblk2 bs=4M status=progress conv=fsync && shutdown -now"
    3) 日志输出并在完成后退出

危险提示：此脚本会覆盖远端设备 (/dev/mmcblk2) 并使其立即关机，请务必确认目标与镜像路径。
"""

import subprocess
import time
import os
import signal
import sys
from datetime import datetime
import re
import shutil

# ====== 配置区（按需修改） ======
IMAGE_PATH = "/Users/calvin/Desktop/3318box/img/AirplayAndDlan_backup.img"
REMOTE_USER = "root"
REMOTE_DEV = "/dev/mmcblk2"
TARGET_NAMES = ["multitool.lan", "multitool"]  # 轮流尝试解析
POLL_INTERVAL = 3  # 秒
SSH_OPTS = ["-o", "StrictHostKeyChecking=accept-new"]
# =================================

stop_requested = False

def log(msg):
    print(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {msg}", flush=True)

def signal_handler(sig, frame):
    global stop_requested
    log("收到中断信号，准备退出...")
    stop_requested = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_ping_ip(ping_output):
    """
    解析 macOS / Linux ping 输出第一行中的 IP，示例：
    PING multitool.lan (192.168.2.179): 56 data bytes
    """
    if not ping_output:
        return None
    m = re.search(r'\((\d{1,3}(?:\.\d{1,3}){3})\)', ping_output)
    if m:
        return m.group(1)
    # 备用尝试：有些系统会直接在第一行出现 IP 后跟冒号
    m2 = re.search(r'PING [^\s]+ ([\d\.]+):', ping_output)
    if m2:
        return m2.group(1)
    return None

def try_resolve_by_ping(name, timeout_sec=3):
    """
    在 macOS 上执行 `ping -c 1 name` 并解析出 IP（如果能解析到）。
    返回 ip 字符串或 None。
    """
    try:
        completed = subprocess.run(
            ["ping", "-c", "1", name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_sec,
            text=True
        )
        out = completed.stdout
        ip = parse_ping_ip(out.splitlines()[0] if out else "")
        if ip:
            return ip
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None
    return None

def is_reachable(ip):
    """简单 ping 测试，返回 True/False"""
    try:
        res = subprocess.run(["ping", "-c", "1", ip],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             timeout=3)
        return res.returncode == 0
    except Exception:
        return False

def play_sound(kind):
    """
    在 macOS 上播放提示音（非阻塞）。
    kind: "start" / "success" / "failure"
    优先使用 afplay + 系统声音文件；若不可用，回退到终端响铃。
    """
    # 可选的系统声音（macOS 通常存在）
    sound_map = {
        "start": "/System/Library/Sounds/Glass.aiff",
        "success": "/System/Library/Sounds/Pop.aiff",
        "failure": "/System/Library/Sounds/Basso.aiff"
    }
    path = sound_map.get(kind)
    try:
        if path and os.path.exists(path) and shutil.which("afplay"):
            # 非阻塞播放
            subprocess.Popen(["afplay", path],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             close_fds=True)
        else:
            # 回退：如果有 say 命令，可短暂说一句（可选），否则打印响铃
            if shutil.which("say"):
                # 用 say 简短提示，非阻塞
                text = {
                    "start": "Transfer starting",
                    "success": "Transfer successful",
                    "failure": "Transfer failed"
                }.get(kind, "")
                if text:
                    subprocess.Popen(["say", text],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL,
                                     close_fds=True)
                else:
                    print('\a', end='', flush=True)
            else:
                # 最后回退到终端响铃
                print('\a', end='', flush=True)
    except Exception as e:
        # 不要因为声音报错影响主流程，仅记录日志
        log(f"播放提示音失败: {e}")

def perform_transfer(image_path, remote_user, remote_ip, remote_dev):
    """执行 cat image | ssh root@remote_ip "dd ... && shutdown -now"
       在开始、成功、失败时播放提示音（macOS）。
    """
    if not os.path.isfile(image_path):
        log(f"镜像文件不存在: {image_path}")
        play_sound("failure")
        return False

    ssh_target = f"{remote_user}@{remote_ip}"
    remote_cmd = f"dd of={remote_dev} bs=4M status=progress conv=fsync && shutdown -now"

    ssh_cmd = ["ssh"] + SSH_OPTS + [ssh_target, remote_cmd]

    # 使用 Popen，把文件作为 stdin 传给 ssh
    log("准备开始传输镜像：")
    log(f"cat {image_path} | ssh {ssh_target} \"dd of={remote_dev} bs=8M status=progress oflag=direct && shutdown -now\"")

    # 播放“开始写入”提示音（非阻塞）
    play_sound("start")

    try:
        with open(image_path, "rb") as f:
            proc = subprocess.Popen(ssh_cmd, stdin=f)
            log("传输中...（根据镜像大小与网络速度，这会花些时间）")
            proc.wait()
            if proc.returncode == 0:
                log("传输与远端关机命令执行成功。")
                play_sound("success")
                return True
            else:
                log(f"ssh 返回非零码：{proc.returncode}")
                play_sound("failure")
                return False
    except KeyboardInterrupt:
        log("用户中断传输。")
        play_sound("failure")
        return False
    except Exception as e:
        log(f"传输失败，异常：{e}")
        play_sound("failure")
        return False

def main():
    log("脚本启动（macOS）。开始轮询目标主机...")
    while not stop_requested:
        found_ip = None
        resolved_name = None
        for name in TARGET_NAMES:
            if stop_requested:
                break
            log(f"尝试解析主机名：{name}")
            ip = try_resolve_by_ping(name)
            if ip:
                log(f"通过 ping 解析到 {name} -> {ip}")
                # 进一步确认可达
                if is_reachable(ip):
                    log(f"{ip} 可达（ping 成功）。")
                    found_ip = ip
                    resolved_name = name
                    break
                else:
                    log(f"{ip} 不可达，继续检测下一个名称。")
            else:
                log(f"未解析到 {name}（ping 未返回 IP）。")
        if found_ip:
            log(f"已发现目标 {resolved_name}（{found_ip}），将向该 IP 发起写入操作。")
            ok = perform_transfer(IMAGE_PATH, REMOTE_USER, found_ip, REMOTE_DEV)
            if ok:
                log("任务完成，脚本退出。")
                return 0
            else:
                log(f"写入失败或异常。{POLL_INTERVAL}s 后重试。")
        else:
            log(f"未检测到目标（{', '.join(TARGET_NAMES)}）。{POLL_INTERVAL}s 后重试。")
        # 等待间隔（可被中断）
        for _ in range(POLL_INTERVAL):
            if stop_requested:
                break
            time.sleep(1)

    log("被请求停止，退出程序。")
    return 1

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)