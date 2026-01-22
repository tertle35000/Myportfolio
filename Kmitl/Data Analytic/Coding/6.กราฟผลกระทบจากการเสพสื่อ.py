import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "C:/Windows/Fonts/THSarabun.ttf"  # ใช้ฟอนต์ที่เจอจากคำสั่งก่อนหน้า
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = font_prop.get_name()

# Set Sheet ID and Sheet Name
sheet_id = "1YX3HKrvKoYYQeSielEAUXf0DWAPm_by-BJP2lBpxpys"
sheet_name = "Dataproject"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Load data into Pandas
df = pd.read_csv(url)

# สมมติว่า 'ความรู้สึกและผลกระทบจากการเสพสื่อ' คือคอลัมน์ที่เก็บข้อมูลคำตอบ
# แยกคำตอบที่เลือกโดยใช้ comma (ถ้ามีหลายตัวเลือก)
df['ความรู้สึกและผลกระทบจากการเสพสื่อ'] = df['ความรู้สึกและผลกระทบจากการเสพสื่อ'].fillna('')

# สร้างรายการของคำตอบทั้งหมดที่เลือก
all_feelings = []
for feelings in df['ความรู้สึกและผลกระทบจากการเสพสื่อ']:
    # ลบช่องว่างก่อนและหลังคำและใช้ set เพื่อกรองคำซ้ำ
    unique_feelings = set(f.strip() for f in feelings.split(','))
    all_feelings.extend(unique_feelings)

# นับจำนวนของแต่ละคำตอบ
feeling_counts = pd.Series(all_feelings).value_counts()

# พล็อตกราฟแท่ง
plt.figure(figsize=(10, 6))
feeling_counts.plot(kind='bar', color='skyblue')

# เพิ่มรายละเอียดกราฟ
plt.title("ความรู้สึกจากการเสพสื่อ", fontproperties=font_prop)
plt.xlabel("ความรู้สึก", fontproperties=font_prop)
plt.ylabel("จำนวนคน", fontproperties=font_prop)
plt.xticks(rotation=45, ha='right', fontproperties=font_prop)

# แสดงกราฟ
plt.tight_layout()
plt.show()
