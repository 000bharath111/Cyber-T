import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import os
import sqlite3
from PIL import Image, ImageTk
import io
import base64
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import winsound
import ast
import re
import hashlib
import mimetypes
import webbrowser
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import queue
import socket
import ipaddress
import subprocess
import re
import http.server
import socketserver
import threading
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
try:
    import dns.resolver
    import dns.reversename
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

class ThreadLocalDB:
    def __init__(self, db_path='cyber_t.db'):
        self.db_path = db_path
        self.local = threading.local()
    
    def get_connection(self):
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.local.connection
    
    def close_all(self):
        if hasattr(self.local, 'connection'):
            self.local.connection.close()

class CyberT:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cyber-T - Advanced Security Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg="#18191A")
        
        self.db_manager = ThreadLocalDB()
        
        self.sound_enabled = True
        
        self.scan_progress_count = 0
        self.scan_total_count = 0
        
        self.last_sound_time = 0
        self.sound_throttle_ms = 100  
        
        self.vulnerability_patterns = self._init_vulnerability_patterns()
        self.uploaded_files = []
        self.analysis_results = []
        
        self.setup_styling()
        
        self.init_database()
        
        self.proxy_server = None
        self.proxy_running = False
        self.intercepted_requests = []
        self.intercepted_responses = []
        self.intercept_enabled = False
        
        self.create_main_interface()
        
    def setup_styling(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        
        style.configure('TFrame', background='#18191A')
        style.configure('TLabel', background='#18191A', foreground='#FF0000')
        style.configure('TButton', background='#2D2D2D', foreground='#FF0000', 
                       borderwidth=1, relief='solid')
        style.map('TButton', background=[('active', '#3D3D3D')])
        
        style.configure('TEntry', fieldbackground='#2D2D2D', foreground='#FFFFFF', 
                       borderwidth=1, relief='solid')
        style.configure('TText', background='#2D2D2D', foreground='#FFFFFF', 
                       borderwidth=1, relief='solid')
        
        self.create_logo()
        
    def create_logo(self):
        try:
            if os.path.exists('image.png'):
                logo = Image.open('image.png')
                if logo.size != (40, 40):
                    logo = logo.resize((40, 40), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo)
                print("✅ Logo loaded from image.png")
            else:
            
    
    def create_fallback_logo(self):
        logo_size = 40
        logo = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
        
        from PIL import ImageDraw
        draw = ImageDraw.Draw(logo)
        
        draw.ellipse([2, 2, logo_size-2, logo_size-2], outline='#FF0000', width=2)
        
        center = logo_size // 2
        draw.polygon([(center, 8), (center-8, 16), (center-4, 24), 
                     (center+4, 24), (center+8, 16)], fill='#FF0000')
        
        self.logo_image = ImageTk.PhotoImage(logo)
        print("✅ Fallback logo created")
        
    def init_database(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                method TEXT NOT NULL,
                url TEXT NOT NULL,
                headers TEXT,
                body TEXT,
                expected_status INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                result TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT,
                status TEXT,
                assigned_to TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    def _init_vulnerability_patterns(self):
        return {
            'sql_injection': {
                'patterns': [
                    r'SELECT.*FROM.*WHERE.*\+.*request\.',
                    r'INSERT.*INTO.*VALUES.*\+.*request\.',
                    r'UPDATE.*SET.*=.*\+.*request\.',
                    r'DELETE.*FROM.*WHERE.*\+.*request\.',
                    r'exec.*\(.*request\.',
                    r'execute.*\(.*request\.',
                    r'query.*\(.*request\.',
                    r'cursor\.execute.*%s',
                    r'cursor\.execute.*format',
                    r'cursor\.execute.*\+',
                    r'cursor\.execute.*%\(',
                    r'\.format\(.*request\.',
                    r'%s.*%request\.',
                    r'%\(.*request\.',
                ],
                'severity': 'HIGH',
                'description': 'SQL Injection vulnerability detected'
            },
            'xss': {
                'patterns': [
                    r'innerHTML.*=.*request\.',
                    r'outerHTML.*=.*request\.',
                    r'insertAdjacentHTML.*request\.',
                    r'document\.write.*request\.',
                    r'eval.*\(.*request\.',
                    r'setTimeout.*request\.',
                    r'setInterval.*request\.',
                    r'Function.*request\.',
                    r'new Function.*request\.',
                    r'\.html\(.*request\.',
                    r'\.append.*request\.',
                    r'\.prepend.*request\.',
                    r'response\.write.*request\.',
                    r'print.*request\.',
                    r'echo.*request\.',
                ],
                'severity': 'HIGH',
                'description': 'Cross-Site Scripting (XSS) vulnerability detected'
            },
            'command_injection': {
                'patterns': [
                    r'os\.system.*request\.',
                    r'subprocess\.call.*request\.',
                    r'subprocess\.run.*request\.',
                    r'os\.popen.*request\.',
                    r'exec.*\(.*request\.',
                    r'eval.*\(.*request\.',
                    r'Process\.start.*request\.',
                    r'Runtime\.exec.*request\.',
                    r'shell_exec.*request\.',
                    r'system.*request\.',
                    r'passthru.*request\.',
                    r'exec.*request\.',
                ],
                'severity': 'CRITICAL',
                'description': 'Command Injection vulnerability detected'
            },
            'path_traversal': {
                'patterns': [
                    r'open\(.*request\.',
                    r'file_get_contents.*request\.',
                    r'readfile.*request\.',
                    r'include.*request\.',
                    r'require.*request\.',
                    r'File\.ReadAllText.*request\.',
                    r'File\.ReadAllBytes.*request\.',
                    r'Files\.readAllBytes.*request\.',
                    r'Files\.readAllLines.*request\.',
                    r'\.\.\/',
                    r'\.\.\\',
                    r'%2e%2e%2f',
                    r'%2e%2e%5c',
                ],
                'severity': 'HIGH',
                'description': 'Path Traversal vulnerability detected'
            },
            'hardcoded_secrets': {
                'patterns': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']',
                    r'private_key\s*=\s*["\'][^"\']+["\']',
                    r'access_token\s*=\s*["\'][^"\']+["\']',
                    r'aws_access_key\s*=\s*["\'][^"\']+["\']',
                    r'aws_secret_key\s*=\s*["\'][^"\']+["\']',
                    r'connectionString\s*=\s*["\'][^"\']+["\']',
                    r'database_url\s*=\s*["\'][^"\']+["\']',
                ],
                'severity': 'MEDIUM',
                'description': 'Hardcoded secrets detected'
            },
            'weak_crypto': {
                'patterns': [
                    r'MD5\(',
                    r'SHA1\(',
                    r'DES\(',
                    r'RC4\(',
                    r'hashlib\.md5',
                    r'hashlib\.sha1',
                    r'Crypto\.Cipher\.DES',
                    r'Crypto\.Cipher\.RC4',
                    r'MessageDigest\.getInstance\("MD5"',
                    r'MessageDigest\.getInstance\("SHA1"',
                    r'md5\(',
                    r'sha1\(',
                    r'des\(',
                    r'rc4\(',
                ],
                'severity': 'MEDIUM',
                'description': 'Weak cryptographic algorithm detected'
            },
            'insecure_random': {
                'patterns': [
                    r'random\.random\(\)',
                    r'Math\.random\(\)',
                    r'new Random\(\)',
                    r'Random\.nextInt\(\)',
                    r'rand\(\)',
                    r'mt_rand\(\)',
                    r'random\(\)',
                ],
                'severity': 'MEDIUM',
                'description': 'Insecure random number generation detected'
            },
            'buffer_overflow': {
                'patterns': [
                    r'strcpy\(',
                    r'strcat\(',
                    r'sprintf\(',
                    r'gets\(',
                    r'scanf\(',
                    r'sprintf_s\(',
                    r'strcpy_s\(',
                    r'strcat_s\(',
                ],
                'severity': 'HIGH',
                'description': 'Potential buffer overflow vulnerability'
            },
            'memory_leak': {
                'patterns': [
                    r'malloc\(.*\).*[^free]',
                    r'new\s+\w+.*[^delete]',
                    r'new\s+\w+\[.*\].*[^delete\[\]]',
                    r'GlobalAlloc\(',
                    r'LocalAlloc\(',
                    r'VirtualAlloc\(',
                ],
                'severity': 'MEDIUM',
                'description': 'Potential memory leak detected'
            },
            'insecure_deserialization': {
                'patterns': [
                    r'pickle\.loads\(',
                    r'pickle\.load\(',
                    r'cPickle\.loads\(',
                    r'cPickle\.load\(',
                    r'json\.loads.*allow_pickle=True',
                    r'yaml\.load\(',
                    r'yaml\.safe_load\(',
                    r'ObjectInputStream',
                    r'readObject\(',
                    r'unserialize\(',
                    r'deserialize\(',
                ],
                'severity': 'HIGH',
                'description': 'Insecure deserialization vulnerability detected'
            }
        }
    
    def play_sound(self, sound_type="start"):
        if not self.sound_enabled:
            return
            
        try:
            if sound_type == "start":
                winsound.Beep(1200, 300)
            elif sound_type == "complete":
                winsound.Beep(1500, 200)
                time.sleep(0.1)
                winsound.Beep(1800, 200)
            elif sound_type == "error":
                winsound.Beep(500, 500)
            elif sound_type == "scan_progress":
                winsound.Beep(800, 100)
            elif sound_type == "scan_success":
                winsound.Beep(1000, 150)
        except Exception as e:
            pass
    
    def _update_scan_progress(self):
        if self.scan_total_count > 0:
            progress_percent = (self.scan_progress_count / self.scan_total_count) * 100
            self.scan_status_label.config(text=f"🔍 Scanning... {self.scan_progress_count}/{self.scan_total_count} ({progress_percent:.1f}%)")
        
    def create_main_interface(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        logo_label = ttk.Label(header_frame, image=self.logo_image)
        logo_label.pack(side='left', padx=(0, 10))
        
        title_label = ttk.Label(header_frame, text="Cyber-T", 
                               font=('Arial', 24, 'bold'))
        title_label.pack(side='left')
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Advanced Security Tool by S.Tamilselvan", 
                                  font=('Arial', 10))
        subtitle_label.pack(side='left', padx=(10, 0))
        
        community_frame = ttk.Frame(header_frame)
        community_frame.pack(side='right', padx=10)
        
        ttk.Button(community_frame, text="💬 Community Support", 
                  command=self.open_community_support, 
                  style='Accent.TButton').pack(side='right', padx=5)
        
        ttk.Button(community_frame, text="🌐 Cyber Chat", 
                  command=self.open_cyber_chat, 
                  style='Accent.TButton').pack(side='right', padx=5)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.create_proxy_interceptor_tab()
        self.create_api_tester_tab()
        self.create_security_scanner_tab()
        self.create_source_code_analyzer_tab()
        self.create_network_analysis_tab()
        self.create_dashboard_tab()
        
        self.scan_results_queue = queue.Queue()
        self.scanning_active = False
        
    def create_proxy_interceptor_tab(self):
        proxy_frame = ttk.Frame(self.notebook)
        self.notebook.add(proxy_frame, text="🔄 Proxy Interceptor")
        
        control_frame = ttk.LabelFrame(proxy_frame, text="Proxy Server Controls")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill='x', pady=5)
        
        ttk.Label(settings_frame, text="Proxy Port:").pack(side='left', padx=(0, 5))
        self.proxy_port_var = tk.StringVar(value="8080")
        port_entry = ttk.Entry(settings_frame, textvariable=self.proxy_port_var, width=10)
        port_entry.pack(side='left', padx=(0, 20))
        
        intercept_frame = ttk.Frame(control_frame)
        intercept_frame.pack(fill='x', pady=5)
        
        self.intercept_requests_var = tk.BooleanVar(value=True)
        self.intercept_responses_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(intercept_frame, text="Intercept Requests", 
                       variable=self.intercept_requests_var).pack(side='left', padx=(0, 20))
        ttk.Checkbutton(intercept_frame, text="Intercept Responses", 
                       variable=self.intercept_responses_var).pack(side='left', padx=(0, 20))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.start_proxy_btn = ttk.Button(button_frame, text="🚀 Start Proxy", 
                                         command=self.start_proxy_server)
        self.start_proxy_btn.pack(side='left', padx=(0, 10))
        
        self.stop_proxy_btn = ttk.Button(button_frame, text="⏹️ Stop Proxy", 
                                        command=self.stop_proxy_server, state='disabled')
        self.stop_proxy_btn.pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Clear Traffic", 
                  command=self.clear_traffic).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="📄 Export Traffic", 
                  command=self.export_traffic).pack(side='left')
        
        self.proxy_status_label = ttk.Label(control_frame, text="Proxy Status: Stopped", 
                                           font=('Arial', 10, 'bold'))
        self.proxy_status_label.pack(pady=5)
        
        legend_frame = ttk.Frame(control_frame)
        legend_frame.pack(fill='x', pady=5)
        
        ttk.Label(legend_frame, text="Vulnerability Legend:", font=('Arial', 9, 'bold')).pack(anchor='w')
        
        legend_items_frame = ttk.Frame(legend_frame)
        legend_items_frame.pack(fill='x', pady=2)
        
        legend_items = [
            ('🔴 HIGH', '#2D1B1B', '#FF6B6B'),
            ('🟡 MEDIUM', '#2D2B1B', '#FFD93D'),
            ('🟢 LOW', '#1B2D2B', '#6BCF7F'),
            ('⚪ NONE', '#2D2D2D', '#FFFFFF')
        ]
        
        for i, (text, bg_color, fg_color) in enumerate(legend_items):
            legend_item = tk.Label(legend_items_frame, text=text, 
                                 bg=bg_color, fg=fg_color, font=('Arial', 8))
            legend_item.pack(side='left', padx=(0, 10))
        
        content_frame = ttk.Frame(proxy_frame)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.traffic_notebook = ttk.Notebook(content_frame)
        self.traffic_notebook.pack(fill='both', expand=True)
        
        requests_frame = ttk.Frame(self.traffic_notebook)
        self.traffic_notebook.add(requests_frame, text="📥 Intercepted Requests")
        
        requests_list_frame = ttk.Frame(requests_frame)
        requests_list_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        ttk.Label(requests_list_frame, text="Intercepted Requests", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        self.requests_listbox = tk.Listbox(requests_list_frame, bg='#2D2D2D', fg='#FFFFFF',
                                          selectbackground='#3D3D3D', font=('Consolas', 9))
        self.requests_listbox.pack(fill='both', expand=True)
        self.requests_listbox.bind('<<ListboxSelect>>', self.on_request_select)
        
        request_details_frame = ttk.Frame(requests_frame)
        request_details_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        ttk.Label(request_details_frame, text="Request Details", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        self.request_details_text = tk.Text(request_details_frame, bg='#2D2D2D', fg='#FFFFFF',
                                           font=('Consolas', 9))
        request_scrollbar = ttk.Scrollbar(request_details_frame, orient='vertical', 
                                         command=self.request_details_text.yview)
        self.request_details_text.configure(yscrollcommand=request_scrollbar.set)
        self.request_details_text.pack(side='left', fill='both', expand=True)
        request_scrollbar.pack(side='right', fill='y')
        
        request_actions_frame = ttk.Frame(request_details_frame)
        request_actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(request_actions_frame, text="✅ Forward", 
                  command=self.forward_request).pack(side='left', padx=(0, 5))
        ttk.Button(request_actions_frame, text="✏️ Edit", 
                  command=self.edit_request).pack(side='left', padx=(0, 5))
        ttk.Button(request_actions_frame, text="❌ Drop", 
                  command=self.drop_request).pack(side='left')
        
        responses_frame = ttk.Frame(self.traffic_notebook)
        self.traffic_notebook.add(responses_frame, text="📤 Intercepted Responses")
        
        responses_list_frame = ttk.Frame(responses_frame)
        responses_list_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        ttk.Label(responses_list_frame, text="Intercepted Responses", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        self.responses_listbox = tk.Listbox(responses_list_frame, bg='#2D2D2D', fg='#FFFFFF',
                                           selectbackground='#3D3D3D', font=('Consolas', 9))
        self.responses_listbox.pack(fill='both', expand=True)
        self.responses_listbox.bind('<<ListboxSelect>>', self.on_response_select)
        
        response_details_frame = ttk.Frame(responses_frame)
        response_details_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        ttk.Label(response_details_frame, text="Response Details", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        self.response_details_text = tk.Text(response_details_frame, bg='#2D2D2D', fg='#FFFFFF',
                                            font=('Consolas', 9))
        response_scrollbar = ttk.Scrollbar(response_details_frame, orient='vertical', 
                                          command=self.response_details_text.yview)
        self.response_details_text.configure(yscrollcommand=response_scrollbar.set)
        self.response_details_text.pack(side='left', fill='both', expand=True)
        response_scrollbar.pack(side='right', fill='y')
        
        response_actions_frame = ttk.Frame(response_details_frame)
        response_actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(response_actions_frame, text="✅ Forward", 
                  command=self.forward_response).pack(side='left', padx=(0, 5))
        ttk.Button(response_actions_frame, text="✏️ Edit", 
                  command=self.edit_response).pack(side='left', padx=(0, 5))
        ttk.Button(response_actions_frame, text="❌ Drop", 
                  command=self.drop_response).pack(side='left')
        
    def analyze_request_vulnerability(self, request_data):
        vulnerability_score = 0
        method = request_data.get('method', '').upper()
        url = request_data.get('url', '').lower()
        headers = request_data.get('headers', {})
        body = request_data.get('body', '').lower()
        
        if method in ['PUT', 'DELETE', 'PATCH', 'TRACE']:
            vulnerability_score += 2
        
        sensitive_paths = ['admin', 'login', 'api', 'config', 'backup', 'test', 'debug']
        for path in sensitive_paths:
            if path in url:
                vulnerability_score += 1
        
        sql_patterns = ['union', 'select', 'insert', 'delete', 'drop', 'exec', 'script']
        for pattern in sql_patterns:
            if pattern in url or pattern in body:
                vulnerability_score += 2
        
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'alert(']
        for pattern in xss_patterns:
            if pattern in url or pattern in body:
                vulnerability_score += 2
        
        if '../' in url or '..\\' in url:
            vulnerability_score += 3
        
        security_headers = ['x-frame-options', 'x-content-type-options', 'x-xss-protection']
        for header in security_headers:
            if header not in [h.lower() for h in headers.keys()]:
                vulnerability_score += 1
                if 'authorization' in [h.lower() for h in headers.keys()]:
            auth_header = headers.get('Authorization', '')
            if 'basic' in auth_header.lower() and not auth_header.endswith('='):
                vulnerability_score += 2
        
        if vulnerability_score >= 5:
            return 'HIGH'
        elif vulnerability_score >= 3:
            return 'MEDIUM'
        elif vulnerability_score >= 1:
            return 'LOW'
        else:
            return 'NONE'
    
    def analyze_response_vulnerability(self, response_data):
        vulnerability_score = 0
        status = response_data.get('status', 0)
        headers = response_data.get('headers', {})
        body = response_data.get('body', '').lower()
        
        if status in [500, 501, 502, 503, 504]:
            vulnerability_score += 1  # Server errors can reveal information
        
        security_headers = {
            'x-frame-options': 2,
            'x-content-type-options': 1,
            'x-xss-protection': 1,
            'strict-transport-security': 2,
            'content-security-policy': 2
        }
        
        for header, score in security_headers.items():
            if header not in [h.lower() for h in headers.keys()]:
                vulnerability_score += score
        
        sensitive_info = ['password', 'token', 'key', 'secret', 'api_key', 'database']
        for info in sensitive_info:
            if info in body:
                vulnerability_score += 2
        
        error_patterns = ['stack trace', 'exception', 'error in', 'warning:', 'notice:']
        for pattern in error_patterns:
            if pattern in body:
                vulnerability_score += 1
        
        if 'debug' in body or 'development' in body:
            vulnerability_score += 2
        
        if 'index of' in body or 'parent directory' in body:
            vulnerability_score += 3
        
        if vulnerability_score >= 6:
            return 'HIGH'
        elif vulnerability_score >= 3:
            return 'MEDIUM'
        elif vulnerability_score >= 1:
            return 'LOW'
        else:
            return 'NONE'
    
    def get_vulnerability_indicator(self, level):
        indicators = {
            'HIGH': '🔴',    # Red circle
            'MEDIUM': '🟡',  # Yellow circle
            'LOW': '🟢',     # Green circle
            'NONE': '⚪'     # White circle
        }
        return indicators.get(level, '⚪')
        
    def start_proxy_server(self):
        try:
            port = int(self.proxy_port_var.get())
            self.proxy_server = ProxyServer(('localhost', port), ProxyHandler, self)
            self.proxy_thread = threading.Thread(target=self.proxy_server.serve_forever, daemon=True)
            self.proxy_thread.start()
            
            self.proxy_running = True
            self.start_proxy_btn.config(state='disabled')
            self.stop_proxy_btn.config(state='normal')
            self.proxy_status_label.config(text=f"Proxy Status: Running on port {port}")
            
            self.play_sound("start")
            
            messagebox.showinfo("Success", f"Proxy server started on port {port}\n\n"
                                          f"Configure your browser or application to use:\n"
                                          f"HTTP Proxy: localhost:{port}\n"
                                          f"HTTPS Proxy: localhost:{port}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start proxy server: {str(e)}")
            
    def stop_proxy_server(self):
        try:
            if self.proxy_server:
                self.proxy_server.shutdown()
                self.proxy_server = None
                
            self.proxy_running = False
            self.start_proxy_btn.config(state='normal')
            self.stop_proxy_btn.config(state='disabled')
            self.proxy_status_label.config(text="Proxy Status: Stopped")
            
            self.play_sound("complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop proxy server: {str(e)}")
            
    def add_intercepted_request(self, request_data):
        self.intercepted_requests.append(request_data)
        
        vulnerability_level = self.analyze_request_vulnerability(request_data)
        
        vuln_indicator = self.get_vulnerability_indicator(vulnerability_level)
        display_text = f"{vuln_indicator} {request_data.get('method', 'UNKNOWN')} {request_data.get('url', 'Unknown URL')}"
        
        index = self.requests_listbox.size()
        self.requests_listbox.insert(tk.END, display_text)
        
        if vulnerability_level == 'HIGH':
            self.requests_listbox.itemconfig(index, {'bg': '#2D1B1B', 'fg': '#FF6B6B'})  # Dark red
        elif vulnerability_level == 'MEDIUM':
            self.requests_listbox.itemconfig(index, {'bg': '#2D2B1B', 'fg': '#FFD93D'})  # Dark yellow
        elif vulnerability_level == 'LOW':
            self.requests_listbox.itemconfig(index, {'bg': '#1B2D2B', 'fg': '#6BCF7F'})  # Dark green
        else:
            self.requests_listbox.itemconfig(index, {'bg': '#2D2D2D', 'fg': '#FFFFFF'})  # Default dark
        
    def add_intercepted_response(self, response_data):
        self.intercepted_responses.append(response_data)
        
        vulnerability_level = self.analyze_response_vulnerability(response_data)
        
        vuln_indicator = self.get_vulnerability_indicator(vulnerability_level)
        display_text = f"{vuln_indicator} {response_data.get('status', 'Unknown')} {response_data.get('url', 'Unknown URL')}"
        
        index = self.responses_listbox.size()
        self.responses_listbox.insert(tk.END, display_text)
        
        if vulnerability_level == 'HIGH':
            self.responses_listbox.itemconfig(index, {'bg': '#2D1B1B', 'fg': '#FF6B6B'})  # Dark red
        elif vulnerability_level == 'MEDIUM':
            self.responses_listbox.itemconfig(index, {'bg': '#2D2B1B', 'fg': '#FFD93D'})  # Dark yellow
        elif vulnerability_level == 'LOW':
            self.responses_listbox.itemconfig(index, {'bg': '#1B2D2B', 'fg': '#6BCF7F'})  # Dark green
        else:
            self.responses_listbox.itemconfig(index, {'bg': '#2D2D2D', 'fg': '#FFFFFF'})  # Default dark
        
    def on_request_select(self, event):
        selection = self.requests_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_requests):
                request_data = self.intercepted_requests[index]
                self.display_request_details(request_data)
                
    def on_response_select(self, event):
        selection = self.responses_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_responses):
                response_data = self.intercepted_responses[index]
                self.display_response_details(response_data)
                
    def display_request_details(self, request_data):
        self.request_details_text.delete(1.0, tk.END)
                vulnerability_level = self.analyze_request_vulnerability(request_data)
        vuln_indicator = self.get_vulnerability_indicator(vulnerability_level)
        
        details = []
        details.append(f"🔍 VULNERABILITY ANALYSIS: {vuln_indicator} {vulnerability_level}")
        details.append("=" * 50)
        details.append("")
        details.append(f"Method: {request_data.get('method', 'Unknown')}")
        details.append(f"URL: {request_data.get('url', 'Unknown')}")
        details.append(f"Version: {request_data.get('version', 'Unknown')}")
        details.append("")
        details.append("Headers:")
        details.append("-" * 20)
        
        headers = request_data.get('headers', {})
        for key, value in headers.items():
            details.append(f"{key}: {value}")
            
        details.append("")
        details.append("Body:")
        details.append("-" * 20)
        details.append(request_data.get('body', 'No body'))
        
        details.append("")
        details.append("🔒 SECURITY ANALYSIS:")
        details.append("-" * 20)
        
        method = request_data.get('method', '').upper()
        url = request_data.get('url', '').lower()
        body = request_data.get('body', '').lower()
        
        if method in ['PUT', 'DELETE', 'PATCH', 'TRACE']:
            details.append(f"⚠️  Dangerous HTTP method: {method}")
        
        if any(path in url for path in ['admin', 'login', 'api', 'config']):
            details.append("⚠️  Sensitive endpoint detected")
        
        if any(pattern in url or pattern in body for pattern in ['union', 'select', 'script']):
            details.append("⚠️  Potential SQL injection or XSS detected")
        
        if '../' in url or '..\\' in url:
            details.append("⚠️  Path traversal attempt detected")
        
        self.request_details_text.insert(1.0, "\n".join(details))
        
    def display_response_details(self, response_data):
        self.response_details_text.delete(1.0, tk.END)
        
        vulnerability_level = self.analyze_response_vulnerability(response_data)
        vuln_indicator = self.get_vulnerability_indicator(vulnerability_level)
        
        details = []
        details.append(f"🔍 VULNERABILITY ANALYSIS: {vuln_indicator} {vulnerability_level}")
        details.append("=" * 50)
        details.append("")
        details.append(f"Status: {response_data.get('status', 'Unknown')}")
        details.append(f"URL: {response_data.get('url', 'Unknown')}")
        details.append(f"Version: {response_data.get('version', 'Unknown')}")
        details.append("")
        details.append("Headers:")
        details.append("-" * 20)
        
        headers = response_data.get('headers', {})
        for key, value in headers.items():
            details.append(f"{key}: {value}")
            
        details.append("")
        details.append("Body:")
        details.append("-" * 20)
        body = response_data.get('body', 'No body')
        if len(body) > 2000:
            body = body[:2000] + "\n... (truncated)"
        details.append(body)
        
        details.append("")
        details.append("🔒 SECURITY ANALYSIS:")
        details.append("-" * 20)
        
        status = response_data.get('status', 0)
        headers_lower = {k.lower(): v for k, v in headers.items()}
        body_lower = body.lower()
        
        if status in [500, 501, 502, 503, 504]:
            details.append(f"⚠️  Server error status: {status}")
        
        missing_headers = []
        security_headers = ['x-frame-options', 'x-content-type-options', 'x-xss-protection', 
                           'strict-transport-security', 'content-security-policy']
        for header in security_headers:
            if header not in headers_lower:
                missing_headers.append(header)
        
        if missing_headers:
            details.append(f"⚠️  Missing security headers: {', '.join(missing_headers)}")
        
        if any(info in body_lower for info in ['password', 'token', 'key', 'secret']):
            details.append("⚠️  Sensitive information detected in response")
        
        if 'debug' in body_lower or 'development' in body_lower:
            details.append("⚠️  Debug information exposed")
        
        self.response_details_text.insert(1.0, "\n".join(details))
        
    def forward_request(self):
        selection = self.requests_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_requests):
                request_data = self.intercepted_requests.pop(index)
                self.requests_listbox.delete(index)
                self.request_details_text.delete(1.0, tk.END)
                messagebox.showinfo("Success", "Request forwarded successfully")
                
    def forward_response(self):
        selection = self.responses_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_responses):
                # Remove from intercepted list
                response_data = self.intercepted_responses.pop(index)
                self.responses_listbox.delete(index)
                self.response_details_text.delete(1.0, tk.END)
                messagebox.showinfo("Success", "Response forwarded successfully")
                
    def edit_request(self):
        selection = self.requests_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_requests):
                self.open_request_editor(index)
                
    def edit_response(self):
        selection = self.responses_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_responses):
                self.open_response_editor(index)
                
    def drop_request(self):
        selection = self.requests_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_requests):
                self.intercepted_requests.pop(index)
                self.requests_listbox.delete(index)
                self.request_details_text.delete(1.0, tk.END)
                messagebox.showinfo("Success", "Request dropped successfully")
                
    def drop_response(self):
        selection = self.responses_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.intercepted_responses):
                self.intercepted_responses.pop(index)
                self.responses_listbox.delete(index)
                self.response_details_text.delete(1.0, tk.END)
                messagebox.showinfo("Success", "Response dropped successfully")
                
    def open_request_editor(self, index):
        request_data = self.intercepted_requests[index]
        
        editor = tk.Toplevel(self.root)
        editor.title("Edit Request")
        editor.geometry("800x600")
        editor.configure(bg='#18191A')
        
        ttk.Label(editor, text="Edit HTTP Request", font=('Arial', 14, 'bold')).pack(pady=10)
                method_frame = ttk.Frame(editor)
        method_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(method_frame, text="Method:").pack(side='left', padx=(0, 5))
        method_var = tk.StringVar(value=request_data.get('method', 'GET'))
        method_combo = ttk.Combobox(method_frame, textvariable=method_var,
                                   values=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
        method_combo.pack(side='left', padx=(0, 20))
        
        ttk.Label(method_frame, text="URL:").pack(side='left', padx=(0, 5))
        url_var = tk.StringVar(value=request_data.get('url', ''))
        url_entry = ttk.Entry(method_frame, textvariable=url_var, width=50)
        url_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Label(editor, text="Headers:", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        headers_text = tk.Text(editor, height=8, bg='#2D2D2D', fg='#FFFFFF', font=('Consolas', 9))
        headers_text.pack(fill='x', padx=10, pady=5)
        
        headers = request_data.get('headers', {})
        headers_content = []
        for key, value in headers.items():
            headers_content.append(f"{key}: {value}")
        headers_text.insert(1.0, "\n".join(headers_content))
        
        ttk.Label(editor, text="Body:", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        body_text = tk.Text(editor, height=10, bg='#2D2D2D', fg='#FFFFFF', font=('Consolas', 9))
        body_text.pack(fill='both', expand=True, padx=10, pady=5)
        body_text.insert(1.0, request_data.get('body', ''))
        
        button_frame = ttk.Frame(editor)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def save_request():
            request_data['method'] = method_var.get()
            request_data['url'] = url_var.get()
            
            headers_content = headers_text.get(1.0, tk.END).strip()
            new_headers = {}
            for line in headers_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    new_headers[key.strip()] = value.strip()
            request_data['headers'] = new_headers
            
            request_data['body'] = body_text.get(1.0, tk.END).strip()
            
            self.display_request_details(request_data)
            editor.destroy()
            messagebox.showinfo("Success", "Request updated successfully")
            
        ttk.Button(button_frame, text="💾 Save", command=save_request).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=editor.destroy).pack(side='left', padx=5)
        
    def open_response_editor(self, index):
        response_data = self.intercepted_responses[index]
        
        editor = tk.Toplevel(self.root)
        editor.title("Edit Response")
        editor.geometry("800x600")
        editor.configure(bg='#18191A')
        
        ttk.Label(editor, text="Edit HTTP Response", font=('Arial', 14, 'bold')).pack(pady=10)
        
        status_frame = ttk.Frame(editor)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side='left', padx=(0, 5))
        status_var = tk.StringVar(value=str(response_data.get('status', '200')))
        status_entry = ttk.Entry(status_frame, textvariable=status_var, width=10)
        status_entry.pack(side='left')
        
        ttk.Label(editor, text="Headers:", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        headers_text = tk.Text(editor, height=8, bg='#2D2D2D', fg='#FFFFFF', font=('Consolas', 9))
        headers_text.pack(fill='x', padx=10, pady=5)
        
        headers = response_data.get('headers', {})
        headers_content = []
        for key, value in headers.items():
            headers_content.append(f"{key}: {value}")
        headers_text.insert(1.0, "\n".join(headers_content))
        
        ttk.Label(editor, text="Body:", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        body_text = tk.Text(editor, height=10, bg='#2D2D2D', fg='#FFFFFF', font=('Consolas', 9))
        body_text.pack(fill='both', expand=True, padx=10, pady=5)
        body_text.insert(1.0, response_data.get('body', ''))
        
        
        button_frame = ttk.Frame(editor)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def save_response():
            response_data['status'] = int(status_var.get())
            
            headers_content = headers_text.get(1.0, tk.END).strip()
            new_headers = {}
            for line in headers_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    new_headers[key.strip()] = value.strip()
            response_data['headers'] = new_headers
            
            response_data['body'] = body_text.get(1.0, tk.END).strip()
            
            self.display_response_details(response_data)
            editor.destroy()
            messagebox.showinfo("Success", "Response updated successfully")
            
        ttk.Button(button_frame, text="💾 Save", command=save_response).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=editor.destroy).pack(side='left', padx=5)
        
    def clear_traffic(self):
        self.intercepted_requests.clear()
        self.intercepted_responses.clear()
        self.requests_listbox.delete(0, tk.END)
        self.responses_listbox.delete(0, tk.END)
        self.request_details_text.delete(1.0, tk.END)
        self.response_details_text.delete(1.0, tk.END)
        messagebox.showinfo("Success", "All traffic cleared")
        
    def export_traffic(self):        if not self.intercepted_requests and not self.intercepted_responses:
            messagebox.showwarning("Warning", "No traffic to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")],
            title="Export Traffic Data"
        )
        
        if filename:
            try:
                traffic_data = {
                    'requests': self.intercepted_requests,
                    'responses': self.intercepted_responses,
                    'export_time': datetime.now().isoformat(),
                    'tool': 'Cyber-T Proxy Interceptor'
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(traffic_data, f, indent=2, ensure_ascii=False)
                    
                messagebox.showinfo("Success", f"Traffic data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export traffic: {str(e)}")
        
    def create_api_tester_tab(self):
        api_frame = ttk.Frame(self.notebook)
        self.notebook.add(api_frame, text="⚡ Wolf API Tester")
        
        left_frame = ttk.Frame(api_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        list_header = ttk.Frame(left_frame)
        list_header.pack(fill='x', pady=(0, 5))
        
        ttk.Label(list_header, text="API Tests", font=('Arial', 14, 'bold')).pack(side='left')
        
        refresh_btn = ttk.Button(list_header, text="🔄 Refresh", 
                                command=self.load_api_tests)
        refresh_btn.pack(side='right')
        
        self.api_listbox = tk.Listbox(left_frame, bg='#2D2D2D', fg='#FFFFFF',
                                     selectbackground='#3D3D3D', font=('Arial', 10))
        self.api_listbox.pack(fill='both', expand=True)
        self.api_listbox.bind('<<ListboxSelect>>', self.on_api_test_select)
        
        right_frame = ttk.Frame(api_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        test_frame = ttk.LabelFrame(right_frame, text="API Test Configuration")
        test_frame.pack(fill='both', expand=True)
        
        ttk.Label(test_frame, text="Test Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.test_name_entry = ttk.Entry(test_frame, width=50)
        self.test_name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        ttk.Label(test_frame, text="Method:").grid(row=1, column=0, sticky='w', pady=5)
        self.method_var = tk.StringVar(value="GET")
        method_combo = ttk.Combobox(test_frame, textvariable=self.method_var,
                                   values=["GET", "POST", "PUT", "DELETE", "PATCH"])
        method_combo.grid(row=1, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        ttk.Label(test_frame, text="URL:").grid(row=2, column=0, sticky='w', pady=5)
        self.url_entry = ttk.Entry(test_frame, width=50)
        self.url_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        ttk.Label(test_frame, text="Headers (JSON):").grid(row=3, column=0, sticky='nw', pady=5)
        self.headers_text = tk.Text(test_frame, height=4, width=50, 
                                   bg='#2D2D2D', fg='#FFFFFF')
        self.headers_text.grid(row=3, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        ttk.Label(test_frame, text="Body:").grid(row=4, column=0, sticky='nw', pady=5)
        self.body_text = tk.Text(test_frame, height=6, width=50, 
                                bg='#2D2D2D', fg='#FFFFFF')
        self.body_text.grid(row=4, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        ttk.Label(test_frame, text="Expected Status:").grid(row=5, column=0, sticky='w', pady=5)
        self.expected_status_entry = ttk.Entry(test_frame, width=50)
        self.expected_status_entry.grid(row=5, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        button_frame = ttk.Frame(test_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="💾 Save", command=self.save_api_test).pack(side='left', padx=5)
        ttk.Button(button_frame, text="➕ New", command=self.new_api_test).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🚀 Run Test", command=self.run_api_test).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_api_test).pack(side='left', padx=5)
        
        response_frame = ttk.LabelFrame(right_frame, text="Response")
        response_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        self.response_text = tk.Text(response_frame, height=10, width=50, 
                                    bg='#2D2D2D', fg='#FFFFFF')
        self.response_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        test_frame.columnconfigure(1, weight=1)
        
    def create_security_scanner_tab(self):
        scanner_frame = ttk.Frame(self.notebook)
        self.notebook.add(scanner_frame, text="🔍 Security Scanner")
        
        config_frame = ttk.LabelFrame(scanner_frame, text="Scan Configuration")
        config_frame.pack(fill='x', padx=10, pady=5)
        
        url_frame = ttk.Frame(config_frame)
        url_frame.pack(fill='x', pady=5)
        
        ttk.Label(url_frame, text="Target URL:").pack(side='left', padx=(0, 5))
        self.scan_url_entry = ttk.Entry(url_frame, width=60)
        self.scan_url_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.scan_url_entry.insert(0, "https://example.com")
        
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill='x', pady=5)
        
        ttk.Label(options_frame, text="Threads:").pack(side='left', padx=(0, 5))
        self.thread_count_var = tk.StringVar(value="10")
        thread_spinbox = ttk.Spinbox(options_frame, from_=1, to=50, width=5, 
                                    textvariable=self.thread_count_var)
        thread_spinbox.pack(side='left', padx=(0, 20))
        
        ttk.Label(options_frame, text="Timeout (s):").pack(side='left', padx=(0, 5))
        self.timeout_var = tk.StringVar(value="5")
        timeout_spinbox = ttk.Spinbox(options_frame, from_=1, to=30, width=5, 
                                     textvariable=self.timeout_var)
        timeout_spinbox.pack(side='left', padx=(0, 20))
        
        scan_types_frame = ttk.Frame(config_frame)
        scan_types_frame.pack(fill='x', pady=5)
        
        self.directory_scan_var = tk.BooleanVar(value=True)
        self.method_scan_var = tk.BooleanVar(value=True)
        self.status_scan_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(scan_types_frame, text="Directory Enumeration", 
                       variable=self.directory_scan_var).pack(side='left', padx=(0, 20))
        ttk.Checkbutton(scan_types_frame, text="HTTP Method Testing", 
                       variable=self.method_scan_var).pack(side='left', padx=(0, 20))
        ttk.Checkbutton(scan_types_frame, text="Status Code Analysis", 
                       variable=self.status_scan_var).pack(side='left')
        
        control_frame = ttk.Frame(config_frame)
        control_frame.pack(fill='x', pady=10)
        
        self.start_scan_btn = ttk.Button(control_frame, text="🚀 Start Scan", 
                                        command=self.start_security_scan)
        self.start_scan_btn.pack(side='left', padx=(0, 10))
        
        self.stop_scan_btn = ttk.Button(control_frame, text="⏹️ Stop Scan", 
                                       command=self.stop_security_scan, state='disabled')
        self.stop_scan_btn.pack(side='left', padx=(0, 10))
        
        ttk.Button(control_frame, text="📄 Export PDF", 
                  command=self.export_scan_results_pdf).pack(side='left', padx=(0, 10))
        
        ttk.Button(control_frame, text="🗑️ Clear Results", 
                  command=self.clear_scan_results).pack(side='left')
        
        self.scan_progress = ttk.Progressbar(config_frame, mode='indeterminate')
        self.scan_progress.pack(fill='x', pady=5)
        
        results_frame = ttk.LabelFrame(scanner_frame, text="Scan Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('Type', 'URL', 'Status', 'Size', 'Response Time', 'Details')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        self.results_tree.heading('Type', text='Type')
        self.results_tree.heading('URL', text='URL')
        self.results_tree.heading('Status', text='Status')
        self.results_tree.heading('Size', text='Size')
        self.results_tree.heading('Response Time', text='Response Time')
        self.results_tree.heading('Details', text='Details')
        
        self.results_tree.column('Type', width=100)
        self.results_tree.column('URL', width=300)
        self.results_tree.column('Status', width=80)
        self.results_tree.column('Size', width=80)
        self.results_tree.column('Response Time', width=100)
        self.results_tree.column('Details', width=200)
        
        v_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        self.scan_status_label = ttk.Label(scanner_frame, text="Ready to scan", 
                                          font=('Arial', 10, 'bold'))
        self.scan_status_label.pack(pady=5)
        
        self.init_wordlists()
        
    def init_wordlists(self):
        self.directory_wordlist = []
        self.file_extensions = []
        self.security_payloads = []
        
        try:
            with open('common.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                
                in_extensions = False
                in_security = False
                
                for line in lines:
                    if line.startswith('.'):
                        self.file_extensions.append(line)
                    elif any(payload in line for payload in ["'", '"', 'SELECT', 'UNION', 'script', 'alert']):
                        self.security_payloads.append(line)
                    else:
                        self.directory_wordlist.append(line)
                        
        except FileNotFoundError:
            self.directory_wordlist = [
                'admin', 'administrator', 'api', 'app', 'assets', 'backup', 'bin', 'config',
                'css', 'data', 'db', 'dev', 'docs', 'download', 'files', 'images', 'img',
                'inc', 'include', 'js', 'lib', 'logs', 'media', 'old', 'php', 'private',
                'public', 'scripts', 'src', 'static', 'temp', 'test', 'tmp', 'uploads',
                'vendor', 'web', 'www', 'xml', 'json', 'sql'
            ]
            self.file_extensions = ['.php', '.html', '.asp', '.aspx', '.jsp']
            self.security_payloads = ["'", '"', "<script>alert('XSS')</script>"]
        
        self.http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE']
        
    def start_security_scan(self):
        url = self.scan_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a target URL!")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.scan_url_entry.delete(0, tk.END)
            self.scan_url_entry.insert(0, url)
            
        self.scanning_active = True
        self.start_scan_btn.config(state='disabled')
        self.stop_scan_btn.config(state='normal')
        self.scan_progress.start()
        self.scan_status_label.config(text="🔍 Initializing security scan...")
        
        self.play_sound("start")
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        threading.Thread(target=self._run_security_scan, args=(url,), daemon=True).start()
        
    def stop_security_scan(self):
        self.scanning_active = False
        self.start_scan_btn.config(state='normal')
        self.stop_scan_btn.config(state='disabled')
        self.scan_progress.stop()
        self.scan_status_label.config(text="🛑 Scan stopped by user")
        
        self.play_sound("error")
        
    def _run_security_scan(self, base_url):
        try:
            parsed_url = urllib.parse.urlparse(base_url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            self._test_url(base_url, "Base URL")
            
            if self.directory_scan_var.get():
                self._directory_enumeration(base_domain)
                
            if self.method_scan_var.get():
                self._method_testing(base_url)
                
            if self.status_scan_var.get():
                self._status_analysis(base_url)
                
        except Exception as e:
            self.root.after(0, lambda: self.scan_status_label.config(text=f"Scan error: {str(e)}"))
        finally:
            self.root.after(0, self._scan_completed)
            
    def _test_url(self, url, test_type):
        if not self.scanning_active:
            return
            
        try:
            start_time = time.time()
            response = requests.get(url, timeout=int(self.timeout_var.get()), 
                                  allow_redirects=True, verify=False)
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)
            content_length = len(response.content)
            
            status_color = "green" if 200 <= response.status_code < 300 else \
                          "orange" if 300 <= response.status_code < 400 else "red"
            
            result = {
                'type': test_type,
                'url': url,
                'status': response.status_code,
                'size': f"{content_length} bytes",
                'response_time': f"{response_time}ms",
                'details': f"Status: {response.status_code} | Server: {response.headers.get('Server', 'Unknown')}"
            }
            
            self.root.after(0, self._add_scan_result, result)
            
            self.scan_progress_count += 1
            if self.scan_progress_count % 10 == 0:
                self.root.after(0, self._update_scan_progress)
            
        except requests.exceptions.RequestException as e:
            result = {
                'type': test_type,
                'url': url,
                'status': "ERROR",
                'size': "0 bytes",
                'response_time': "0ms",
                'details': f"Error: {str(e)}"
            }
            self.root.after(0, self._add_scan_result, result)
            
    def _directory_enumeration(self, base_domain):
        thread_count = int(self.thread_count_var.get())
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for directory in self.directory_wordlist:
                if not self.scanning_active:
                    break
                    
                test_url = f"{base_domain}/{directory}"
                future = executor.submit(self._test_url, test_url, "Directory")
                futures.append(future)
                
                extensions_to_test = ['/'] + self.file_extensions[:10]  # Limit to avoid too many requests
                for ext in extensions_to_test:
                    if not self.scanning_active:
                        break
                    test_url_ext = f"{base_domain}/{directory}{ext}"
                    future = executor.submit(self._test_url, test_url_ext, "Directory")
                    futures.append(future)
                    
            for future in as_completed(futures):
                if not self.scanning_active:
                    break
                    
    def _method_testing(self, url):
        thread_count = int(self.thread_count_var.get())
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for method in self.http_methods:
                if not self.scanning_active:
                    break
                    
                future = executor.submit(self._test_http_method, url, method)
                futures.append(future)
                
            for future in as_completed(futures):
                if not self.scanning_active:
                    break
                    
    def _test_http_method(self, url, method):
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'POST':
                response = requests.post(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'PUT':
                response = requests.put(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'PATCH':
                response = requests.patch(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'HEAD':
                response = requests.head(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'OPTIONS':
                response = requests.options(url, timeout=int(self.timeout_var.get()), verify=False)
            elif method == 'TRACE':
                response = requests.request('TRACE', url, timeout=int(self.timeout_var.get()), verify=False)
                
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            result = {
                'type': f"Method: {method}",
                'url': url,
                'status': response.status_code,
                'size': f"{len(response.content)} bytes",
                'response_time': f"{response_time}ms",
                'details': f"Method: {method} | Headers: {len(response.headers)}"
            }
            
            self.root.after(0, self._add_scan_result, result)
            
        except requests.exceptions.RequestException as e:
            result = {
                'type': f"Method: {method}",
                'url': url,
                'status': "ERROR",
                'size': "0 bytes",
                'response_time': "0ms",
                'details': f"Error: {str(e)}"
            }
            self.root.after(0, self._add_scan_result, result)
            
    def _status_analysis(self, url):
        test_cases = [
            (f"{url}/nonexistent", "404 Test"),
            (f"{url}/admin", "Admin Test"),
            (f"{url}/robots.txt", "Robots Test"),
            (f"{url}/sitemap.xml", "Sitemap Test"),
            (f"{url}/.git", "Git Test"),
            (f"{url}/.env", "Env Test"),
            (f"{url}/config.php", "Config Test"),
            (f"{url}/backup.sql", "Backup Test")
        ]
        
        for test_url, test_name in test_cases:
            if not self.scanning_active:
                break
            self._test_url(test_url, test_name)
            
    def _add_scan_result(self, result):
        if result['status'] == "ERROR":
            tags = ('error',)
        elif isinstance(result['status'], int):
            if 200 <= result['status'] < 300:
                tags = ('success',)
            elif 300 <= result['status'] < 400:
                tags = ('redirect',)
            else:
                tags = ('error',)
        else:
            tags = ('error',)
            
        item = self.results_tree.insert('', 'end', values=(
            result['type'],
            result['url'],
            result['status'],
            result['size'],
            result['response_time'],
            result['details']
        ), tags=tags)
        
        self.results_tree.tag_configure('success', background='#2D4A2D', foreground='#90EE90')
        self.results_tree.tag_configure('redirect', background='#4A4A2D', foreground='#FFFF90')
        self.results_tree.tag_configure('error', background='#4A2D2D', foreground='#FF9090')
        
        
    def _scan_completed(self):
        self.scanning_active = False
        self.start_scan_btn.config(state='normal')
        self.stop_scan_btn.config(state='disabled')
        self.scan_progress.stop()
        
        total_results = len(self.results_tree.get_children())
        success_count = 0
        for item in self.results_tree.get_children():
            tags = self.results_tree.item(item, 'tags')
            if 'success' in tags:
                success_count += 1
        
        self.scan_status_label.config(text=f"✅ Scan completed! Found {total_results} results ({success_count} successful)")
        
        
        self.update_dashboard()
        
    def clear_scan_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.scan_status_label.config(text="Results cleared")
        
    def export_scan_results_pdf(self):
        if not self.results_tree.get_children():
            messagebox.showwarning("Warning", "No scan results to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Scan Results"
        )
        
        if filename:
            try:
                self._generate_scan_pdf(filename)
                messagebox.showinfo("Success", f"Scan results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
                
    def _generate_scan_pdf(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.red,
            alignment=1  # Center alignment
        )
        
        title = Paragraph("Cyber-T Security Scan Report", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        scan_info = f"""
        <b>Scan Target:</b> {self.scan_url_entry.get()}<br/>
        <b>Scan Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Total Results:</b> {len(self.results_tree.get_children())}<br/>
        <b>Developed by:</b> S.Tamilselvan - Cyber Security Researcher
        """
        
        info_style = ParagraphStyle(
            'ScanInfo',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20
        )
        
        story.append(Paragraph(scan_info, info_style))
        story.append(Spacer(1, 12))
        
        data = [['Type', 'URL', 'Status', 'Size', 'Response Time', 'Details']]
        
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item)['values']
            data.append(values)
            
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        
        story.append(Spacer(1, 20))
        footer = Paragraph(
            f"<i>Generated by Cyber-T Advanced Security Tool<br/>"
            f"Developed by S.Tamilselvan - Cyber Security Researcher<br/>"
            f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            styles['Normal']
        )
        story.append(footer)
        
        doc.build(story)
    
    def create_source_code_analyzer_tab(self):
        analyzer_frame = ttk.Frame(self.notebook)
        self.notebook.add(analyzer_frame, text="💻 Code Analyzer")
        
        upload_frame = ttk.LabelFrame(analyzer_frame, text="📁 File Upload & Analysis")
        upload_frame.pack(fill='x', padx=10, pady=5)
        
        upload_controls = ttk.Frame(upload_frame)
        upload_controls.pack(fill='x', pady=5)
        
        ttk.Button(upload_controls, text="📂 Upload Files", 
                  command=self.upload_source_files).pack(side='left', padx=5)
        ttk.Button(upload_controls, text="📂 Upload Folder", 
                  command=self.upload_source_folder).pack(side='left', padx=5)
        ttk.Button(upload_controls, text="🗑️ Clear Files", 
                  command=self.clear_uploaded_files).pack(side='left', padx=5)
        
        options_frame = ttk.LabelFrame(upload_frame, text="🔧 Analysis Options")
        options_frame.pack(fill='x', pady=5)
        
        self.analyze_sql_injection = tk.BooleanVar(value=True)
        self.analyze_xss = tk.BooleanVar(value=True)
        self.analyze_command_injection = tk.BooleanVar(value=True)
        self.analyze_path_traversal = tk.BooleanVar(value=True)
        self.analyze_hardcoded_secrets = tk.BooleanVar(value=True)
        self.analyze_weak_crypto = tk.BooleanVar(value=True)
        self.analyze_insecure_random = tk.BooleanVar(value=True)
        self.analyze_buffer_overflow = tk.BooleanVar(value=True)
        self.analyze_memory_leak = tk.BooleanVar(value=True)
        self.analyze_deserialization = tk.BooleanVar(value=True)
        
        left_col = ttk.Frame(options_frame)
        left_col.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Checkbutton(left_col, text="SQL Injection", 
                       variable=self.analyze_sql_injection).pack(anchor='w')
        ttk.Checkbutton(left_col, text="XSS (Cross-Site Scripting)", 
                       variable=self.analyze_xss).pack(anchor='w')
        ttk.Checkbutton(left_col, text="Command Injection", 
                       variable=self.analyze_command_injection).pack(anchor='w')
        ttk.Checkbutton(left_col, text="Path Traversal", 
                       variable=self.analyze_path_traversal).pack(anchor='w')
        ttk.Checkbutton(left_col, text="Hardcoded Secrets", 
                       variable=self.analyze_hardcoded_secrets).pack(anchor='w')
        
        right_col = ttk.Frame(options_frame)
        right_col.pack(side='right', fill='both', expand=True, padx=5)
        
        ttk.Checkbutton(right_col, text="Weak Cryptography", 
                       variable=self.analyze_weak_crypto).pack(anchor='w')
        ttk.Checkbutton(right_col, text="Insecure Random", 
                       variable=self.analyze_insecure_random).pack(anchor='w')
        ttk.Checkbutton(right_col, text="Buffer Overflow", 
                       variable=self.analyze_buffer_overflow).pack(anchor='w')
        ttk.Checkbutton(right_col, text="Memory Leaks", 
                       variable=self.analyze_memory_leak).pack(anchor='w')
        ttk.Checkbutton(right_col, text="Insecure Deserialization", 
                       variable=self.analyze_deserialization).pack(anchor='w')
        
        controls_frame = ttk.Frame(upload_frame)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="🚀 Start Analysis", 
                  command=self.start_code_analysis).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="⏹️ Stop Analysis", 
                  command=self.stop_code_analysis).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="📊 Export Report", 
                  command=self.export_analysis_report).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="🗑️ Clear Results", 
                  command=self.clear_analysis_results).pack(side='left', padx=5)
        
        self.analysis_progress = ttk.Progressbar(upload_frame, mode='indeterminate')
        self.analysis_progress.pack(fill='x', pady=5)
        
        self.analysis_status_label = ttk.Label(upload_frame, text="Ready to analyze source code")
        self.analysis_status_label.pack(pady=2)
        
        file_list_frame = ttk.LabelFrame(analyzer_frame, text="📋 Uploaded Files")
        file_list_frame.pack(fill='x', padx=10, pady=5)
        
        file_list_container = ttk.Frame(file_list_frame)
        file_list_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.uploaded_files_listbox = tk.Listbox(file_list_container, height=4)
        file_scrollbar = ttk.Scrollbar(file_list_container, orient='vertical', 
                                     command=self.uploaded_files_listbox.yview)
        self.uploaded_files_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        self.uploaded_files_listbox.pack(side='left', fill='both', expand=True)
        file_scrollbar.pack(side='right', fill='y')
        
        results_frame = ttk.LabelFrame(analyzer_frame, text="🔍 Analysis Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('File', 'Vulnerability', 'Severity', 'Line', 'Description')
        self.analysis_results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.analysis_results_tree.heading('File', text='File')
        self.analysis_results_tree.heading('Vulnerability', text='Vulnerability Type')
        self.analysis_results_tree.heading('Severity', text='Severity')
        self.analysis_results_tree.heading('Line', text='Line Number')
        self.analysis_results_tree.heading('Description', text='Description')
        
        self.analysis_results_tree.column('File', width=200)
        self.analysis_results_tree.column('Vulnerability', width=150)
        self.analysis_results_tree.column('Severity', width=100)
        self.analysis_results_tree.column('Line', width=80)
        self.analysis_results_tree.column('Description', width=300)
        
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient='vertical', 
                                       command=self.analysis_results_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient='horizontal', 
                                       command=self.analysis_results_tree.xview)
        self.analysis_results_tree.configure(yscrollcommand=tree_scrollbar_y.set,
                                           xscrollcommand=tree_scrollbar_x.set)
        
        self.analysis_results_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar_y.pack(side='right', fill='y')
        tree_scrollbar_x.pack(side='bottom', fill='x')
        
        self.analysis_results_tree.tag_configure('CRITICAL', background='#4A1A1A', foreground='#FF6B6B')
        self.analysis_results_tree.tag_configure('HIGH', background='#4A2D1A', foreground='#FFB366')
        self.analysis_results_tree.tag_configure('MEDIUM', background='#4A4A1A', foreground='#FFFF66')
        self.analysis_results_tree.tag_configure('LOW', background='#2D4A2D', foreground='#66FF66')
        
        self.analysis_active = False
    
    def upload_source_files(self):
        file_types = [
            ('All Source Files', '*.py *.js *.php *.java *.cpp *.c *.cs *.rb *.go *.rs *.ts *.jsx *.tsx'),
            ('Python Files', '*.py'),
            ('JavaScript Files', '*.js *.jsx *.ts *.tsx'),
            ('PHP Files', '*.php'),
            ('Java Files', '*.java'),
            ('C/C++ Files', '*.c *.cpp *.h *.hpp'),
            ('C# Files', '*.cs'),
            ('Ruby Files', '*.rb'),
            ('Go Files', '*.go'),
            ('Rust Files', '*.rs'),
            ('All Files', '*.*')
        ]
        
        files = filedialog.askopenfilenames(
            title="Select source code files to analyze",
            filetypes=file_types
        )
        
        if files:
            for file_path in files:
                if file_path not in self.uploaded_files:
                    self.uploaded_files.append(file_path)
                    filename = os.path.basename(file_path)
                    self.uploaded_files_listbox.insert(tk.END, f"{filename} ({file_path})")
            
            self.analysis_status_label.config(text=f"📁 {len(self.uploaded_files)} files uploaded")
            self.play_sound("start")
    
    def upload_source_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder containing source code")
        
        if folder_path:
            supported_extensions = {'.py', '.js', '.php', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.rs', '.ts', '.jsx', '.tsx', '.h', '.hpp'}
            files_added = 0
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        file_path = os.path.join(root, file)
                        if file_path not in self.uploaded_files:
                            self.uploaded_files.append(file_path)
                            relative_path = os.path.relpath(file_path, folder_path)
                            self.uploaded_files_listbox.insert(tk.END, f"{relative_path}")
                            files_added += 1
            
            if files_added > 0:
                self.analysis_status_label.config(text=f"📁 {files_added} files uploaded from folder")
                self.play_sound("start")
            else:
                self.analysis_status_label.config(text="❌ No supported source files found in folder")
                self.play_sound("error")
    
    def clear_uploaded_files(self):
        self.uploaded_files.clear()
        self.uploaded_files_listbox.delete(0, tk.END)
        self.analysis_status_label.config(text="🗑️ All files cleared")
        self.play_sound("error")
    
    def start_code_analysis(self):
        if not self.uploaded_files:
            messagebox.showerror("Error", "Please upload source code files first!")
            return
        
        # Check if any analysis options are selected
        analysis_options = [
            self.analyze_sql_injection.get(),
            self.analyze_xss.get(),
            self.analyze_command_injection.get(),
            self.analyze_path_traversal.get(),
            self.analyze_hardcoded_secrets.get(),
            self.analyze_weak_crypto.get(),
            self.analyze_insecure_random.get(),
            self.analyze_buffer_overflow.get(),
            self.analyze_memory_leak.get(),
            self.analyze_deserialization.get()
        ]
        
        if not any(analysis_options):
            messagebox.showerror("Error", "Please select at least one analysis option!")
            return
        
        self.analysis_active = True
        self.analysis_progress.start()
        self.analysis_status_label.config(text="🔍 Analyzing source code for vulnerabilities...")
        
        self.play_sound("start")
        
        for item in self.analysis_results_tree.get_children():
            self.analysis_results_tree.delete(item)
        
        threading.Thread(target=self._run_code_analysis, daemon=True).start()
    
    def stop_code_analysis(self):
        self.analysis_active = False
        self.analysis_progress.stop()
        self.analysis_status_label.config(text="🛑 Analysis stopped by user")
        self.play_sound("error")
    
    def _run_code_analysis(self):
        try:
            total_files = len(self.uploaded_files)
            processed_files = 0
            
            for file_path in self.uploaded_files:
                if not self.analysis_active:
                    break
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    vulnerabilities = self._analyze_file_content(file_path, content)
                    
                    for vuln in vulnerabilities:
                        self.root.after(0, self._add_analysis_result, vuln)
                        self.play_sound("scan_progress")
                    
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    self.root.after(0, lambda: self.analysis_status_label.config(
                        text=f"🔍 Analyzing... {processed_files}/{total_files} files ({progress:.1f}%)"
                    ))
                    
                except Exception as e:
                    print(f"Error analyzing file {file_path}: {e}")
                    continue
            
            self.root.after(0, self._analysis_completed)
            
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.root.after(0, lambda: self.analysis_status_label.config(text=error_msg))
        finally:
            self.analysis_active = False
            self.root.after(0, lambda: self.analysis_progress.stop())
    
    def _analyze_file_content(self, file_path, content):
        vulnerabilities = []
        lines = content.split('\n')
        filename = os.path.basename(file_path)
        
        analysis_options = {
            'sql_injection': self.analyze_sql_injection.get(),
            'xss': self.analyze_xss.get(),
            'command_injection': self.analyze_command_injection.get(),
            'path_traversal': self.analyze_path_traversal.get(),
            'hardcoded_secrets': self.analyze_hardcoded_secrets.get(),
            'weak_crypto': self.analyze_weak_crypto.get(),
            'insecure_random': self.analyze_insecure_random.get(),
            'buffer_overflow': self.analyze_buffer_overflow.get(),
            'memory_leak': self.analyze_memory_leak.get(),
            'insecure_deserialization': self.analyze_deserialization.get()
        }
        
        for vuln_type, vuln_data in self.vulnerability_patterns.items():
            if not analysis_options.get(vuln_type, False):
                continue
            
            patterns = vuln_data['patterns']
            severity = vuln_data['severity']
            description = vuln_data['description']
            
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    try:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append({
                                'file': filename,
                                'vulnerability': vuln_type.replace('_', ' ').title(),
                                'severity': severity,
                                'line': line_num,
                                'description': f"{description} - Line: {line.strip()}"
                            })
                            break  # Avoid duplicate matches on same line
                    except re.error:
                        continue  # Skip invalid regex patterns
        
        return vulnerabilities
    
    def _add_analysis_result(self, vulnerability):
        tags = (vulnerability['severity'],)
        item = self.analysis_results_tree.insert('', 'end', values=(
            vulnerability['file'],
            vulnerability['vulnerability'],
            vulnerability['severity'],
            vulnerability['line'],
            vulnerability['description']
        ), tags=tags)
    
    def _analysis_completed(self):
        total_vulnerabilities = len(self.analysis_results_tree.get_children())
        
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for item in self.analysis_results_tree.get_children():
            severity = self.analysis_results_tree.item(item, 'values')[2]
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        status_text = f"✅ Analysis completed! Found {total_vulnerabilities} vulnerabilities"
        if total_vulnerabilities > 0:
            status_text += f" (Critical: {severity_counts['CRITICAL']}, High: {severity_counts['HIGH']}, Medium: {severity_counts['MEDIUM']}, Low: {severity_counts['LOW']})"
        
        self.analysis_status_label.config(text=status_text)
        self.play_sound("complete")
    
    def clear_analysis_results(self):
        for item in self.analysis_results_tree.get_children():
            self.analysis_results_tree.delete(item)
        self.analysis_status_label.config(text="🗑️ Analysis results cleared")
        self.play_sound("error")
    
    def export_analysis_report(self):
        if not self.analysis_results_tree.get_children():
            messagebox.showwarning("Warning", "No analysis results to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Analysis Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if filename:
            try:
                self._generate_analysis_pdf(filename)
                messagebox.showinfo("Success", f"Analysis report saved to {filename}")
                self.play_sound("complete")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")
                self.play_sound("error")
    
    def _generate_analysis_pdf(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        title = Paragraph("Cyber-T Source Code Analysis Report", title_style)
        story.append(title)
        
        total_vulnerabilities = len(self.analysis_results_tree.get_children())
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for item in self.analysis_results_tree.get_children():
            severity = self.analysis_results_tree.item(item, 'values')[2]
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        summary_data = [
            ['Total Files Analyzed', str(len(self.uploaded_files))],
            ['Total Vulnerabilities', str(total_vulnerabilities)],
            ['Critical Vulnerabilities', str(severity_counts['CRITICAL'])],
            ['High Vulnerabilities', str(severity_counts['HIGH'])],
            ['Medium Vulnerabilities', str(severity_counts['MEDIUM'])],
            ['Low Vulnerabilities', str(severity_counts['LOW'])],
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Detailed Vulnerability Analysis", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        results_data = [['File', 'Vulnerability', 'Severity', 'Line', 'Description']]
        
        for item in self.analysis_results_tree.get_children():
            values = self.analysis_results_tree.item(item, 'values')
            results_data.append([
                values[0],  # File
                values[1],  # Vulnerability
                values[2],  # Severity
                str(values[3]),  # Line
                values[4]   # Description
            ])
        
        results_table = Table(results_data, colWidths=[120, 100, 60, 40, 250])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(results_table)
        
        story.append(Spacer(1, 30))
        footer = Paragraph(
            f"<i>Report generated by Cyber-T on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            styles['Normal']
        )
        story.append(footer)
        
        doc.build(story)
    
    def open_community_support(self):
        try:
            webbrowser.open("https://cyber-chat-tamilselvan.web.app/")
            self.play_sound("start")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open community support: {str(e)}")
            self.play_sound("error")
    
    def open_cyber_chat(self):
        try:
            webbrowser.open("https://cyber-chat-tamilselvan.web.app/")
            self.play_sound("start")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Cyber Chat: {str(e)}")
            self.play_sound("error")
    
    def create_network_analysis_tab(self):
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="🌐 Network Analysis")
        
        input_frame = ttk.LabelFrame(network_frame, text="Target Information")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        url_frame = ttk.Frame(input_frame)
        url_frame.pack(fill='x', pady=5)
        
        ttk.Label(url_frame, text="Domain/IP:").pack(side='left', padx=(0, 5))
        self.network_target_entry = ttk.Entry(url_frame, width=50)
        self.network_target_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.network_target_entry.insert(0, "google.com")
        
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill='x', pady=5)
        
        ttk.Label(options_frame, text="Timeout (s):").pack(side='left', padx=(0, 5))
        self.network_timeout_var = tk.StringVar(value="15")
        timeout_spinbox = ttk.Spinbox(options_frame, from_=5, to=60, width=5, 
                                     textvariable=self.network_timeout_var)
        timeout_spinbox.pack(side='left', padx=(0, 20))
                button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="🔍 DNS Lookup", 
                  command=self.perform_dns_lookup).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="📍 IP Geolocation", 
                  command=self.perform_ip_lookup).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="📋 WHOIS Lookup", 
                  command=self.perform_whois_lookup).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="📡 Traceroute", 
                  command=self.perform_traceroute).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="📄 Export PDF", 
                  command=self.export_network_analysis_pdf).pack(side='left', padx=(0, 5))
        
        results_frame = ttk.LabelFrame(network_frame, text="Analysis Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.network_notebook = ttk.Notebook(results_frame)
        self.network_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        dns_frame = ttk.Frame(self.network_notebook)
        self.network_notebook.add(dns_frame, text="DNS Records")
        
        self.dns_results_text = tk.Text(dns_frame, bg='#2D2D2D', fg='#FFFFFF',
                                       font=('Consolas', 10))
        dns_scrollbar = ttk.Scrollbar(dns_frame, orient='vertical', command=self.dns_results_text.yview)
        self.dns_results_text.configure(yscrollcommand=dns_scrollbar.set)
        self.dns_results_text.pack(side='left', fill='both', expand=True)
        dns_scrollbar.pack(side='right', fill='y')
        
        ip_frame = ttk.Frame(self.network_notebook)
        self.network_notebook.add(ip_frame, text="IP Analysis")
        
        self.ip_results_text = tk.Text(ip_frame, bg='#2D2D2D', fg='#FFFFFF',
                                      font=('Consolas', 10))
        ip_scrollbar = ttk.Scrollbar(ip_frame, orient='vertical', command=self.ip_results_text.yview)
        self.ip_results_text.configure(yscrollcommand=ip_scrollbar.set)
        self.ip_results_text.pack(side='left', fill='both', expand=True)
        ip_scrollbar.pack(side='right', fill='y')
        
        whois_frame = ttk.Frame(self.network_notebook)
        self.network_notebook.add(whois_frame, text="WHOIS Info")
        
        self.whois_results_text = tk.Text(whois_frame, bg='#2D2D2D', fg='#FFFFFF',
                                         font=('Consolas', 10))
        whois_scrollbar = ttk.Scrollbar(whois_frame, orient='vertical', command=self.whois_results_text.yview)
        self.whois_results_text.configure(yscrollcommand=whois_scrollbar.set)
        self.whois_results_text.pack(side='left', fill='both', expand=True)
        whois_scrollbar.pack(side='right', fill='y')
        
        traceroute_frame = ttk.Frame(self.network_notebook)
        self.network_notebook.add(traceroute_frame, text="Traceroute")
        
        self.traceroute_results_text = tk.Text(traceroute_frame, bg='#2D2D2D', fg='#FFFFFF',
                                              font=('Consolas', 10))
        traceroute_scrollbar = ttk.Scrollbar(traceroute_frame, orient='vertical', command=self.traceroute_results_text.yview)
        self.traceroute_results_text.configure(yscrollcommand=traceroute_scrollbar.set)
        self.traceroute_results_text.pack(side='left', fill='both', expand=True)
        traceroute_scrollbar.pack(side='right', fill='y')
        
    def perform_dns_lookup(self):
        target = self.network_target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a domain name!")
            return
            
        threading.Thread(target=self._dns_lookup_thread, args=(target,), daemon=True).start()
        
    def _dns_lookup_thread(self, domain):
        try:
            results = []
            results.append(f"🔍 DNS Lookup Results for: {domain}")
            results.append("=" * 50)
            results.append(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append("")
            
            if not DNS_AVAILABLE:
                results.append("❌ DNS module not available. Install with: pip install dnspython")
                self.root.after(0, self._update_dns_results, "\n".join(results))
                return
            
            # A Records
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                results.append("📋 A Records (IPv4):")
                for record in a_records:
                    results.append(f"   └─ {record}")
                results.append("")
            except Exception as e:
                results.append(f"❌ A Records: {str(e)}")
                results.append("")
            
            try:
                aaaa_records = dns.resolver.resolve(domain, 'AAAA')
                results.append("📋 AAAA Records (IPv6):")
                for record in aaaa_records:
                    results.append(f"   └─ {record}")
                results.append("")
            except Exception as e:
                results.append(f"❌ AAAA Records: {str(e)}")
                results.append("")
            
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                results.append("📧 MX Records (Mail):")
                for record in mx_records:
                    results.append(f"   └─ Priority: {record.preference}, Server: {record.exchange}")
                results.append("")
            except Exception as e:
                results.append(f"❌ MX Records: {str(e)}")
                results.append("")
            
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                results.append("🌐 NS Records (Name Servers):")
                for record in ns_records:
                    results.append(f"   └─ {record}")
                results.append("")
            except Exception as e:
                results.append(f"❌ NS Records: {str(e)}")
                results.append("")
            
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                results.append("📝 TXT Records:")
                for record in txt_records:
                    results.append(f"   └─ {record}")
                results.append("")
            except Exception as e:
                results.append(f"❌ TXT Records: {str(e)}")
                results.append("")
            
            try:
                cname_records = dns.resolver.resolve(domain, 'CNAME')
                results.append("🔗 CNAME Records:")
                for record in cname_records:
                    results.append(f"   └─ {record}")
                results.append("")
            except Exception as e:
                results.append(f"❌ CNAME Records: {str(e)}")
                results.append("")
            
            self.root.after(0, self._update_dns_results, "\n".join(results))
            
        except Exception as e:
            error_msg = f"❌ DNS Lookup Error: {str(e)}"
            self.root.after(0, self._update_dns_results, error_msg)
            
    def _update_dns_results(self, results):
        self.dns_results_text.delete(1.0, tk.END)
        self.dns_results_text.insert(1.0, results)
        self.network_notebook.select(0)  # Switch to DNS tab
        
    def perform_ip_lookup(self):
        target = self.network_target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter an IP address or domain!")
            return
            
        threading.Thread(target=self._ip_lookup_thread, args=(target,), daemon=True).start()
        
    def _ip_lookup_thread(self, target):
        try:
            results = []
            results.append(f"📍 IP Analysis for: {target}")
            results.append("=" * 50)
            results.append(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append("")
            
            # Resolve domain to IP if needed
            ip_address = target
            if not self._is_valid_ip(target):
                try:
                    ip_address = socket.gethostbyname(target)
                    results.append(f"🔍 Resolved {target} to: {ip_address}")
                    results.append("")
                except socket.gaierror:
                    results.append(f"❌ Could not resolve domain: {target}")
                    self.root.after(0, self._update_ip_results, "\n".join(results))
                    return
            
            try:
                ip_obj = ipaddress.ip_address(ip_address)
                results.append(f"📊 IP Information:")
                results.append(f"   └─ IP Address: {ip_address}")
                results.append(f"   └─ Version: IPv{ip_obj.version}")
                results.append(f"   └─ Private: {ip_obj.is_private}")
                results.append(f"   └─ Global: {ip_obj.is_global}")
                results.append(f"   └─ Multicast: {ip_obj.is_multicast}")
                results.append("")
            except Exception as e:
                results.append(f"❌ IP Analysis Error: {str(e)}")
                results.append("")
            
            results.append("🔍 Port Scan (Common Ports):")
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
            open_ports = []
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip_address, port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                        service = self._get_service_name(port)
                        results.append(f"   ✅ Port {port}/tcp - {service}")
                except:
                    pass
            
            if not open_ports:
                results.append("   ❌ No common ports found open")
            
            results.append("")
            results.append(f"📈 Summary: {len(open_ports)} open ports found")
            
            self.root.after(0, self._update_ip_results, "\n".join(results))
            
        except Exception as e:
            error_msg = f"❌ IP Lookup Error: {str(e)}"
            self.root.after(0, self._update_ip_results, error_msg)
            
    def _update_ip_results(self, results):
        self.ip_results_text.delete(1.0, tk.END)
        self.ip_results_text.insert(1.0, results)
        self.network_notebook.select(1)  # Switch to IP tab
        
    def perform_whois_lookup(self):
        target = self.network_target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a domain name!")
            return
            
        threading.Thread(target=self._whois_lookup_thread, args=(target,), daemon=True).start()
        
    def _whois_lookup_thread(self, domain):
        try:
            results = []
            results.append(f"📋 WHOIS Information for: {domain}")
            results.append("=" * 50)
            results.append(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append("")
            

            
        except Exception:
            return None
            
    def _basic_domain_lookup(self, domain):
        try:
            import socket
            
            info = []
            
            try:
                ip = socket.gethostbyname(domain)
                info.append(f"IP Address: {ip}")
            except socket.gaierror:
                info.append("IP Address: Could not resolve")
            
            try:
                import urllib.request
                urllib.request.urlopen(f"http://{domain}", timeout=5)
                info.append("HTTP: Accessible")
            except:
                info.append("HTTP: Not accessible")
            
            try:
                import urllib.request
                urllib.request.urlopen(f"https://{domain}", timeout=5)
                info.append("HTTPS: Accessible")
            except:
                info.append("HTTPS: Not accessible")
            
            return "\n".join(info) if info else None
            
        except Exception:
            return None
            
    def _update_whois_results(self, results):
        self.whois_results_text.delete(1.0, tk.END)
        self.whois_results_text.insert(1.0, "\n".join(results))
        self.network_notebook.select(2)  # Switch to WHOIS tab
        
    def perform_traceroute(self):
        target = self.network_target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a domain or IP address!")
            return
            
        threading.Thread(target=self._traceroute_thread, args=(target,), daemon=True).start()
        
    def _traceroute_thread(self, target):
        try:
            results = []
            results.append(f"📡 Traceroute to: {target}")
            results.append("=" * 50)
            results.append(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append("")
            
            import platform
            system = platform.system().lower()
            
            if system == "windows":
                cmd = ["tracert", "-h", "30", target]
            else:
                cmd = ["traceroute", "-m", "30", target]
            
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                         text=True, timeout=60)
                stdout, stderr = process.communicate()
                
                if stdout:
                    results.append("📍 Traceroute Results:")
                    results.append("-" * 30)
                    results.append(stdout)
                else:
                    results.append("❌ No traceroute output received")
                    
                if stderr:
                    results.append("\n⚠️ Errors:")
                    results.append(stderr)
                    
            except subprocess.TimeoutExpired:
                results.append("⏰ Traceroute timed out after 60 seconds")
            except FileNotFoundError:
                results.append("❌ Traceroute command not found on system")
            except Exception as e:
                results.append(f"❌ Traceroute Error: {str(e)}")
            
            self.root.after(0, self._update_traceroute_results, "\n".join(results))
            
        except Exception as e:
            error_msg = f"❌ Traceroute Error: {str(e)}"
            self.root.after(0, self._update_traceroute_results, error_msg)
            
    def _update_traceroute_results(self, results):
        self.traceroute_results_text.delete(1.0, tk.END)
        self.traceroute_results_text.insert(1.0, results)
        self.network_notebook.select(3)  # Switch to Traceroute tab
        
    def _is_valid_ip(self, ip_string):
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
            
    def _get_service_name(self, port):
        services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            993: "IMAPS", 995: "POP3S", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
        }
        return services.get(port, "Unknown")
        
    def export_network_analysis_pdf(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Network Analysis Results"
        )
        
        if filename:
            try:
                self._generate_network_analysis_pdf(filename)
                messagebox.showinfo("Success", f"Network analysis exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
                
    def _generate_network_analysis_pdf(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.red,
            alignment=1 
        )
        
        title = Paragraph("Cyber-T Network Analysis Report", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        target = self.network_target_entry.get()
        target_info = f"""
        <b>Target:</b> {target}<br/>
        <b>Analysis Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Developed by:</b> S.Tamilselvan - Cyber Security Researcher
        """
        
        info_style = ParagraphStyle(
            'TargetInfo',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20
        )
        
        story.append(Paragraph(target_info, info_style))
        story.append(Spacer(1, 12))
        
        sections = [
            ("DNS Records", self.dns_results_text),
            ("IP Analysis", self.ip_results_text),
            ("WHOIS Information", self.whois_results_text),
            ("Traceroute", self.traceroute_results_text)
        ]
        
        for section_name, text_widget in sections:
            content = text_widget.get(1.0, tk.END).strip()
            if content:
                section_style = ParagraphStyle(
                    'SectionHeader',
                    parent=styles['Heading2'],
                    fontSize=14,
                    spaceAfter=10,
                    textColor=colors.red
                )
                
                story.append(Paragraph(section_name, section_style))
                
                content_style = ParagraphStyle(
                    'SectionContent',
                    parent=styles['Normal'],
                    fontSize=9,
                    fontName='Courier',
                    spaceAfter=20
                )
                
                content = content.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(content.replace('\n', '<br/>'), content_style))
                story.append(Spacer(1, 12))
        
        footer = Paragraph(
            f"<i>Generated by Cyber-T Advanced Security Tool<br/>"
            f"Developed by S.Tamilselvan - Cyber Security Researcher<br/>"
            f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            styles['Normal']
        )
        story.append(footer)
        
        doc.build(story)
        
    def create_dashboard_tab(self):
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Statistics")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x', padx=10, pady=10)
        
        self.proxy_status_label = ttk.Label(stats_grid, text="Proxy: Stopped", 
                                           font=('Arial', 12, 'bold'))
        self.proxy_status_label.grid(row=0, column=0, padx=20, pady=5)
        
        self.intercepted_requests_label = ttk.Label(stats_grid, text="Requests: 0", 
                                                   font=('Arial', 12))
        self.intercepted_requests_label.grid(row=0, column=1, padx=20, pady=5)
        
        self.intercepted_responses_label = ttk.Label(stats_grid, text="Responses: 0", 
                                                    font=('Arial', 12))
        self.intercepted_responses_label.grid(row=0, column=2, padx=20, pady=5)
        
        self.api_tests_label = ttk.Label(stats_grid, text="API Tests: 0", 
                                        font=('Arial', 12, 'bold'))
        self.api_tests_label.grid(row=1, column=0, padx=20, pady=5)
        
        self.scan_results_label = ttk.Label(stats_grid, text="Scan Results: 0", 
                                           font=('Arial', 12, 'bold'))
        self.scan_results_label.grid(row=1, column=1, padx=20, pady=5)
        
        self.successful_scans_label = ttk.Label(stats_grid, text="Successful: 0", 
                                               font=('Arial', 12))
        self.successful_scans_label.grid(row=1, column=2, padx=20, pady=5)
        
        community_frame = ttk.LabelFrame(dashboard_frame, text="🌐 Community & Support")
        community_frame.pack(fill='x', padx=10, pady=5)
        
        community_buttons = ttk.Frame(community_frame)
        community_buttons.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(community_buttons, text="💬 Join Community Chat", 
                  command=self.open_community_support,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(community_buttons, text="🌐 Cyber Chat Platform", 
                  command=self.open_cyber_chat,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(community_buttons, text="📧 Report Issues", 
                  command=self.open_community_support,

        self.play_sound("start")
            
        threading.Thread(target=self._run_api_test_thread, args=(test,), daemon=True).start()
        
    def _run_api_test_thread(self, test):
        try:
            method = test[2]
            url = test[3]
            headers_str = test[4] or "{}"
            body = test[5] or ""
            expected_status = test[6]
            
            
            try:
                headers = json.loads(headers_str) if headers_str else {}
            except json.JSONDecodeError:
                headers = {}
                
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, data=body, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, data=body, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, data=body, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            result = {
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "headers": dict(response.headers),
                "content": response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            }
            
            self.root.after(0, self._update_response_display, result, expected_status)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE api_tests SET last_run=CURRENT_TIMESTAMP, result=? WHERE id=?
            ''', (json.dumps(result), test[0]))
            conn.commit()
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.root.after(0, self._update_response_display, error_result, None)
            
    def _update_response_display(self, result, expected_status):
        self.response_text.delete(1.0, tk.END)
        
        if "error" in result:
            self.response_text.insert(tk.END, f"❌ ERROR: {result['error']}\n")
        else:
            status_icon = "✅" if expected_status and result["status_code"] == expected_status else "⚠️"
            self.response_text.insert(tk.END, f"{status_icon} Status: {result['status_code']}\n")
            self.response_text.insert(tk.END, f"⏱️ Response Time: {result['response_time_ms']}ms\n")
            self.response_text.insert(tk.END, f"📋 Headers:\n{json.dumps(result['headers'], indent=2)}\n\n")
            self.response_text.insert(tk.END, f"📄 Content:\n{result['content']}\n")
            
    def update_dashboard(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM api_tests")
        total_api_tests = cursor.fetchone()[0]
        
        proxy_status = "Running" if self.proxy_running else "Stopped"
        intercepted_requests = len(self.intercepted_requests)
        intercepted_responses = len(self.intercepted_responses)
        
        scan_results = 0
        successful_scans = 0
        
        if hasattr(self, 'results_tree'):
            scan_results = len(self.results_tree.get_children())
            successful_scans = 0
            for item in self.results_tree.get_children():
                tags = self.results_tree.item(item, 'tags')
                if 'success' in tags:
                    successful_scans += 1
        
        self.proxy_status_label.config(text=f"Proxy: {proxy_status}")
        self.intercepted_requests_label.config(text=f"Requests: {intercepted_requests}")
        self.intercepted_responses_label.config(text=f"Responses: {intercepted_responses}")
        self.api_tests_label.config(text=f"API Tests: {total_api_tests}")
        self.scan_results_label.config(text=f"Scan Results: {scan_results}")
        self.successful_scans_label.config(text=f"Successful: {successful_scans}")
        
        self.activity_text.delete(1.0, tk.END)
        self.activity_text.insert(tk.END, f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Dashboard updated\n")
        self.activity_text.insert(tk.END, f"🔄 Proxy: {proxy_status} | Requests: {intercepted_requests} | Responses: {intercepted_responses}\n")
        self.activity_text.insert(tk.END, f"⚡ {total_api_tests} API tests configured\n")
        self.activity_text.insert(tk.END, f"🔍 {scan_results} scan results, {successful_scans} successful\n")
        self.activity_text.insert(tk.END, f"🛡️ Cyber-T Advanced Security Tool - Ready for action!\n")
        
    def run(self):
        self.root.mainloop()
        
    def __del__(self):
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all()

class ProxyServer(socketserver.ThreadingMixIn, HTTPServer):    
    allow_reuse_address = True
    
    def __init__(self, server_address, RequestHandlerClass, cyber_t_app):
        super().__init__(server_address, RequestHandlerClass)
        self.cyber_t_app = cyber_t_app

class ProxyHandler(BaseHTTPRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.cyber_t_app = server.cyber_t_app
        super().__init__(request, client_address, server)
   

if __name__ == "__main__":
    app = CyberT()
    app.run()
