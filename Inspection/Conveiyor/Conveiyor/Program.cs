using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace Conveiyor
{
    internal static class Program
    {
        public static PythonConnector Connector; // ประกาศเป็น static เพื่อให้ Form1 เข้าถึงได้

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            // สร้าง PythonConnector และเริ่มฟังข้อมูล
            Connector = new PythonConnector(5000);
            Connector.Start();

            // เปิด Form1
            Application.Run(new Form1());

            // เมื่อปิด Form ให้หยุด Connector
            Connector.Stop();
        }
    }
}
