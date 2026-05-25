using System;
using System.Collections.Generic;
using System.Net.Http.Json;
using System.Text;

namespace ClientApp.Services
{
    public class ApiResponse<T>
    {
        public T? Data { get; set; }
        public int StatusCode { get; set; }
        public bool IsSuccess { get; set; }
        public string? ErrorMessage { get; set; }

        public ApiResponse()
        {
        }
    }
}
