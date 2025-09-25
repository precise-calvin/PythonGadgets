#!/usr/bin/env python3
"""
macOS 版本 —— 当在局域网中扫描到名为 multitool (multitool.lan) 的主机时：
    1) 取到该主机的 IP（通过 ping 解析）
    2) 通过 SSH 在远端执行：
       zcat /mnt/images/AirplayOnly_backup.img.gz | dd of=/dev/mmcblk2 bs=4M conv=fsync
       并在完成后关机
    3) 刷写完成后继续等待下一台设备上线.
"""

import subprocess
import time
import os
import signal
from datetime import datetime
import re
import shutil
import requests
import urllib.parse
import sys

# ====== 配置区（按需修改） ======
# REMOTE_IMAGE_PATH = "/mnt/images/AirplayOnly_backup.img.gz"
REMOTE_IMAGE_PATH = "/mnt/images/AirplayAndDlan_backup.img.gz"

REMOTE_IMAGE_NAME = os.path.basename(REMOTE_IMAGE_PATH)
REMOTE_USER = "root"
REMOTE_DEV = "/dev/mmcblk2"
TARGET_NAMES = ["multitool.lan", "multitool"]
POLL_INTERVAL = 3  # 秒
SSH_OPTS = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
BARK_URL = "https://api.day.app/cCTnvfFmg93txkgLP6SupU"

# 颜色常量
class Colors:
    BLUE = '\033[34m'
    ORANGE = '\033[33m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'

def colored_text(text, color):
    return f"{color}{text}{Colors.RESET}"

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
    m = re.search(r'\((\d{1,3}(?:\.\d{1,3}){3})\)', ping_output)
    if m:
        return m.group(1)
    m2 = re.search(r'PING [^\s]+ ([\d\.]+):', ping_output)
    if m2:
        return m2.group(1)
    return None

def try_resolve_by_ping(name, timeout_sec=3):
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
    except Exception:
        return None
    return None

def is_reachable(ip):
    try:
        res = subprocess.run(["ping", "-c", "1", ip],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             timeout=3)
        return res.returncode == 0
    except Exception:
        return False

def play_sound(kind):
    sound_map = {
        "start": "/System/Library/Sounds/Glass.aiff",
        "success": "/System/Library/Sounds/Pop.aiff",
        "failure": "/System/Library/Sounds/Basso.aiff"
    }
    path = sound_map.get(kind)
    try:
        if path and os.path.exists(path) and shutil.which("afplay"):
            subprocess.Popen(["afplay", path],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             close_fds=True)
        else:
            print('\a', end='', flush=True)
    except Exception as e:
        log(f"播放提示音失败: {e}")

def perform_transfer_remote(remote_image_path, remote_user, remote_ip, remote_dev):
    """
    在远端执行刷写命令，并通过 /proc/sysrq-trigger 关机
    实时显示刷写进度在一行
    """
    ssh_target = f"{remote_user}@{remote_ip}"
    remote_cmd = (
        f"zcat {remote_image_path} | dd of={remote_dev} bs=4M "
        f"status=progress oflag=direct conv=fsync && sync && sleep 2s && echo o > /proc/sysrq-trigger"
    )
    ssh_cmd = ["ssh"] + SSH_OPTS + [ssh_target, remote_cmd]

    log(f"准备在远端 {ssh_target} 执行刷写命令")
    play_sound("start")

    try:
        proc = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        output_accum = ""
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                line = line.rstrip()
                output_accum += line + "\n"
                # 在一行刷新显示（橙色）
                print(f"\r{colored_text('刷写进度: ' + line, Colors.ORANGE)}", end="", flush=True)

        proc.wait()
        print()  # 刷写完成后换行

        # 判断返回码或是否包含 "No space left on device"
        if proc.returncode == 0:
            log(colored_text(f"{remote_ip} 刷写成功并已关机。", Colors.GREEN))
            play_sound("success")
            return True

        if "No space left on device" in output_accum:
            log(colored_text(f"{remote_ip} 刷写成功（超emmc大小刷写）并已关机。", Colors.GREEN))
            play_sound("failure")
            time.sleep(1)
            play_sound("success")
            return True

        log(colored_text(f"ssh 返回非零码：{proc.returncode}", Colors.RED))
        play_sound("failure")
        return False

    except Exception as e:
        log(colored_text(f"刷写失败，异常：{e}", Colors.RED))
        play_sound("failure")
        return False

def send_bark(title, message, url=BARK_URL):
    sound = "glass"
    encoded_title = urllib.parse.quote(title)
    encoded_message = urllib.parse.quote(message)
    push_url = f"{url}/{encoded_title}/{encoded_message}?sound={sound}"
    try:
        response = requests.get(push_url)
        if response.status_code == 200:
            print("Bark 推送成功！")
        else:
            print(f"Bark 推送失败，状态码: {response.status_code}, 内容: {response.text}")
    except Exception as e:
        print(f"Bark 推送异常: {e}")

def main():
    log("脚本启动（macOS）。开始轮询目标主机...")
    while not stop_requested:
        for name in TARGET_NAMES:
            if stop_requested:
                break
            ip = try_resolve_by_ping(name)
            if ip:
                if is_reachable(ip):
                    print()  # 换行，结束之前的刷新行
                    log(f"发现可达设备 {name} -> {ip}，准备刷写")
                    send_bark("刷写开始", REMOTE_IMAGE_NAME)
                    ok = perform_transfer_remote(REMOTE_IMAGE_PATH, REMOTE_USER, ip, REMOTE_DEV)
                    if ok:
                        send_bark("刷写完成", REMOTE_IMAGE_NAME)
                        log(colored_text(f"{ip} 刷写完成，继续等待下一台设备上线。", Colors.GREEN))
                    else:
                        send_bark("刷写失败", REMOTE_IMAGE_NAME)
                        log(colored_text(f"{ip} 刷写失败，将在下轮重试。", Colors.RED))
                else:
                    print(f"\r[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {colored_text(f'{ip} 不可达，继续检测...', Colors.BLUE)}", end="", flush=True)
            else:
                print(f"\r[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {colored_text(f'正在查找 {name}...', Colors.BLUE)}", end="", flush=True)
        for _ in range(POLL_INTERVAL):
            if stop_requested:
                break
            time.sleep(1)
    print()  # 换行，结束最后的刷新行
    log("被请求停止，退出程序。")

if __name__ == "__main__":
    main()