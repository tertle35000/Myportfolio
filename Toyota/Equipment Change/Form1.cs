using System;
using System.Collections.Generic;
using System.Drawing;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Windows.Forms;

namespace Equipment_Change
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            textBox2.Text = "192.168.128.20";
        }
        
        private void textBox1_TextChanged_1(object sender, EventArgs e)
        {
            // ตรวจสอบว่ากรอกเป็นตัวเลข
            if (int.TryParse(textBox1.Text, out int startValue))
            {
                // กำหนดค่า TextBox อื่น ๆ
                textBox4.Text = (startValue + 1).ToString();
                textBox6.Text = (startValue + 2).ToString();
                textBox8.Text = (startValue + 3).ToString();
                textBox10.Text = (startValue + 4).ToString();
            }
            else
            {
                // ถ้าไม่ใช่เลข ให้ล้างค่า
                textBox4.Text = "";
                textBox6.Text = "";
                textBox8.Text = "";
                textBox10.Text = "";
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string serverIP = textBox2.Text;
            int serverPort = 5000;

            // อ่านชื่อ key จาก TextBox
            string key0 = "C" + textBox1.Text.Trim();
            string key1 = "C" + textBox4.Text.Trim();
            string key2 = "C" + textBox6.Text.Trim();
            string key3 = "C" + textBox8.Text.Trim();
            string key4 = "C" + textBox10.Text.Trim();

            // สร้าง Dictionary เพื่อเก็บข้อมูลแบบ dynamic key
            var data = new Dictionary<string, string>
            {
                { key0, button2.Text == "ON" ? "1" : "0" },
                { key1, button3.Text == "ON" ? "1" : "0" },
                { key2, button4.Text == "ON" ? "1" : "0" },
                { key3, button5.Text == "ON" ? "1" : "0" },
                { key4, button6.Text == "ON" ? "1" : "0" }
            };

            string jsonStr = JsonSerializer.Serialize(data) + "\n";

            try
            {
                using (TcpClient client = new TcpClient())
                {
                    client.Connect(serverIP, serverPort);
                    NetworkStream stream = client.GetStream();

                    byte[] bytesToSend = Encoding.UTF8.GetBytes(jsonStr);
                    stream.Write(bytesToSend, 0, bytesToSend.Length);

                    MessageBox.Show("Sender successful");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Sender failed: " + ex.Message);
            }
        }



        private void ToggleButton(Button btn)
        {
            if (btn.Text == "OFF")
            {
                btn.Text = "ON";
                btn.ForeColor = Color.LimeGreen;
            }
            else
            {
                btn.Text = "OFF";
                btn.ForeColor = Color.Red;
            }
        }

        private void button2_Click(object sender, EventArgs e) => ToggleButton(button2);
        private void button3_Click(object sender, EventArgs e) => ToggleButton(button3);
        private void button4_Click(object sender, EventArgs e) => ToggleButton(button4);
        private void button5_Click(object sender, EventArgs e) => ToggleButton(button5);
        private void button6_Click(object sender, EventArgs e) => ToggleButton(button6);
   
    
    }
}

