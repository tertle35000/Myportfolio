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
columns = ['อายุ : ', 'ระยะเวลาการเสพสื่อในแต่ละครั้ง :', 'เวลาว่างเฉลี่ยต่อวันสำหรับพักผ่อน :']
df_selected = df[columns].dropna()

# จัดลำดับช่วงอายุใหม่
age_order = ['ต่ำกว่า 18 ปี', '18-24 ปี', '25-34 ปี', '35-44 ปี', '45-54 ปี', '55-64 ปี']
df_selected['อายุ : '] = pd.Categorical(df_selected['อายุ : '], categories=age_order, ordered=True)

# จัดลำดับระยะเวลาการพักผ่อน (เวลาว่างเฉลี่ยต่อวัน) ตามลำดับที่ต้องการ
time_order = ['น้อยกว่า 1 ชั่วโมง', '1-2 ชั่วโมง', '3-4 ชั่วโมง', 'มากกว่า 4 ชั่วโมง']
df_selected['เวลาว่างเฉลี่ยต่อวันสำหรับพักผ่อน :'] = pd.Categorical(df_selected['เวลาว่างเฉลี่ยต่อวันสำหรับพักผ่อน :'], categories=time_order, ordered=True)

# Group by age and free time, then count the occurrences
age_free_time_count = df_selected.groupby(['อายุ : ', 'เวลาว่างเฉลี่ยต่อวันสำหรับพักผ่อน :']).size().unstack().fillna(0)

# Plot the bar graph
plt.figure(figsize=(12, 6))
age_free_time_count.plot(kind='bar', colormap='Greens', figsize=(12, 6), width=0.7)

plt.title("การพักผ่อนตามช่วงอายุ", fontproperties=font_prop)
plt.xlabel("ช่วงอายุ", fontproperties=font_prop)
plt.ylabel("จำนวนคน", fontproperties=font_prop)
plt.legend(title="เวลาว่างเฉลี่ยต่อวันสำหรับพักผ่อน", prop=font_prop)
plt.xticks(rotation=45, fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()
