using System;
using System;
using System.Collections.Generic;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static MiniProject.Form2;


namespace MiniProject
{
    internal class DatabaseConnector
    {

        public readonly string connectionString;

        public DatabaseConnector()
        {
        }

        public DatabaseConnector(string connString)
        {
            this.connectionString = connString;
        }

        // ตัวอย่างเมธอด
        public DataTable GetAllData()
        {
            string query = "SELECT [Item Number], [Parameter], [Address], [Value], [Status], [Type] FROM [MiniProject-(table1)]";

            using (SqlConnection conn = new SqlConnection(connectionString))
            using (SqlCommand cmd = new SqlCommand(query, conn))
            using (SqlDataAdapter adapter = new SqlDataAdapter(cmd))
            {
                DataTable dt = new DataTable();
                try
                {
                    conn.Open();
                    adapter.Fill(dt);
                    return dt;
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Database Error: " + ex.Message);
                    return null;
                }
            }
        }

        public DataTable GetTable2Data()
        {
            string query = "SELECT * FROM [MiniProject-(table2)]";

            using (SqlConnection conn = new SqlConnection(connectionString))
            using (SqlCommand cmd = new SqlCommand(query, conn))
            using (SqlDataAdapter adapter = new SqlDataAdapter(cmd))
            {
                DataTable dt = new DataTable();
                try
                {
                    conn.Open();
                    adapter.Fill(dt);
                    return dt;
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Database Error: " + ex.Message);
                    return null;
                }
            }
        }




        public bool InsertData(int itemNumber, string parameter, string address, string value, string status, string type)
        {
            string query = "INSERT INTO [MiniProject-(table1)] ([Item Number], [Parameter], [Address], [Value], [Status], [Type]) " +
                           "VALUES (@ItemNumber, @Parameter, @Address, @Value, @Status, @Type)";

            using (SqlConnection conn = new SqlConnection(connectionString))
            using (SqlCommand cmd = new SqlCommand(query, conn))
            {
                cmd.Parameters.AddWithValue("@ItemNumber", itemNumber);
                cmd.Parameters.AddWithValue("@Parameter", parameter);
                cmd.Parameters.AddWithValue("@Address", address);
                cmd.Parameters.AddWithValue("@Value", value);
                cmd.Parameters.AddWithValue("@Status", status);
                cmd.Parameters.AddWithValue("@Type", type);

                try
                {
                    conn.Open();
                    GetAllData();
                    return cmd.ExecuteNonQuery() > 0;
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Database Error: " + ex.Message);
                    return false;
                }
            }
        }


        public bool UpdateData(int itemNumber, string parameter, string address, string value, string status, string type)
        {
            string query = "UPDATE [MiniProject-(table1)] " +
                           "SET [Parameter] = @Parameter, [Address] = @Address, [Value] = @Value, [Status] = @Status, [Type] = @Type " +
                           "WHERE [Item Number] = @ItemNumber";

            using (SqlConnection conn = new SqlConnection(connectionString))
            using (SqlCommand cmd = new SqlCommand(query, conn))
            {
                cmd.Parameters.AddWithValue("@ItemNumber", itemNumber);
                cmd.Parameters.AddWithValue("@Parameter", parameter);
                cmd.Parameters.AddWithValue("@Address", address);
                cmd.Parameters.AddWithValue("@Value", value);
                cmd.Parameters.AddWithValue("@Status", status);
                cmd.Parameters.AddWithValue("@Type", type);

                try
                {
                    conn.Open();
                    return cmd.ExecuteNonQuery() > 0;
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Database Error: " + ex.Message);
                    return false;
                }
            }
        }


        public bool DeleteData(int itemNumber)
        {
            string query = "DELETE FROM [MiniProject-(table1)] WHERE [Item Number] = @ItemNumber";

            using (SqlConnection conn = new SqlConnection(connectionString))
            using (SqlCommand cmd = new SqlCommand(query, conn))
            {
                cmd.Parameters.AddWithValue("@ItemNumber", itemNumber);

                try
                {
                    conn.Open();
                    return cmd.ExecuteNonQuery() > 0;
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Database Error: " + ex.Message);
                    return false;
                }
            }
        }


        public DataRow FindByItemNumber(int itemNumber)
        {
            string query = "SELECT * FROM [MiniProject-(table1)] WHERE [Item Number] = @ItemNumber";

            using (SqlConnection conn = new SqlConnection(connectionString))
            using (SqlCommand cmd = new SqlCommand(query, conn))
            {
                cmd.Parameters.AddWithValue("@ItemNumber", itemNumber);

                using (SqlDataAdapter adapter = new SqlDataAdapter(cmd))
                {
                    DataTable dt = new DataTable();
                    adapter.Fill(dt);

                    if (dt.Rows.Count > 0)
                    {
                        return dt.Rows[0]; // คืนแค่แถวแรกที่เจอ
                    }
                    else
                    {
                        return null; // ไม่พบ
                    }
                }
            }
        }































    }

}
