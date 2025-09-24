# Cyber-T Security Application

## Main Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        CYBER-T APPLICATION                      │
│                    Advanced Security Tool                       │
│                    by Cyber Wolf                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION STARTUP                          │
│  • Initialize Database (SQLite with Thread Safety)             │
│  • Load Vulnerability Patterns (390+ patterns)                 │
│  • Setup Sound System (winsound)                               │
│  • Create GUI Interface (tkinter)                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MAIN INTERFACE                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Header    │  │ Community   │  │   Tabs      │             │
│  │  • Logo     │  │ Support     │  │ Navigation  │             │
│  │  • Title    │  │ • Chat      │  │             │             │
│  └─────────────┘  │ • Platform  │  └─────────────┘             │
│                   └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │    TAB SELECTION    │
                    └─────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  PROXY INTERCEPTOR │ │   API TESTER      │ │ SECURITY SCANNER  │
│                   │ │                   │ │                   │
│ 1. Configure Port │ │ 1. Create Test    │ │ 1. Enter URL      │
│ 2. Start Proxy    │ │ 2. Set Method     │ │ 2. Set Threads    │
│ 3. Capture Traffic│ │ 3. Configure URL  │ │ 3. Select Scans   │
│ 4. Analyze Data   │ │ 4. Run Test       │ │ 4. Start Scan     │
│ 5. Export Results │ │ 5. View Results   │ │ 5. View Results   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   CODE ANALYZER   │ │ NETWORK ANALYSIS  │ │    DASHBOARD      │
│                   │ │                   │ │                   │
│ 1. Upload Files   │ │ 1. DNS Lookup     │ │ 1. View Stats     │
│ 2. Select Checks  │ │ 2. IP Analysis    │ │ 2. Monitor Activity│
│ 3. Start Analysis │ │ 3. WHOIS Lookup   │ │ 3. Community Access│
│ 4. View Results   │ │ 4. Traceroute     │ │ 4. Export Reports │
│ 5. Export Report  │ │ 5. View Results   │ │                   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

---

##  Proxy Interceptor Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROXY INTERCEPTOR                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONFIGURATION PHASE                           │
│  • Set Proxy Port (default: 8080)                               │
│  • Enable/Disable Request Interception                          │
│  • Enable/Disable Response Interception                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROXY STARTUP                                │
│  • Create ProxyServer instance                                  │
│  • Start ThreadingMixIn server                                  │
│  • Bind to localhost:port                                       │
│  • Play Start Sound (1200Hz, 300ms)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TRAFFIC INTERCEPTION                           │
│  • Capture HTTP/HTTPS requests                                  │
│  • Analyze request headers and body                             │
│  • Perform vulnerability analysis                               │
│  • Color-code results (Green/Yellow/Red)                       │
│  • Store in intercepted_requests list                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RESPONSE PROCESSING                            │
│  • Forward requests to target server                            │
│  • Capture response data                                        │
│  • Analyze response headers and content                         │
│  • Perform vulnerability analysis                               │
│  • Store in intercepted_responses list                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA EXPORT                                  │
│  • Export to JSON format                                        │
│  • Generate detailed reports                                    │
│  • Save analysis results                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

