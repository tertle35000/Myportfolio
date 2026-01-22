import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# Select relevant columns
columns = ['อายุ : ', 'ระยะเวลาการเสพสื่อในแต่ละครั้ง :']
df_selected = df[columns].dropna()

# จัดลำดับช่วงอายุใหม่ โดยทำให้ "ต่ำกว่า 18 ปี" มาเป็นช่วงแรก
age_order = ['ต่ำกว่า 18 ปี', '18-24 ปี', '25-34 ปี', '35-44 ปี', '45-54 ปี', '55-64 ปี']
df_selected['อายุ : '] = pd.Categorical(df_selected['อายุ : '], categories=age_order, ordered=True)

# จัดลำดับระยะเวลาการเสพสื่อจากน้อยไปหามาก
time_order = ['น้อยกว่า 30 นาที', '30 นาที - 1 ชั่วโมง', '1 - 2 ชั่วโมง', 'มากกว่า 2 ชั่วโมง']
df_selected['ระยะเวลาการเสพสื่อในแต่ละครั้ง :'] = pd.Categorical(df_selected['ระยะเวลาการเสพสื่อในแต่ละครั้ง :'], categories=time_order, ordered=True)

# Create DataFrame with count data
age_media_count = df_selected.groupby(['อายุ : ', 'ระยะเวลาการเสพสื่อในแต่ละครั้ง :']).size().unstack().fillna(0)

# กำหนดสีสำหรับแต่ละระยะเวลาเสพสื่อ
colors = ['#FFEB3B', '#FF9800', '#FF5722', '#D32F2F']  # เหลืองอ่อน, เหลืองเข้ม, ส้ม, แดง

# พล็อตกราฟแท่ง
plt.figure(figsize=(12, 6))
ax = age_media_count.plot(kind='bar', figsize=(12, 6), width=0.7, color=colors)

plt.title("ระยะเวลาการเสพสื่อตามช่วงอายุ", fontproperties=font_prop)
plt.xlabel("ช่วงอายุ", fontproperties=font_prop)
plt.ylabel("จำนวนคน", fontproperties=font_prop)
plt.legend(title="ระยะเวลาการเสพสื่อ", prop=font_prop)
plt.xticks(rotation=45, fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()
