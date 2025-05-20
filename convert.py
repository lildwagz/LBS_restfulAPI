import bcrypt
import re

# Data pengguna dari database
data = """
('admin', 'admin', 'admin'),
('sutrisnobachir', 'B4chir!X', 'admin'),
('khofifahindar', 'Kh0f!f4h#', 'admin'),
('ekatjandranegara', '3k4Tjan!', 'admin'),
('tgbaguseko', 'TgB4g5$', 'admin'),
('radityadika', 'radityadika', 'user'),
('ajibasuki', 'ajibasuki', 'user'),
('titisjuman', 'titisjuman', 'user'),
('rinisuryono', 'rinisuryono', 'user'),
('aldojonathan', 'aldojonathan', 'user'),
('susipudjiastuti', 'susipudjiastuti', 'user'),
('ekakurniawan', 'ekakurniawan', 'user'),
('lukmanhakim', 'lukmanhakim', 'user'),
('nurhayatisubary', 'nurhayatisubary', 'user'),
('davidjulius', 'davidjulius', 'user'),
('fitriaanggraini', 'fitriaanggraini', 'user'),
('antonioblanco', 'Bl4nc0Ant', 'user'),
('srimulyani', 'Muly4n1', 'user'),
('bambangpamungkas', 'B4mb4ngP', 'user'),
('ratnasarumpaet', 'R4tn4S', 'user'),
('arifinputra', 'Putr4Ar1f', 'user'),
('melatisuryodarmo', 'M3lat1D', 'user'),
('jokowidodo', 'W1d0d0Jk', 'user'),
('sandradewi', 'D3w1S4n', 'user'),
('hendrasetiawan', 'H3ndr4S', 'user'),
('laksmipamuntjak', 'L4ksm1P', 'user'),
('ajisantoso', 'S4nt0s0Aj', 'user'),
('rinanose', 'N0s3R1n', 'user'),
('tulussimatupang', 'Tuluss1m4', 'user'),
('prillylatuconsina', 'Pr1llyLC', 'user'),
('rezarahadian', 'R4h4d14nRz', 'user'),
('dianpelangi', 'P3l4ng1D', 'user'),
('ariobayu', 'B4yuAr1o', 'user'),
('najwashihab', 'Sh1h4bN', 'user'),
('joetaslim', 'T4sl1mJ0', 'user'),
('maudyayunda', '4yund4Mau', 'user'),
('riodewanto', 'D3w4nt0R', 'user'),
('vaneshaprescilla', 'Pr3sc1ll4', 'user'),
('iwanfals', 'F4ls1wan', 'user'),
('rossasinaga', 'S1n4g4Ros', 'user'),
('tretanmuslim', 'Musl1mTr3t', 'user'),
('citrascholastika', 'Sch0l4sT', 'user'),
('judikanababan', 'N4b4b4nJ', 'user'),
('agnesmonica', 'M0n1c4Ag', 'user'),
('armandmaulana', 'M4ul4n4Ar', 'user'),
('gitagutawa', 'Gut4w4G', 'user'),
('andretaulany', 'T4ul4nyAn', 'user'),
('rinirosdiana', 'R0sd1ana', 'user'),
('destamahendra', 'M4h3ndr4D', 'user'),
('sulenugroho', 'Nugr0h0S', 'user'),
('nurularifin', '4r1f1nNur', 'user'),
('ridwankamil', 'K4m1lR1d', 'user'),
('sherinamunaf', 'Mun4fSh3', 'user');
"""

# Ekstrak username dan password menggunakan regex
pattern = r"\('([^']+)',\s*'([^']+)',\s*'[^']+'\),"
matches = re.findall(pattern, data)

print("-- Update password untuk admin")
for username, password in matches[:5]:  # 5 user pertama adalah admin
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    print(f"UPDATE users SET password = '{hashed}' WHERE username = '{username}';")

print("\n-- Update password untuk user biasa")
for username, password in matches[5:]:  # Sisanya adalah user biasa
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    print(f"UPDATE users SET password = '{hashed}' WHERE username = '{username}';")