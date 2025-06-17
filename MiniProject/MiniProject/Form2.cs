using PCLStudy;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.SqlClient;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MiniProject
{
    public partial class Form2 : Form
    {
        private DatabaseConnector db;
        private string connectionString = "Server=localhost\\SQLEXPRESS;Database=MyDatabase;Trusted_Connection=True;";
        private bool isInserting = true;


        public Form2(string connectionString)
        {
            InitializeComponent();
            db = new DatabaseConnector(connectionString); // ส่งจาก Form1
        }

        private void btnToggle_Click(object sender, EventArgs e)
        {
            isInserting = !isInserting;

            btnToggle.Text = isInserting ? "Stop" : "Continue";
        }

        private PLCConector plc;
        int logicalNo;

        private void Form2_Load(object sender, EventArgs e)
        {

            int logicalNo = Convert.ToInt32(File.ReadAllText("ConfigNo/LogicalNo.txt"));
            plc = new PLCConector(logicalNo);
            timer1.Interval = 1000;
            timer1.Start();
           
            try
            {
                plc = new PLCConector(logicalNo);

                if (!plc.Connect())
                {
                    MessageBox.Show("ไม่สามารถเชื่อมต่อกับ PLC ได้", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    this.Close();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"เกิดข้อผิดพลาดในการเชื่อมต่อ PLC: {ex.Message}", "Exception", MessageBoxButtons.OK, MessageBoxIcon.Error);
                this.Close();
            }


            // ตั้งค่าเวลา
            dateTimePicker1.Format = DateTimePickerFormat.Custom;
            dateTimePicker1.CustomFormat = "dd/MM/yyyy HH:mm:ss";
            dateTimePicker1.Value = DateTime.Now;

            timer1.Interval = 1000;
            timer1.Start();

            // โหลดข้อมูลจาก MiniProject-(table2)
            DataTable dt = db.GetTable2Data();
            if (dt != null)
            {
                dataGridView2.DataSource = dt;
            }

            dataGridView2.RowHeadersWidth = 30;
            dataGridView2.Columns["id"].Width = 70;
            dataGridView2.Columns["Value"].Width = 110;
            dataGridView2.Columns["Item Number"].Width = 50;
            dataGridView2.Columns["Parameter"].Width = 80;
            dataGridView2.Columns["Address"].Width = 70;
            dataGridView2.Columns["Status"].Width = 50;
            dataGridView2.Columns["Type"].Width = 50;
            dataGridView2.Columns["Datatime"].Width = 110;

            btnToggle.Text = "Stop"; // ค่าเริ่มต้น
        }


        private void timer1_Tick(object sender, EventArgs e)
        {
            dateTimePicker1.Value = DateTime.Now;

            if (isInserting)
            {
                InsertFromTable1ToTable2(); // เฉพาะตอนเปิดสถานะเท่านั้น
                LoadTable2Data(); // โหลดมาแสดงทุกวินาทีเหมือนเดิม
            }

            dataGridView2.RowHeadersWidth = 30;
            dataGridView2.Columns["id"].Width = 70;
            dataGridView2.Columns["Value"].Width = 110;
            dataGridView2.Columns["Item Number"].Width = 50;
            dataGridView2.Columns["Parameter"].Width = 80;
            dataGridView2.Columns["Address"].Width = 70;
            dataGridView2.Columns["Status"].Width = 50;
            dataGridView2.Columns["Type"].Width = 50;
            dataGridView2.Columns["Datatime"].Width = 110;

        }




        private void InsertFromTable1ToTable2()
        {
            using (SqlConnection conn = new SqlConnection(connectionString))
            {
                conn.Open();

                // ดึงข้อมูลจาก Table1
                string selectQuery = "SELECT [Item Number], [Parameter], [Address], [Status], [Type] FROM [MiniProject-(table1)]";
                SqlCommand selectCmd = new SqlCommand(selectQuery, conn);
                SqlDataReader reader = selectCmd.ExecuteReader();

                // เก็บข้อมูลไว้ใน List ก่อน
                var rows = new List<(int itemNo, string parameter, string address, string status, string type, string value)>();

                while (reader.Read())
                {
                    int itemNo = Convert.ToInt32(reader["Item Number"]);
                    string parameter = reader["Parameter"].ToString();
                    string address = reader["Address"].ToString();
                    string status = reader["Status"].ToString();
                    string type = reader["Type"].ToString().Trim().ToLower();

                    string value = "";

                    try
                    {
                        if (type == "bit")
                        {
                            int statusVal = plc.ReadPlcstatus(address);
                            value = statusVal != 0 ? "1" : "0";
                        }
                        else if (type == "int" || type == "short")
                        {
                            int intVal = plc.ReadPlcData(address); // อ่าน short แล้วแปลงเป็น int
                            value = intVal.ToString();
                        }
                        else if (type.ToLower() == "text")
                        {
                            int asciiLength = 10; // <-- ความยาวที่ต้องอ่าน (จำนวน word)
                            value = plc.ReadPlcAscii(address, asciiLength);
                        }
                        else if (type.ToLower() == "float")
                        {
                            float floatVal = plc.ReadPlcfloat(address);
                            value = floatVal.ToString("0.000"); // ปัดทศนิยม 3 ตำแหน่ง
                        }
                        else
                        {
                            value = "N/A"; // ไม่รู้จัก type นี้
                        }
                    }
                    catch (Exception ex)
                    {
                        value = "ERR"; // อ่านจาก PLC ไม่ได้
                    }



                    rows.Add((itemNo, parameter, address, status, type, value));
                }

                reader.Close(); // ปิด Reader หลังอ่านเสร็จ

                // Insert ทีละแถว
                foreach (var row in rows)
                {
                    string insertQuery = @"
                INSERT INTO [MiniProject-(table2)] 
                ([Item Number], [Parameter], [Address], [Value], [Status], [Type], [DataTime])
                VALUES (@ItemNumber, @Parameter, @Address, @Value, @Status, @Type, @DataTime)";

                    using (SqlCommand insertCmd = new SqlCommand(insertQuery, conn))
                    {
                        insertCmd.Parameters.AddWithValue("@ItemNumber", row.itemNo);
                        insertCmd.Parameters.AddWithValue("@Parameter", row.parameter);
                        insertCmd.Parameters.AddWithValue("@Address", row.address);
                        insertCmd.Parameters.AddWithValue("@Value", row.value);
                        insertCmd.Parameters.AddWithValue("@Status", row.status);
                        insertCmd.Parameters.AddWithValue("@Type", row.type);
                        insertCmd.Parameters.AddWithValue("@DataTime", DateTime.Now);

                        insertCmd.ExecuteNonQuery();
                    }
                }
            }
        }



        private void LoadTable2Data()
        {
            bool userIsSelecting = dataGridView2.SelectedRows.Count > 0;

            // จำตำแหน่ง scroll ปัจจุบันไว้
            int firstVisibleRow = -1;
            if (dataGridView2.FirstDisplayedScrollingRowIndex >= 0)
                firstVisibleRow = dataGridView2.FirstDisplayedScrollingRowIndex;

            // จำแถวที่เลือกไว้ (ถ้ามี)
            int selectedRowIndex = -1;
            if (userIsSelecting)
                selectedRowIndex = dataGridView2.SelectedRows[0].Index;

            // โหลดข้อมูลใหม่
            using (SqlConnection conn = new SqlConnection(connectionString))
            {
                string query = "SELECT * FROM [MiniProject-(table2)] ORDER BY id DESC";
                SqlDataAdapter adapter = new SqlDataAdapter(query, conn);
                DataTable dt = new DataTable();
                adapter.Fill(dt);
                dataGridView2.DataSource = dt;
            }

            // ถ้ามีการเลือกอยู่ → คงการเลือกไว้ & ไม่เปลี่ยน scroll
            if (userIsSelecting && selectedRowIndex >= 0 && selectedRowIndex < dataGridView2.Rows.Count)
            {
                dataGridView2.Rows[selectedRowIndex].Selected = true;
                if (firstVisibleRow >= 0 && firstVisibleRow < dataGridView2.Rows.Count)
                    dataGridView2.FirstDisplayedScrollingRowIndex = firstVisibleRow;
            }
            else
            {
                // ถ้าไม่มีการเลือก → scroll ไปที่บนสุด (หรือแถวใหม่สุด)
                if (dataGridView2.Rows.Count > 0)
                    dataGridView2.FirstDisplayedScrollingRowIndex = 0;
            }

            if (dataGridView2.Columns.Contains("DataTime"))
            {
                dataGridView2.Columns["DataTime"].DefaultCellStyle.Format = "yyyy-MM-dd HH:mm:ss";
            }
        }

































        public class PLCReadRequest
        {
            public string ItemNumber { get; set; }
            public string Parameter { get; set; }
            public string Address { get; set; }
            public string Type { get; set; }
        }

        public class PLCReadResult
        {
            public string ItemNumber { get; set; }
            public string Parameter { get; set; }
            public string Address { get; set; }
            public int Value { get; set; }
            public string Status { get; set; }
            public string Type { get; set; }
            public DateTime DateTime { get; set; }
        }


        private void Form2_FormClosing(object sender, FormClosingEventArgs e)
        {
            timer1.Stop();
            if (plc != null)
            {
                plc.Disconnect();
            }
        }
    }
}
