using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Conveiyor
{
    internal class PythonConnector
    {
        private TcpListener _listener;
        private bool _running = false;

        public event Action<PythonData> OnDataReceived;

        public PythonConnector(int port = 5000)
        {
            _listener = new TcpListener(IPAddress.Loopback, port);
        }

        public void Start()
        {
            _listener.Start();
            _running = true;
            Task.Run(() => AcceptClientsAsync());
        }

        public void Stop()
        {
            _running = false;
            _listener.Stop();
        }

        private async Task AcceptClientsAsync()
        {
            while (_running)
            {
                try
                {
                    var client = await _listener.AcceptTcpClientAsync();
                    _ = Task.Run(() => HandleClientAsync(client));
                }
                catch { }
            }
        }

        private async Task HandleClientAsync(TcpClient client)
        {
            using (client)
            using (var stream = client.GetStream())
            {
                byte[] buffer = new byte[1024];
                while (_running)
                {
                    try
                    {
                        int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                        if (bytesRead == 0) break;

                        string json = Encoding.UTF8.GetString(buffer, 0, bytesRead);

                        var dataObj = JsonConvert.DeserializeObject<PythonData>(json);
                        OnDataReceived?.Invoke(dataObj);

                    }
                    catch { break; }
                }
            }
        }
    }

    public class PythonData
    {
        public string color { get; set; }
        public List<string> QRdata { get; set; } = new List<string>();
        public List<string> Bardata { get; set; } = new List<string>();
    }



}
