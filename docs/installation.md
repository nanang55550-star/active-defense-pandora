# 📦 Instalasi Active Defense Pandora

## Persyaratan Sistem

### Minimum Requirements
- Python 3.8 atau lebih baru
- 2GB RAM
- 500MB storage
- Termux (Android) atau Linux/Unix

### Recommended
- Python 3.10+
- 4GB RAM
- 1GB storage
- Koneksi internet untuk broadcast

---

## 🚀 Instalasi di Termux (Android)

```bash
# 1. Update Termux
pkg update && pkg upgrade -y

# 2. Install dependencies
pkg install python git libpcap -y

# 3. Clone repository
git clone https://github.com/nanang55550-star/active-defense-pandora.git
cd active-defense-pandora

# 4. Install Python packages
pip install -r requirements.txt

# 5. Jalankan
python core/pandora_engine.py

```
## 🐧 Instalasi di Linux/Ubuntu

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python dan pip
sudo apt install python3 python3-pip git -y

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Clone repository
git clone https://github.com/nanang55550-star/active-defense-pandora.git
cd active-defense-pandora

# 5. Jalankan
python3 core/pandora_engine.py

```
## 🐳 Instalasi dengan Docker

```bash

FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "core/pandora_engine.py"]

# Build image
docker build -t pandora .

# Run container
docker run -d --name pandora --network host pandora
