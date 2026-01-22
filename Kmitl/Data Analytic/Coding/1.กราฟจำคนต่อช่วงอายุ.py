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
columns = ['อายุ : ']
df_selected = df[columns].dropna()

# จัดลำดับช่วงอายุใหม่
age_order = ['ต่ำกว่า 18 ปี', '18-24 ปี', '25-34 ปี', '35-44 ปี', '45-54 ปี', '55-64 ปี', '65 ปีขึ้นไป']
df_selected['อายุ : '] = pd.Categorical(df_selected['อายุ : '], categories=age_order, ordered=True)

# คำนวณจำนวนคนในแต่ละช่วงอายุ
age_count = df_selected['อายุ : '].value_counts().sort_index()

# Plot the pie chart for the number of people in each age group
plt.figure(figsize=(8, 8))

# ใช้ colors และ explode เพื่อให้กราฟดูน่าสนใจ
colors = sns.color_palette("pastel", len(age_count))
explode = (0.1, 0, 0, 0, 0, 0, 0)  # ขยับส่วนแรกออกมา

plt.pie(age_count, labels=age_count.index, autopct='%1.1f%%', startangle=90, colors=colors, explode=explode, 
        shadow=True, wedgeprops={'edgecolor': 'black', 'linewidth': 2})

plt.title("การกระจายของจำนวนคนในแต่ละช่วงอายุ", fontproperties=font_prop, fontsize=14, weight='bold')

# เพิ่มแถบสีด้านนอกเพื่อให้กราฟดูชัดเจนขึ้น
plt.gca().set_aspect('equal')  # ทำให้วงกลมไม่บิดเบี้ยว

# เพิ่มสไตล์ในกราฟ เช่น ขอบด้านนอกของกราฟ
plt.grid(False)  # ปิดกริด

# Show the plot
plt.show()
