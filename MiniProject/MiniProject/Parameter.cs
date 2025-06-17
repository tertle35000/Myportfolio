using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MiniProject
{
    public class Parameter
    {
        public int ItemNumber { get; set; }
        public string ParameterName { get; set; }
        public string Address { get; set; }
        public string Value { get; set; }
        public string Status { get; set; }
        public string Type { get; set; }

        public Parameter(int itemNumber, string parameter, string address, string valueText, string type)
        {
            ItemNumber = itemNumber;
            ParameterName = parameter.Trim();
            Address = address.Trim();
            Type = type;

            if (parameter.Equals("Status", StringComparison.OrdinalIgnoreCase))
            {
                Status = (valueText == "0" || valueText == "1") ? valueText : "";
                Value = "";
            }
            else
            {
                Value = valueText.Trim();
                Status = "";
            }
        }
    }



}
