#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
print_nps_tunnels.py

从 NPS API (/index/gettunnel) 拉取所有隧道信息并打印出来（每条一行，格式化 JSON）。
基于你给出的 execute_command 与常量示例实现。
"""

import time
import hashlib
import json
from typing import Optional, List, Dict
import requests
import sys

try:
    import paramiko
except ImportError:
    paramiko = None

class NPSConstants:
    """NPS 服务配置常量 - 根据需要修改"""
    NPS_API_BASE_URL = "http://intranetpenetration.chen.click:8080"
    NPS_AUTH_KEY = "3748392839283928"
    NPS_BASE_URL = "intranetpenetration.chen.click"
    SSH_HOST = "intranetpenetration.chen.click"
    SSH_USER = "root"
    SSH_PASSWORDS = ["armbian", "musicboxDevice@"]  # 会按顺序尝试这两个密码

class NPSUtils:
    @staticmethod
    def get_timestamp() -> Optional[str]:
        """
        调用 NPS 服务端 /auth/gettime 获取时间戳。
        返回值示例：{"time":"1695623456"}
        """
        try:
            url = f"{NPSConstants.NPS_API_BASE_URL}/auth/gettime"
            print(f"DEBUG: 请求时间戳 URL: {url}")
            response = requests.post(url, timeout=10)
            print(f"DEBUG: 时间戳响应状态码: {response.status_code}")
            print(f"DEBUG: 时间戳响应内容: {response.text}")
            response.raise_for_status()
            content = response.text.strip()
            # 优先尝试 JSON 解析
            try:
                data = json.loads(content)
                if "time" in data:
                    timestamp = str(data["time"])
                    print(f"DEBUG: 解析到时间戳: {timestamp}")
                    return timestamp
            except Exception as e:
                print(f"DEBUG: JSON 解析失败: {e}")
            # 如果不是标准 JSON，就用字符串截取方式
            start_index = content.find(":") + 1
            end_index = content.rfind("}")
            if start_index > 0 and end_index > start_index:
                timestamp = content[start_index:end_index].strip().strip('"')
                print(f"DEBUG: 字符串截取时间戳: {timestamp}")
                return timestamp
            print("DEBUG: 无法从响应中提取时间戳")
            return None
        except Exception as e:
            print(f"获取NPS服务时间戳失败: {str(e)}")
            return None

    @staticmethod
    def _get_md5(text: str) -> str:
        """计算 md5（小写十六进制）"""
        md5_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        print(f"DEBUG: MD5({text}) = {md5_hash}")
        return md5_hash

    @staticmethod
    def execute_command(path: str, params: str = "") -> Optional[str]:
        """
        按照你提供的实现封装请求。
        path: 以 / 开头的路径，例如 "/index/gettunnel"
        params: 请求体参数字符串，例如 "client_id=&type=tcp&search=&offset=1&limit=1000"
        返回响应文本或 None（失败）。
        """
        try:
            print(f"DEBUG: 执行命令路径: {path}, 参数: {params}")
            timestamp = NPSUtils.get_timestamp()
            if not timestamp:
                print("无法获取时间戳")
                return None
            auth_key_md5 = NPSUtils._get_md5(NPSConstants.NPS_AUTH_KEY + timestamp)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            # 只有认证参数放在 URL 中
            url = f"{NPSConstants.NPS_API_BASE_URL}{path}?auth_key={auth_key_md5}&timestamp={timestamp}"
            # 业务参数放在请求体中
            if params and not params.startswith("&"):
                params = "&" + params
            print(f"DEBUG: 最终请求 URL: {url}")
            print(f"DEBUG: 请求头: {headers}")
            print(f"DEBUG: 请求体: {params}")
            # 使用 POST，data 为 params（表单格式）
            response = requests.post(url, data=params, headers=headers, timeout=30)
            print(f"DEBUG: 响应状态码: {response.status_code}")
            print(f"DEBUG: 响应头: {dict(response.headers)}")
            print(f"DEBUG: 响应内容前500字符: {response.text[:500]}")
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"请求NPS服务失败 (网络错误): {str(e)}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"请求NPS服务失败 (其他错误): {str(e)}", file=sys.stderr)
            return None

def fetch_tunnels_page(offset: int = 0, limit: int = 1000) -> Optional[Dict]:
    """
    拉取一页隧道数据。返回解析后的 JSON（dict），或 None。
    注意：offset 是记录索引（从0开始），不是页码
    """
    params = f"client_id=&type=tcp&search=&offset={offset}&limit={limit}"
    text = NPSUtils.execute_command("/index/gettunnel", params)
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception as e:
        print(f"解析返回 JSON 失败: {e}", file=sys.stderr)
        return None

def fetch_all_tunnels() -> List[Dict]:
    """
    获取所有隧道数据，处理分页。
    offset 是记录索引（从0开始），每次递增 limit 的数量。
    返回去重后的 rows 列表。
    """
    limit = 1000
    all_rows: List[Dict] = []
    seen_ids = set()  # 用于去重

    # 第一页从 offset=0 开始
    first_page = fetch_tunnels_page(offset=0, limit=limit)
    if not first_page:
        return all_rows

    print(f"DEBUG: 第一页响应: {first_page}")
    
    # 有些 NPS 返回结构：{"total": n, "rows": [...]}
    rows = first_page.get("rows") if isinstance(first_page, dict) else None
    total = first_page.get("total") if isinstance(first_page, dict) else None

    if rows is None:
        # 有些接口直接返回列表
        if isinstance(first_page, list):
            return first_page
        return all_rows

    print(f"DEBUG: 总记录数: {total}, 第一页记录数: {len(rows)}")
    
    # 添加第一页数据（带去重）
    for row in rows:
        row_id = row.get("Id") or row.get("id")
        if row_id not in seen_ids:
            seen_ids.add(row_id)
            all_rows.append(row)

    # 如果总数大于第一页数量，继续获取后续页面
    if isinstance(total, int) and total > len(rows):
        offset = limit  # 下一页从 limit 开始
        while len(all_rows) < total and offset < total:
            print(f"DEBUG: 获取第 {offset//limit + 1} 页，offset={offset}")
            page = fetch_tunnels_page(offset=offset, limit=limit)
            if not page:
                print("DEBUG: 获取页面失败，停止分页")
                break
            more_rows = page.get("rows", [])
            if not more_rows:
                print("DEBUG: 页面无数据，停止分页")
                break
            
            # 添加数据（带去重）
            added_count = 0
            for row in more_rows:
                row_id = row.get("Id") or row.get("id")
                if row_id not in seen_ids:
                    seen_ids.add(row_id)
                    all_rows.append(row)
                    added_count += 1
            
            print(f"DEBUG: 本页新增 {added_count} 条记录，累计 {len(all_rows)} 条")
            
            # 如果本页没有新增记录，可能是重复数据，停止
            if added_count == 0:
                print("DEBUG: 本页无新增记录，停止分页")
                break
            
            offset += limit

    print(f"DEBUG: 最终获取 {len(all_rows)} 条去重后的记录")
    return all_rows

def upgrade_firmware(rows: List[Dict]) -> List:
    """
    升级固件准备方法:
    1. 遍历隧道数据
    2. 当 target_str == '127.0.0.1:22' 且 is_connect 为 True 时，将该隧道的 target_port 收集到列表中
    3. 返回待升级端口列表（后续实际升级逻辑可在别处实现）
    """
    if not rows:
        print("未找到隧道信息或请求失败，无法准备固件升级。")
        return []
    upgrade_ports: List = []
    match_count = 0
    for r in rows:
        try:
            target_str = r.get('Target', {}).get('TargetStr')
            is_connect = r.get('Client', {}).get('IsConnect')
            target_port = r.get('Port', {})
            if target_str == '127.0.0.1:22' and is_connect is True:
                match_count += 1
                upgrade_ports.append(target_port)
        except Exception as e:
            print(f"处理隧道数据出错: {e}")
    print(f"共扫描 {len(rows)} 条隧道，匹配到 {match_count} 条可进行固件升级的隧道。")
    # 开始固件升级占位逻辑（实现 SSH 检查，不改变原始“逻辑占位”语义）
    def _extract_port_value(p):
        if isinstance(p, int):
            return p
        if isinstance(p, str) and p.isdigit():
            return int(p)
        if isinstance(p, dict):
            for k in ("Port", "port", "ServerPort", "ClientPort"):
                v = p.get(k)
                if isinstance(v, int):
                    return v
                if isinstance(v, str) and v.isdigit():
                    return int(v)
        return None
    def _ssh_check_and_upgrade(port_num: int) -> Dict:
        result = {
            "port": port_num,
            "service_status": "unknown",
            "upgrade_status": "skipped",
            "auth_used": None,
            "error": None
        }
        if paramiko is None:
            result["error"] = "paramiko not installed"
            print(f"WARNING: 未安装 paramiko，跳过端口 {port_num} 的 SSH 检查。")
            return result
        print(f"DEBUG: 将对端口 {port_num} 尝试 {len(NPSConstants.SSH_PASSWORDS)} 个候选密码进行认证")
        host = NPSConstants.SSH_HOST
        user = NPSConstants.SSH_USER
        passwords = NPSConstants.SSH_PASSWORDS
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected = False
        for pwd in passwords:
            try:
                client.connect(hostname=host, port=port_num, username=user,
                               password=pwd, timeout=8, auth_timeout=8, banner_timeout=8)
                connected = True
                result["auth_used"] = "<matched_password>"  # 不直接打印真实密码
                break
            except paramiko.AuthenticationException:
                continue
            except Exception as e:
                result["error"] = f"连接失败: {e}"
                break
        if not connected:
            if result["error"] is None:
                result["error"] = "认证失败"
            print(f"DEBUG: 端口 {port_num} SSH 连接失败: {result['error']}")
            try:
                client.close()
            except Exception:
                pass
            return result
        try:
            print(f"DEBUG: 端口 {port_num} 已连接，检查 musicbox.service 状态")
            stdin, stdout, stderr = client.exec_command("systemctl is-active musicbox.service", timeout=10)
            status = stdout.read().decode().strip()
            if not status:
                status = stderr.read().decode().strip() or "unknown"
            result["service_status"] = status
            if status == "active":
                # 占位：未真正执行升级，只打印说明（保持“暂时留空”逻辑不变）
                print(f"端口 {port_num} 的服务处于活跃状态，(占位) 未执行实际升级步骤。")
                # 可在此处未来添加真实升级命令:
                # upgrade_cmd = "sh /usr/local/bin/upgrade_musicbox.sh"
                # stdin, stdout, stderr = client.exec_command(upgrade_cmd, timeout=300)
                # exit_code = stdout.channel.recv_exit_status()
                # 根据 exit_code 设置 upgrade_status
                result["upgrade_status"] = "pending"  # 表示等待未来真实升级实现
            else:
                print(f"端口 {port_num} 的服务不处于活跃状态(状态={status})，跳过升级。")
                result["upgrade_status"] = "skipped"
        except Exception as e:
            result["error"] = f"执行命令失败: {e}"
            print(f"DEBUG: 端口 {port_num} 状态检查出错: {e}")
        finally:
            try:
                client.close()
            except Exception:
                pass
        return result
    upgrade_results: List[Dict] = []
    for port in upgrade_ports:
        print(f"DEBUG: 准备检查端口 {port} 的服务状态")
        port_num = _extract_port_value(port)
        if port_num is None:
            print(f"WARNING: 端口字段无法解析为整数: {port}")
            upgrade_results.append({
                "port": port,
                "service_status": "unknown",
                "upgrade_status": "skipped",
                "error": "invalid_port_format"
            })
            continue
        res = _ssh_check_and_upgrade(port_num)
        upgrade_results.append(res)
    #2/3/4 步骤仍为占位（未改变原有注释语义）
    if upgrade_ports:
        print(f"待升级端口列表: {upgrade_ports}")
    else:
        print("暂无可升级目标。")
    print("升级结果概览:")
    for r in upgrade_results:
        print(r)
    return upgrade_ports

def main():
    print("开始从 NPS 获取隧道信息...")
    print(f"DEBUG: NPS_API_BASE_URL = {NPSConstants.NPS_API_BASE_URL}")
    print(f"DEBUG: NPS_AUTH_KEY = {NPSConstants.NPS_AUTH_KEY}")
    rows = fetch_all_tunnels()
    upgrade_ports = upgrade_firmware(rows)


if __name__ == "__main__":
    main()