##  API Tester Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       API TESTER                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TEST CREATION                                 │
│  • Enter Test Name                                              │
│  • Select HTTP Method (GET/POST/PUT/DELETE/PATCH)              │
│  • Input Target URL                                             │
│  • Configure Headers (JSON format)                             │
│  • Set Request Body (if applicable)                            │
│  • Define Expected Status Code                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATABASE STORAGE                              │
│  • Save to SQLite database                                      │
│  • Use ThreadLocalDB for thread safety                          │
│  • Store in api_tests table                                    │
│  • Update test list display                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TEST EXECUTION                               │
│  • Start execution in separate thread                           │
│  • Play Start Sound (1200Hz, 300ms)                            │
│  • Send HTTP request with configured parameters                 │
│  • Measure response time                                        │
│  • Capture response data                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RESULT ANALYSIS                               │
│  • Compare actual vs expected status code                       │
│  • Display response headers and body                            │
│  • Show response time metrics                                   │
│  • Update database with results                                 │
│  • Play Completion Sound (1500Hz + 1800Hz)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Security Scanner Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY SCANNER                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SCAN CONFIGURATION                            │
│  • Enter Target URL                                             │
│  • Set Thread Count (1-50)                                      │
│  • Configure Timeout (1-30 seconds)                            │
│  • Select Scan Types:                                           │
│    - Directory Enumeration                                      │
│    - HTTP Method Testing                                        │
│    - Status Code Analysis                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCAN INITIALIZATION                          │
│  • Validate URL format                                          │
│  • Set scanning_active = True                                   │
│  • Start progress bar                                           │
│  • Play Start Sound (1200Hz, 300ms) - TOUCH FEEDBACK           │
│  • Clear previous results                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MULTI-THREADED SCANNING                       │
│  • Create ThreadPoolExecutor                                    │
│  • Launch directory enumeration threads                         │
│  • Launch HTTP method testing threads                           │
│  • Launch status code analysis threads                          │
│  • Process results in real-time                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESULT PROCESSING                            │
│  • Color-code results by status:                                │
│    - 🟢 Green (200-299) - Success                              │
│    - 🟡 Yellow (300-399) - Redirect                            │
│    - 🔴 Red (400+) - Error                                     │
│  • Update progress counter                                      │
│  • Display results in treeview                                  │
│  • NO SOUNDS during scanning (performance optimized)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCAN COMPLETION                              │
│  • Set scanning_active = False                                  │
│  • Stop progress bar                                            │
│  • Count total results                                          │
│  • Count successful scans                                       │
│  • Update dashboard statistics                                  │
│  • NO COMPLETION SOUND (performance optimized)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION                            │
│  • Export results to PDF                                        │
│  • Generate professional reports                                │
│  • Include vulnerability analysis                               │
│  • Provide remediation recommendations                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Source Code Analyzer Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   SOURCE CODE ANALYZER                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FILE UPLOAD                                  │
│  • Upload Individual Files                                      │
│  • Upload Entire Folders                                        │
│  • Support Multiple Languages:                                  │
│    - Python (.py)                                               │
│    - JavaScript (.js, .jsx, .ts, .tsx)                         │
│    - PHP (.php)                                                 │
│    - Java (.java)                                               │
│    - C/C++ (.c, .cpp, .h, .hpp)                                │
│    - C# (.cs)                                                   │
│    - Ruby (.rb)                                                 │
│    - Go (.go)                                                   │
│    - Rust (.rs)                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ANALYSIS CONFIGURATION                          │
│  • Select Vulnerability Types:                                  │
│    - ✅ SQL Injection                                           │
│    - ✅ Cross-Site Scripting (XSS)                             │
│    - ✅ Command Injection                                       │
│    - ✅ Path Traversal                                          │
│    - ✅ Hardcoded Secrets                                       │
│    - ✅ Weak Cryptography                                       │
│    - ✅ Insecure Random                                         │
│    - ✅ Buffer Overflow                                         │
│    - ✅ Memory Leaks                                            │
│    - ✅ Insecure Deserialization                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS EXECUTION                           │
│  • Start analysis in separate thread                            │
│  • Play Start Sound (1200Hz, 300ms)                            │
│  • Process each file sequentially                               │
│  • Apply 390+ regex patterns                                    │
│  • Perform line-by-line analysis                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   VULNERABILITY DETECTION                       │
│  • Match code patterns against vulnerability signatures         │
│  • Classify by severity:                                        │
│    - 🔴 CRITICAL - Command Injection                           │
│    - 🟠 HIGH - SQL Injection, XSS, Path Traversal             │
│    - 🟡 MEDIUM - Hardcoded Secrets, Weak Crypto               │
│    - 🟢 LOW - Minor issues                                     │
│  • Play Progress Sound (800Hz, 100ms) for each finding         │
│  • Display results in real-time                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION                            │
│  • Generate PDF reports                                         │
│  • Include executive summary                                    │
│  • Provide detailed vulnerability analysis                      │
│  • Show remediation recommendations                             │
│  • Play Completion Sound (1500Hz + 1800Hz)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Network Analysis Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK ANALYSIS                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   TOOL SELECTION    │
                    └─────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│    DNS LOOKUP     │ │    IP ANALYSIS    │ │   WHOIS LOOKUP    │
