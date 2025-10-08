using PCLStudy;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Conveiyor
{
    public partial class Form1 : Form
    {
        // ประกาศ field ของ PLCConector
        private PLCConector plc;
        private int colorCount = 0; // นับจำนวนครั้งทั้งหมด
        private int okCount = 0;    // นับจำนวนสีอื่น (OK)
        private int ngCount = 0;    // นับจำนวนสีแดง (NG)

        public Form1()
        {
            InitializeComponent();

            // กำหนดค่าเริ่มต้นของ Label
            label6.Text = "0"; // Total
            label7.Text = "0"; // OK
            label9.Text = "0"; // NG

            // สร้าง Timer สำหรับอัปเดตสถานะปุ่มทุกวินาที
            Timer timer = new Timer();
            timer.Interval = 1000; // 1 วินาที
            timer.Tick += Timer_Tick;
            timer.Start();

            // สร้าง PLC connector และเชื่อมต่อ
            plc = new PLCConector(1);                                   // LogocalNumber และเชื่อมต่อ
            plc.Connect();

            // Subscribe event จาก PythonConnector
            Program.Connector.OnDataReceived += Connector_OnDataReceived;
        }

        // ฟังก์ชัน Tick ของ Timer
        private void Timer_Tick(object sender, EventArgs e)
        {
            UpdateButtonStateFromPLC();   // อัปเดตปุ่ม 1 (M0)
            UpdateButton2StateFromPLC();  // อัปเดตปุ่ม 2 (Y5)
        }


        private void Connector_OnDataReceived(PythonData data)
        {
            this.Invoke((MethodInvoker)delegate
            {
                if (!string.IsNullOrEmpty(data.color))
                {
                    string color = data.color;

                    // แสดงสีที่ label1
                    label1.Text = color;
                    switch (color.ToLower())
                    {
                        case "red": label1.ForeColor = Color.Red; break;
                        case "green": label1.ForeColor = Color.Green; break;
                        case "yellow": label1.ForeColor = Color.Yellow; break;
                        case "orange": label1.ForeColor = Color.Orange; break;
                        default: label1.ForeColor = Color.Black; break;
                    }

                    // นับจำนวนทั้งหมด
                    colorCount++;
                    label6.Text = colorCount.ToString();

                    // เงื่อนไข OK / NG
                    if (color.ToLower() == "red")
                    {
                        ngCount++;
                        label9.Text = ngCount.ToString();

                        // เขียนค่า 2 ไปที่ D0 เวลาเจอสีแดง
                        plc.WritePlcData("D0", 2);
                        plc.WritePlcData("M20", 1);
                    }
                    else
                    {
                        okCount++;
                        label7.Text = okCount.ToString();

                        // เขียนค่า 1 ไปที่ D0 ถ้าไม่ใช่สีแดง
                        plc.WritePlcData("D0", 1);
                        plc.WritePlcData("M20", 1);
                    }

                    // แสดง QR / Barcode
                    label11.Text = data.QRdata.Count > 0 ? string.Join(", ", data.QRdata) : "None";
                    label12.Text = data.Bardata.Count > 0 ? string.Join(", ", data.Bardata) : "None";
                }
            });
        }


        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                // toggle bit ใน PLC
                plc.ToggleBit("M0");

            }
            catch (Exception ex)
            {
                MessageBox.Show("เกิดข้อผิดพลาด: " + ex.Message);
            }
        }

        
        // ฟังก์ชันอัปเดตสถานะปุ่มตามค่าจริงจาก PLC
        private bool hasShownM0Error = false;
        private bool hasShownY5Error = false;
        private bool isOn = false ;
        private void UpdateButtonStateFromPLC()
        {
            try
            {
                int status = plc.ReadPlcstatus("M0"); // อ่านค่า bit M0

                // ถ้าอ่านสำเร็จ ให้ reset flag
                hasShownM0Error = false;

                if (status == 1)
                {
                    isOn = true;
                    button1.Text = "ON";
                    button1.ForeColor = Color.Green;
                }
                else
                {
                    isOn = false;
                    button1.Text = "OFF";
                    button1.ForeColor = Color.Red;
                }
            }
            catch (Exception ex)
            {
                isOn = false;
                button1.Text = "OFF";
                button1.ForeColor = Color.Red;

                // แสดง MessageBox แค่ครั้งแรก
                if (!hasShownM0Error)
                {
                    hasShownM0Error = true;
                    MessageBox.Show("เกิดข้อผิดพลาดในการอ่านค่า M0: " + ex.Message);
                }
            }
        }












        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void label10_Click(object sender, EventArgs e)
        {

        }

        
        
        
        
        
        
        
        private bool isY5On = false;
        private void UpdateButton2StateFromPLC()
        {
            try
            {
                int status = plc.ReadPlcstatus("Y5"); // อ่านค่า bit Y5

                hasShownY5Error = false; // ถ้าอ่านสำเร็จให้ reset flag

                if (status == 1)
                {
                    isY5On = true;
                    button2.Text = "ON";
                    button2.ForeColor = Color.Green;
                }
                else
                {
                    isY5On = false;
                    button2.Text = "OFF";
                    button2.ForeColor = Color.Red;
                }
            }
            catch (Exception ex)
            {
                isY5On = false;
                button2.Text = "OFF";
                button2.ForeColor = Color.Red;

                if (!hasShownY5Error)
                {
                    hasShownY5Error = true;
                    MessageBox.Show("เกิดข้อผิดพลาดในการอ่านค่า Y5: " + ex.Message);
                }
            }
        }


        private void button2_Click(object sender, EventArgs e)
        {
            try
            {
                // toggle bit ใน PLC
                plc.ToggleBit("M4");

            }
            catch (Exception ex)
            {
                MessageBox.Show("เกิดข้อผิดพลาด: " + ex.Message);
            }
        }
    }
}
