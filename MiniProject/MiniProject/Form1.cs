using ActUtlTypeLib;
using PCLStudy;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.SqlClient;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace MiniProject
{
    public partial class Form1 : Form
    {
        private string connectionString = "Server=localhost\\SQLEXPRESS;Database=MyDatabase;Trusted_Connection=True;";
        private DatabaseConnector db;
        public Form1()
        {
            InitializeComponent();
            db = new DatabaseConnector(connectionString); // ใช้ตัวแปรระดับคลาส
        }


        private PLCConector plc;
        int logicalNo;
  

        private void Form1_Load(object sender, EventArgs e)
        {

            // เพิ่มรายการใหม่
            comboBox1.Items.Add("Please Select Type");
            comboBox1.Items.Add("short");
            comboBox1.Items.Add("bit");
            comboBox1.Items.Add("text");
            comboBox1.Items.Add("float");

            // เลือกรายการเริ่มต้นเป็น "Please Select Type"
            comboBox1.SelectedIndex = 0;

            // ตั้งค่า DateTimePicker ให้แสดงทั้งวันที่และเวลา
            dateTimePicker1.Format = DateTimePickerFormat.Custom;
            dateTimePicker1.CustomFormat = "dd/MM/yyyy HH:mm:ss";

            // ตั้งค่าให้แสดงเวลาปัจจุบัน
            dateTimePicker1.Value = DateTime.Now;

            // เริ่ม Timer
            timer1.Interval = 1000;
            timer1.Start();

            try
            {
                logicalNo = Convert.ToInt32(File.ReadAllText("ConfigNo/LogicalNo.txt"));
                lb_StatusLogical.Text = "Logical Sucess";
                lb_StatusLogical.ForeColor = Color.Green;
            }
            catch
            {
                lb_StatusLogical.Text = "Logical is Not Set";
                lb_StatusLogical.ForeColor = Color.Red;
            }
      
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            // อัปเดตเวลาใน DateTimePicker ทุกวินาที
            dateTimePicker1.Value = DateTime.Now;
            
        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            // ตรวจสอบว่าผู้ใช้เลือก "text" หรือไม่
            if (comboBox1.SelectedItem != null && comboBox1.SelectedItem.ToString() == "text")
            {
                textBox_Length.ReadOnly = false;         // เปิดให้กรอก
                textBox_Length.BackColor = Color.White;  // สีพื้นหลังปกติ
            }
            else
            {
                textBox_Length.ReadOnly = true;          // ปิดการกรอก
                textBox_Length.BackColor = Color.LightGray;  // ช่องสีเทา
            }
        }


        private void btn_ReadPLC_Click(object sender, EventArgs e)
        {
            Form2 form2 = new Form2(connectionString); // ส่ง connectionString ไป
            form2.Show();
        }


        private bool ValidateInput()
        {
            // ตรวจสอบ Item Number ต้องไม่ว่าง และต้องเป็นตัวเลข
            if (string.IsNullOrWhiteSpace(textBox1.Text) || !Regex.IsMatch(textBox1.Text, @"^\d+$"))
            {
                MessageBox.Show("กรุณากรอก Item Number ให้ถูกต้อง (ต้องเป็นตัวเลขเท่านั้น)");
                textBox1.Focus();
                return false;
            }

            // ตรวจสอบ Parameter ห้ามว่าง
            if (string.IsNullOrWhiteSpace(textBox2.Text))
            {
                MessageBox.Show("กรุณากรอก Parameter");
                textBox2.Focus();
                return false;
            }

            // ตรวจสอบ Address ห้ามว่าง
            if (string.IsNullOrWhiteSpace(textBox3.Text))
            {
                MessageBox.Show("กรุณากรอก Address");
                textBox3.Focus();
                return false;
            }

            // ตรวจสอบ Length ต้องเป็นตัวเลข และไม่ว่าง (อาจต้องการให้ใส่จำนวน bit/word ที่ต้องอ่าน)
            //if (string.IsNullOrWhiteSpace(textBox_Length.Text) || !Regex.IsMatch(textBox_Length.Text, @"^\d+$"))
            //{
            //    MessageBox.Show("กรุณากรอก Length ให้ถูกต้อง (ต้องเป็นตัวเลขเท่านั้น)");
            //    textBox_Length.Focus();
            //    return false;
            //}

            // ตรวจสอบการเลือก How to Read
            if (comboBox1.SelectedIndex == 0) // 0 = "Please Select Type"
            {
                MessageBox.Show("กรุณาเลือกวิธีการอ่าน (How to Read)");
                comboBox1.Focus();
                return false;
            }

            return true;
        }


        private void SetDataToForm(DataGridViewRow row)
        {
            textBox1.Text = row.Cells["Item Number"].Value?.ToString();
            textBox2.Text = row.Cells["Parameter"].Value?.ToString();
            textBox3.Text = row.Cells["Address"].Value?.ToString();

            string param = row.Cells["Parameter"].Value?.ToString();
            if (param != null && param.Equals("Status", StringComparison.OrdinalIgnoreCase))
            {
                var statusValue = row.Cells["Status"].Value;
                if (statusValue is bool && (bool)statusValue)
                {
                    textBox_Value.Text = "ON";
                }
                else
                {
                    textBox_Value.Text = "OFF";
                }
            }
            else
            {
                textBox_Value.Text = row.Cells["Value"].Value?.ToString();
            }

            comboBox1.SelectedItem = row.Cells["Type"].Value?.ToString();
        }

        private void SetDataToForm(DataRow row)
        {
            textBox1.Text = row["Item Number"].ToString();
            textBox2.Text = row["Parameter"].ToString();
            textBox3.Text = row["Address"].ToString();
            comboBox1.SelectedItem = row["Type"].ToString();

            if (row["Parameter"].ToString().ToLower() == "status")
            {
                bool status = Convert.ToBoolean(row["Status"]);
                textBox_Value.Text = status ? "1" : "0";
            }
            else
            {
                textBox_Value.Text = row["Value"].ToString();
            }
        }



        private void DataGridView1_SelectionChanged(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow != null && dataGridView1.CurrentRow.Index >= 0)
            {
                SetDataToForm(dataGridView1.CurrentRow);
            }
        }

        private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            // ตรวจว่ามีแถวถูกคลิก และไม่ใช่ header row
            if (e.RowIndex >= 0)
            {
                SetDataToForm(dataGridView1.CurrentRow);
            }
        }


        private void dataGridView1_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (dataGridView1.Columns[e.ColumnIndex].Name == "Value")
            {
                var row = dataGridView1.Rows[e.RowIndex];
                var parameter = row.Cells["Parameter"].Value?.ToString();
                var status = row.Cells["Status"].Value;

                if (parameter != null && parameter.Equals("status", StringComparison.OrdinalIgnoreCase))
                {
                    // ถ้า Status == true → แสดง "ON"
                    if (status is bool && (bool)status)
                    {
                        e.Value = "ON";
                        e.FormattingApplied = true;
                    }

                    else
                    {
                        e.Value = "OFF";
                    }

                }
            }
        }


        private void Insert_Click(object sender, EventArgs e)
        {
            if (!ValidateInput()) return;

            try
            {
                Parameter param = new Parameter(
                    Convert.ToInt32(textBox1.Text),
                    textBox2.Text,
                    textBox3.Text,
                    textBox_Value.Text,
                    comboBox1.SelectedItem.ToString()
                );

                DatabaseConnector db = new DatabaseConnector(connectionString);
                bool success = db.InsertData(
                    param.ItemNumber,
                    param.ParameterName,
                    param.Address,
                    param.Value,
                    param.Status,
                    param.Type
                );

                if (success)
                {
                    dataGridView1.DataSource = db.GetAllData();
                    MessageBox.Show("เพิ่มข้อมูลสำเร็จ");
                }
                else
                {

                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error: " + ex.Message);
            }
        }


        private void Update_Click(object sender, EventArgs e)
        {
            if (!ValidateInput()) return;

            try
            {
                Parameter param = new Parameter(
                    Convert.ToInt32(textBox1.Text),
                    textBox2.Text,
                    textBox3.Text,
                    textBox_Value.Text,
                    comboBox1.SelectedItem.ToString()
                );

                DatabaseConnector db = new DatabaseConnector(connectionString);
                bool success = db.UpdateData(
                    param.ItemNumber,
                    param.ParameterName,
                    param.Address,
                    param.Value,
                    param.Status,
                    param.Type
                );

                dataGridView1.DataSource = db.GetAllData();
                MessageBox.Show(success ? "อัปเดตข้อมูลสำเร็จ" : "ไม่พบข้อมูลที่ต้องการอัปเดต");
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error: " + ex.Message);
            }
        }


        private void Delete_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentCell == null)
            {
                MessageBox.Show("กรุณาเลือกแถวที่ต้องการลบ");
                return;
            }

            int rowIndex = dataGridView1.CurrentCell.RowIndex;
            DataGridViewRow selectedRow = dataGridView1.Rows[rowIndex];

            int itemNumber = Convert.ToInt32(selectedRow.Cells["Item Number"].Value);

            var result = MessageBox.Show($"คุณต้องการลบ Item Number {itemNumber} หรือไม่?", "ยืนยันการลบ", MessageBoxButtons.YesNo);
            if (result == DialogResult.No) return;

            DatabaseConnector db = new DatabaseConnector(connectionString);
            bool success = db.DeleteData(itemNumber);

            if (success)
            {
                MessageBox.Show("ลบข้อมูลสำเร็จ");
                dataGridView1.DataSource = db.GetAllData();
            }
            else
            {
                MessageBox.Show("ไม่สามารถลบข้อมูลได้");
            }
        }



        private void Show_Click(object sender, EventArgs e)
        {
            DatabaseConnector db = new DatabaseConnector(connectionString); // ส่งเข้าไป
            DataTable dt = db.GetAllData();
            dataGridView1.DataSource = dt;
            dataGridView1.RowHeadersWidth = 40;
            dataGridView1.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
        }

        private void FindItem_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(textBox1.Text)) return;

            int itemNo;
            if (!int.TryParse(textBox1.Text, out itemNo))
            {
                MessageBox.Show("Item Number ต้องเป็นตัวเลข");
                return;
            }

            DataRow result = db.FindByItemNumber(itemNo); 

            if (result != null)
            {
                SetDataToForm(result); 

                dataGridView1.ClearSelection();
                foreach (DataGridViewRow row in dataGridView1.Rows)
                {
                    if (row.Cells["Item Number"].Value != null &&
                        Convert.ToInt32(row.Cells["Item Number"].Value) == itemNo)
                    {
                        row.Selected = true;
                        dataGridView1.FirstDisplayedScrollingRowIndex = row.Index;
                        break;
                    }
                }
            }
            else
            {
                MessageBox.Show("ไม่พบข้อมูล Item Number นี้");
            }
        }



    }
}