│                   │ │                   │ │                   │
│ 1. Enter Domain   │ │ 1. Enter IP/Domain│ │ 1. Enter Domain   │
│ 2. Resolve DNS    │ │ 2. Analyze IP     │ │ 2. Query WHOIS    │
│ 3. Show Records   │ │ 3. Show Geoloc    │ │ 3. Show Registry  │
│ 4. Display Results│ │ 4. Display Info   │ │ 4. Display Info   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRACEROUTE                                   │
│  • Enter Target IP/Domain                                       │
│  • Trace network path                                           │
│  • Show hop-by-hop information                                  │
│  • Display latency measurements                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RESULT PROCESSING                              │
│  • Execute in separate threads                                  │
│  • Play Start Sound (1200Hz, 300ms)                            │
│  • Process network requests                                     │
│  • Format results professionally                                │
│  • Display in dedicated text areas                              │
│  • Play Completion Sound (1500Hz + 1800Hz)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Dashboard Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       DASHBOARD                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STATISTICS DISPLAY                            │
│  • Proxy Status (Running/Stopped)                               │
│  • Intercepted Requests Count                                   │
│  • API Tests Count                                              │
│  • Scan Results Count                                           │
│  • Successful Scans Count                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 COMMUNITY SUPPORT SECTION                       │
│  • 💬 Join Community Chat                                       │
│  • 🌐 Cyber Chat Platform                                       │
│  • 📧 Report Issues                                             │
│  • Direct link to https://cyber-chat-tamilselvan.web.app/      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ACTIVITY LOG                                  │
│  • Real-time activity monitoring                                │
│  • System event logging                                         │
│  • User action tracking                                         │
│  • Error and warning notifications                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sound System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      SOUND SYSTEM                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SOUND TRIGGERS                                │
│  • User Actions (Button Clicks)                                 │
│  • Process Start/Stop Events                                    │
│  • Completion Notifications                                     │
│  • Error Conditions                                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SOUND TYPES                                   │
│  • Start Sound (1200Hz, 300ms) - High frequency, longer        │
│  • Completion Sound (1500Hz + 1800Hz) - Success sequence       │
│  • Error Sound (500Hz, 500ms) - Low frequency, longer          │
│  • Progress Sound (800Hz, 100ms) - Medium frequency, short     │
│  • Success Sound (1000Hz, 150ms) - High frequency, medium      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SOUND THROTTLING                              │
│  • 100ms minimum interval between sounds                        │
│  • Important sounds (start/complete) not throttled             │
│  • Performance optimized for minimal CPU impact                 │
│  • Graceful fallback if sound system fails                      │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Database Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE SYSTEM                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 THREAD-LOCAL CONNECTIONS                        │
│  • ThreadLocalDB class manages connections                      │
│  • Each thread gets its own SQLite connection                   │
│  • check_same_thread=False for thread safety                   │
│  • Automatic connection cleanup                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE TABLES                              │
│  • api_tests table - API test configurations                   │
│  • tickets table - Ticket management system                     │
│  • Automatic schema creation on first run                      │
│  • Data persistence across sessions                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OPERATIONS                                    │
│  • CREATE - Insert new records                                  │
│  • READ - Query existing data                                   │
│  • UPDATE - Modify existing records                             │
│  • DELETE - Remove records                                      │
│  • All operations use thread-local connections                  │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Community Support Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   COMMUNITY SUPPORT                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ACCESS POINTS                                 │
│  • Header Community Support Button                              │
│  • Header Cyber Chat Button                                     │
│  • Dashboard Community Section                                  │
│  • Multiple support channels                                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEB BROWSER INTEGRATION                      │
│  • Use webbrowser module to open URLs                           │
│  • Open https://cyber-chat-tamilselvan.web.app/                │
│  • Play Start Sound (1200Hz, 300ms) on success                 │
│  • Play Error Sound (500Hz, 500ms) on failure                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SUPPORT FEATURES                              │
│  • Real-time community chat                                     │
│  • Feature request submissions                                  │
│  • Bug report system                                            │
│  • Security update notifications                                │
│  • Developer collaboration                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ERROR DETECTION                               │
│  • Try-except blocks in all operations                          │
│  • Network connectivity checks                                  │
│  • File system permission validation                            │
│  • Database connection verification                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ERROR RESPONSE                                │
│  • Display user-friendly error messages                         │
│  • Play Error Sound (500Hz, 500ms)                             │
│  • Log detailed error information                               │
│  • Provide recovery suggestions                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ERROR RECOVERY                                │
│  • Graceful degradation of features                             │
│  • Automatic retry mechanisms                                   │
│  • Fallback to alternative methods                              │
│  • User notification of partial functionality                   │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Performance Optimization Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                PERFORMANCE OPTIMIZATION                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SCANNING OPTIMIZATION                         │
│  • Multi-threaded processing with ThreadPoolExecutor           │
│  • Configurable thread count (1-50)                            │
│  • Removed continuous sounds during scanning                    │
│  • Only touch feedback sounds (start/stop)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MEMORY OPTIMIZATION                           │
│  • Thread-local database connections                            │
│  • Efficient data structures                                    │
│  • Automatic garbage collection                                 │
│  • Resource cleanup on exit                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   UI OPTIMIZATION                               │
│  • Non-blocking UI operations                                   │
│  • Progress indicators for long operations                      │
│  • Responsive interface design                                  │
│  • Efficient widget updates                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Application Exit Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION EXIT                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLEANUP OPERATIONS                            │
│  • Stop all running threads                                     │
│  • Close database connections                                   │
│  • Save application state                                       │
│  • Cleanup temporary files                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RESOURCE RELEASE                              │
│  • Release system resources                                     │
│  • Close file handles                                           │
│  • Terminate network connections                                │
│  • Destroy GUI components                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GRACEFUL EXIT                               │
│  • Exit application cleanly                                     │
│  • Return control to operating system                           │
│  • Ensure no resource leaks                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA FLOW OVERVIEW                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT SOURCES                                │
│  • User Interface (GUI)                                         │
│  • File Uploads (Source Code)                                   │
│  • Network Traffic (Proxy)                                      │
│  • Configuration Files                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING ENGINES                            │
│  • Vulnerability Pattern Matching                               │
│  • Network Analysis Tools                                       │
│  • Code Analysis Algorithms                                     │
│  • Traffic Interception Logic                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT FORMATS                               │
│  • Real-time GUI Updates                                        │
│  • PDF Reports                                                  │
│  • JSON Exports                                                 │
│  • Database Storage                                             │
└─────────────────────────────────────────────────────────────────┘
```

---
