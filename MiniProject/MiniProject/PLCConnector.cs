using ActUtlTypeLib;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Net.Mime.MediaTypeNames;

namespace PCLStudy
{
    using ActUtlTypeLib;

    public class PLCConector
    {
        private ActUtlType plc;
        private int logicalNo;

        public PLCConector(int logicalNo)
        {
            this.logicalNo = logicalNo;
            plc = new ActUtlType();
            plc.ActLogicalStationNumber = logicalNo;
        }

        public bool Connect()
        {
            int result = plc.Open();
            return result == 0;
        }

        public void Disconnect()
        {
            plc.Close();
        }

        public short ReadPlcData(string Address)
        {
            plc.ReadDeviceRandom2(Address, 1, out short result);
            return result;
        }

        public void WritePlcData(string Addess, int dataWrite)
        {
            plc.WriteDeviceRandom(Addess, 1, dataWrite);
        }

        public int ReadPlcstatus(string Address)
        {
            plc.ReadDeviceRandom2(Address, 1, out short result);
            return result;
        }

        public void WritePlcstatus(string Addess, int dataWrite)
        {
            plc.WriteDeviceRandom(Addess, 1, dataWrite);
        }

        public string ReadPlcAscii(string address, int length)
        {

            int index = int.Parse(new string(address.SkipWhile(char.IsLetter).ToArray()));

            short[] result = new short[length];

            for (int i = 0; i < length; i++)
            {
                string addr = $"D{index + i}";
                short value;
                plc.ReadDeviceRandom2(addr, 1, out value);
                result[i] = value;
            }

            // แปลง short[] → byte[] → ASCII string
            byte[] bytes = new byte[length * 2];
            for (int i = 0; i < length; i++)
            {
                bytes[i * 2] = (byte)(result[i] & 0xFF);
                bytes[i * 2 + 1] = (byte)((result[i] >> 8) & 0xFF);
            }

            return System.Text.Encoding.ASCII.GetString(bytes).TrimEnd('\0');

            //char character = address.TakeWhile(char.IsLetter).FirstOrDefault();
            //int index = int.Parse(new string(address.SkipWhile(char.IsLetter).ToArray()));

            //short[] result = new short[length];

            //for (int i = 0; i < length; i++)
            //{
            //    string addr = $"{character}{index + i}";
            //    short value;
            //    plc.ReadDeviceRandom2(addr, 1, out value);           ในกรณีไม่ได้อ่านแค่่ D 
            //    result[i] = value;
            //}

            //// แปลง short[] → byte[] → ASCII string
            //byte[] bytes = new byte[length * 2];
            //for (int i = 0; i < length; i++)
            //{
            //    bytes[i * 2] = (byte)(result[i] & 0xFF);
            //    bytes[i * 2 + 1] = (byte)((result[i] >> 8) & 0xFF);
            //}

            //return System.Text.Encoding.ASCII.GetString(bytes).TrimEnd('\0');            
        }


        public string WritePlcAscii(string address, int length, string value)
        {
            // แปลง string → byte[]
            byte[] bytes = System.Text.Encoding.ASCII.GetBytes(value);

            // เติม '\0' ให้ครบความยาว (length * 2 bytes)
            if (bytes.Length < length * 2)
            {
                Array.Resize(ref bytes, length * 2);
            }

            // แปลงเป็น short[] (2 bytes ต่อ 1 short)
            short[] data = new short[length];
            for (int i = 0; i < length; i++)
            {
                data[i] = (short)(bytes[i * 2] | (bytes[i * 2 + 1] << 8));
            }

            // แยก index จาก address เช่น "D0" → 0
            int index = int.Parse(new string(address.SkipWhile(char.IsLetter).ToArray()));

            // เขียนค่าทีละ word ไปยัง D0, D1, ...
            for (int i = 0; i < length; i++)
            {
                string addr = $"D{index + i}";
                plc.WriteDeviceRandom2(addr, 1, ref data[i]);
            }
            return value;
        }

        public float ReadPlcfloat(string address)
        {
            short[] result = new short[2];
            plc.ReadDeviceBlock2(address, 2, out result[0]);

            //ushort Checlower = (ushort)result[0]; 
            //ushort Checupper = (ushort)result[1]; 

            byte[] bytes = new byte[4];
            bytes[0] = (byte)(result[0] & 0xFF);
            bytes[1] = (byte)((result[0] >> 8) & 0xFF);
            bytes[2] = (byte)(result[1] & 0xFF);
            bytes[3] = (byte)((result[1] >> 8) & 0xFF);

            float resultreturn = BitConverter.ToSingle(bytes, 0);
            return resultreturn;
        }

        public void WritePlcfloat(string address, float value)
        {
            // แปลง float เป็น 4 bytes (2 word)
            byte[] bytes = BitConverter.GetBytes(value); // little-endian
            short[] words = new short[2];

            // แปลง byte -> short array
            words[0] = BitConverter.ToInt16(bytes, 0); // lower word
            words[1] = BitConverter.ToInt16(bytes, 2); // upper word

            // เขียนลง PLC 2 word
            plc.WriteDeviceBlock2(address, 2, ref words[0]); // หรือใช้ WriteDeviceRandom2 ก็ได้
        }
    




    }

}
