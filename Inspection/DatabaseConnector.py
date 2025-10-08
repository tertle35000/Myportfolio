import pyodbc

class DatabaseConnector:
    def __init__(self, server, database, username, password):
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print("เชื่อมต่อฐานข้อมูลสำเร็จ")
        except Exception as e:
            print("เชื่อมต่อฐานข้อมูลล้มเหลว:", e)

    def insert_detection(self, color, qr_data=None, bar_data=None):
        """
        บันทึก Color, QRdata, Bardata, ReadComplete และอัปเดต AccumGoodQty / AccumRejectQty
        """
        try:
            cursor = self.conn.cursor()

            # --- Step 1: อ่านค่าล่าสุด ---
            cursor.execute("""
                SELECT TOP 1 AccumGoodQty, AccumRejectQty
                FROM TT_Transaction
                ORDER BY OnDateTime DESC
            """)
            row = cursor.fetchone()
            if row:
                last_good, last_reject = row
                last_good = last_good if last_good is not None else 0
                last_reject = last_reject if last_reject is not None else 0
            else:
                last_good, last_reject = 0, 0


            # --- Step 2: คำนวณค่าใหม่ ---
            if color.lower() == "red":
                judgment = 0  # NG
                accum_good = last_good
                accum_reject = last_reject + 1
            else:
                judgment = 1  # OK
                accum_good = last_good + 1
                accum_reject = last_reject

            qr_text = ", ".join(qr_data) if qr_data else None
            bar_text = ", ".join(bar_data) if bar_data else None
            read_complete = 1

            # --- Step 3: Insert ค่าใหม่ ---
            sql = """
                INSERT INTO TT_Transaction 
                (OnDateTime, JudgmentResult, Color, QrCode, Barcode, ReadComplete, AccumGoodQty, AccumRejectQty)
                VALUES (GETDATE(), ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (judgment, color, qr_text, bar_text, read_complete, accum_good, accum_reject))
            self.conn.commit()

            print(
                f"บันทึก Color={color}, QRdata={qr_text}, Bardata={bar_text}, "
                f"Good={accum_good}, Reject={accum_reject} สำเร็จ"
            )
        except Exception as e:
            print("บันทึกข้อมูลล้มเหลว:", e)



    def close(self):
        if self.conn:
            self.conn.close()
            print("ปิดการเชื่อมต่อฐานข้อมูลแล้ว")
