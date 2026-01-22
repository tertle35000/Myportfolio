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
columns = ['อายุ : ', 'ประเภทของสื่อที่มักเลือกเสพในเวลาพักผ่อน :']
df_selected = df[columns].dropna()

# จัดลำดับช่วงอายุใหม่
age_order = ['ต่ำกว่า 18 ปี', '18-24 ปี', '25-34 ปี', '35-44 ปี', '45-54 ปี', '55-64 ปี']
df_selected['อายุ : '] = pd.Categorical(df_selected['อายุ : '], categories=age_order, ordered=True)

# แยกประเภทสื่อที่เลือกเป็นคอลัมน์บูลีน
media_types = ['โซเชียลมีเดีย', 'ดูหนัง/ซีรีส์', 'ฟังเพลง/พอดแคสต์', 'อ่านหนังสือ/นิยาย/บทความออนไลน์/หนังสือพิมพ์', 'เล่นเกม']
for media in media_types:
    df_selected[media] = df_selected['ประเภทของสื่อที่มักเลือกเสพในเวลาพักผ่อน :'].apply(lambda x: 1 if media in x else 0)

# Group by age and media type selection, then count the occurrences
age_media_count = df_selected.groupby(['อายุ : '])[media_types].sum()

# Plot the bar graph for media preferences by age group
plt.figure(figsize=(12, 6))
age_media_count.plot(kind='bar', figsize=(12, 6), width=0.8, colormap='viridis')

plt.title("ประเภทของสื่อที่มักเลือกเสพในเวลาพักผ่อนตามช่วงอายุ", fontproperties=font_prop)
plt.xlabel("ช่วงอายุ", fontproperties=font_prop)
plt.ylabel("จำนวนคนที่เลือก", fontproperties=font_prop)
plt.legend(title="ประเภทของสื่อ", prop=font_prop)
plt.xticks(rotation=45, fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()
