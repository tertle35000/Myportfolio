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
columns = ['อายุ : ', 'ช่วงเวลาที่มักเสพสื่อมากที่สุด :']
df_selected = df[columns].dropna()

# จัดลำดับช่วงอายุใหม่
age_order = ['ต่ำกว่า 18 ปี', '18-24 ปี', '25-34 ปี', '35-44 ปี', '45-54 ปี', '55-64 ปี']
df_selected['อายุ : '] = pd.Categorical(df_selected['อายุ : '], categories=age_order, ordered=True)

# จัดลำดับช่วงเวลาที่มักเสพสื่อมากที่สุด ตามลำดับที่ต้องการ
time_order = ['เช้า (06:00 - 09:00)', 'สาย (9.00-11.00)', 'กลางวัน (11:00 - 12:00)' ,
              'บ่าย (12:00 - 16:00)', 'เย็น (16:00 - 18:00)', 'ค่ำ (18.00 - 20.00)', 
              'ดึก (20.00 - 00.00)', 'ดึกหลังเที่ยงคืน (00.00 - 06.00)']
df_selected['ช่วงเวลาที่มักเสพสื่อมากที่สุด :'] = pd.Categorical(df_selected['ช่วงเวลาที่มักเสพสื่อมากที่สุด :'], categories=time_order, ordered=True)

# Group by age and most frequent media time, then count the occurrences
age_media_time_count = df_selected.groupby(['อายุ : ', 'ช่วงเวลาที่มักเสพสื่อมากที่สุด :']).size().unstack().fillna(0)

# Plot the bar graph with a blue to purple colormap
plt.figure(figsize=(12, 6))
age_media_time_count.plot(kind='bar', colormap='cool', figsize=(12, 6), width=0.7)

plt.title("ช่วงเวลาที่มักเสพสื่อตามช่วงอายุ", fontproperties=font_prop)
plt.xlabel("ช่วงอายุ", fontproperties=font_prop)
plt.ylabel("จำนวนคน", fontproperties=font_prop)
plt.legend(title="ช่วงเวลาที่มักเสพสื่อมากที่สุด", prop=font_prop)
plt.xticks(rotation=45, fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()
