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
