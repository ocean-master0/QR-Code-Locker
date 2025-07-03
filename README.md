# 🔐 QR Code Locker

🛡️ Military-Grade Encryption • 📱 QR Code Generation • 🎨 Cyberpunk Design • 🔒 Zero Data Storage


## 🌟 **Overview**

**QR Code Locker** is a cutting-edge cyberpunk-inspired web application that transforms your sensitive messages into **encrypted QR codes**. Built with military-grade security and a stunning glassmorphism interface, it ensures your secrets remain protected without storing any data permanently.

### ✨ **Key Highlights**

| 🔐 **Security** | 🎨 **Design** | 🚀 **Privacy** | 💻 **Technology** |
|:---:|:---:|:---:|:---:|
| AES-256-GCM | Cyberpunk UI | Zero Storage | Modern Stack |
| Scrypt KDF | Glassmorphism | Auto-Cleanup | Cross-Platform |
| Authenticated | Neon Effects | Session-Based | Responsive |


## 🚀 **Features**

### 🔒 **Security Features**
- 🛡️ **AES-256-GCM Encryption** - Military-grade security
- 🔑 **Scrypt Key Derivation** - Brute-force protection
- ✅ **Authenticated Encryption** - Data integrity verification
- 🚫 **Zero Persistence** - No permanent data storage
- ⏰ **Auto-Expiry** - Temporary session management




### 🎨 **User Experience**
- 🌈 **Cyberpunk UI** - Futuristic glassmorphism design
- 📱 **Responsive Design** - Works on all devices
- ⚡ **Real-time Processing** - Instant encryption/decryption
- 🔄 **Drag & Drop** - Easy QR code uploads
- 💫 **Smooth Animations** - Engaging interactions





### 🔧 **Core Functionality**

```
graph LR
    A[📝 Message] --> B[🔐 Encrypt]
    B --> C[📊 QR Code]
    C --> D[💾 Share]
    D --> E[📤 Upload]
    E --> F[🔓 Decrypt]
    F --> G[✨ Message]
```



## 🛠️ **Tech Stack**



### **Backend Technologies**
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white)

### **Frontend Technologies**
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

### **Security Libraries**
![Cryptography](https://img.shields.io/badge/PyCryptodome-FF6B6B?style=for-the-badge&logo=lock&logoColor=white)
![QR](https://img.shields.io/badge/QRCode-4ECDC4?style=for-the-badge&logo=qr-code&logoColor=white)
![PIL](https://img.shields.io/badge/Pillow-45B7D1?style=for-the-badge&logo=image&logoColor=white)



## 📦 **Installation**

### **Prerequisites**
- 🐍 Python 3.8 or higher
- 💻 Modern web browser
- 📷 Camera (optional, for QR scanning)

### **Quick Start**

```
# 1️⃣ Clone the repository
git clone https://github.com/ocean-master0/QR-Code-Locker.git
cd qr-code-locker

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the application
python app.py

# 4️⃣ Open your browser
# Navigate to: http://localhost:5000
```

### **Dependencies**

```
# requirements.txt
Flask==2.3.3
pycryptodome==3.19.0
qrcode[pil]==7.4.2
Pillow==10.0.1
opencv-python==4.8.1.78
numpy==1.24.3
```

### 🔐 **Encryption Process**

1. **📝 Enter Message**: Type your secret message
2. **🔑 Set Password**: Choose a strong password (6+ characters)
3. **⚡ Generate QR**: Click "Generate Encrypted QR"
4. **💾 Download**: Save or share your encrypted QR code

### 🔓 **Decryption Process**

1. **📤 Upload QR**: Drag & drop or select QR image
2. **🔑 Enter Password**: Input the decryption password
3. **🔓 Decrypt**: Click "Decrypt QR Code"
4. **✨ View Message**: See your decrypted message


## 🔒 **Security Architecture**

### **Encryption Flow**

```
📝 Message → 🧂 Salt → 🔑 Scrypt → 🔐 AES-256-GCM → 📊 QR Code
```

### **Security Layers**

| Layer | Technology | Purpose |
|:---:|:---:|:---:|
| 🔐 | **AES-256-GCM** | Authenticated encryption |
| 🔑 | **Scrypt KDF** | Key derivation |
| 🧂 | **Random Salt** | Prevent rainbow tables |
| ✅ | **Auth Tags** | Data integrity |
| 🚫 | **Zero Storage** | Privacy protection |



### **🛡️ Security Features**

- **🔐 Encryption**: AES-256-GCM with authenticated encryption
- **🔑 Key Derivation**: Scrypt (N=16384, r=8, p=1) for brute-force protection
- **🧂 Salt Generation**: Cryptographically secure random salts
- **✅ Integrity**: Authentication tags prevent tampering
- **🚫 Zero Persistence**: No permanent data storage
- **⏰ Auto-Expiry**: Temporary session management
- **🧹 Auto-Cleanup**: Memory cleared on refresh/error

---

## 🎨 **UI/UX Features**



### **Design Elements**

| Feature | Description | Visual |
|:---:|:---:|:---:|
| **Glassmorphism** | Frosted glass effects | 🪟 |
| **Cyberpunk Theme** | Neon colors & effects | 🌈 |
| **Responsive** | Mobile-friendly design | 📱 |
| **Animations** | Smooth transitions | ✨ |
| **Dark Mode** | Eye-friendly interface | 🌙 |



### **🎯 User Experience**

- **⚡ Real-time**: Instant encryption/decryption
- **🔄 Drag & Drop**: Easy file uploads
- **📱 Mobile-First**: Responsive design
- **🎨 Visual Feedback**: Loading states & notifications
- **🔍 Auto-Clear**: Automatic data cleanup
- **💫 Smooth**: Buttery animations

---

## 📊 **Project Structure**

```
🔐 qr-code-locker/
├── 📄 app.py                 # Main Flask application
├── 📄 requirements.txt       # Python dependencies
├── 📁 utils/
│   ├── 📄 __init__.py
│   ├── 📄 crypto.py          # AES-256-GCM encryption
│   └── 📄 qr_handler.py      # QR code processing
├── 📁 templates/
│   ├── 📄 base.html          # Base template
│   ├── 📄 index.html         # Landing page
│   ├── 📄 encrypt.html       # Encryption interface
│   └── 📄 decrypt.html       # Decryption interface
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css      # Cyberpunk styles
│   ├── 📁 js/
│   │   └── 📄 script.js      # Frontend logic
│   └── 📁 temp/              # Temporary files (auto-cleaned)
├── 📄 README.md
└── 📄 LICENSE
```

---

## 🧪 **Testing**

### **Health Check**
```
curl http://localhost:5000/api/test-qr
```

### **Expected Response**
```
{
  "success": true,
  "original": "Test QR Code",
  "decoded": "Test QR Code",
  "match": true
}
```

---

## 📜 **License**

![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge&logo=license)

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.



### **📧 Contact Information**
- **GitHub**: [Abhishek Kumar](https://github.com/ocean-master0)
- **Issues**: [GitHub Issues](https://github.com/ocean-master0/qr-code-locker/issues)


