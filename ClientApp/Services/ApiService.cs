using ClientApp.Models;
using System;
using System.Collections.Generic;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text;

namespace ClientApp.Services
{
    public class ApiService
    {
        private HttpClient _httpClient;
        private string _url;

        public ApiService(string url, HttpClient httpClient)
        {
            _httpClient = httpClient;
            _url = url;
        }

        public async Task<ApiResponse<List<AudioTask>>> GetAudioTasksAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync(_url);

                if (response.IsSuccessStatusCode)
                {
                    var options = new System.Text.Json.JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true,
                        Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter() }
                    };

                    var audioTasks = await response.Content.ReadFromJsonAsync<List<AudioTask>>(options);

                    return new ApiResponse<List<AudioTask>>
                    {
                        Data = audioTasks,
                        StatusCode = (int)response.StatusCode,
                        IsSuccess = true
                    };
                }

                return new ApiResponse<List<AudioTask>>
                {
                    Data = null,
                    StatusCode = (int)response.StatusCode,
                    IsSuccess = false,
                    ErrorMessage = $"Server error: {response.ReasonPhrase}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse<List<AudioTask>> { IsSuccess = false, ErrorMessage = ex.Message };
            }
        }


        public async Task<ApiResponse<AudioTask>> GetAudioTaskByIdAsync(string id)
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_url}/{id}");

                if (response.IsSuccessStatusCode)
                {
                    var options = new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                    options.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter());

                    var task = await response.Content.ReadFromJsonAsync<AudioTask>(options);
                    return new ApiResponse<AudioTask> { Data = task, IsSuccess = true };
                }
                return new ApiResponse<AudioTask> { IsSuccess = false, ErrorMessage = response.ReasonPhrase };
            }
            catch (Exception ex)
            {
                return new ApiResponse<AudioTask> { IsSuccess = false, ErrorMessage = ex.Message };
            }
        }



        public async Task<ApiResponse<AudioTask>> UpdateAudioTaskAsync(AudioTaskUpdateRequest request)
        {
            try
            {
                var json = System.Text.Json.JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PatchAsync($"{_url}/{request.Id}", content);

                if (response.IsSuccessStatusCode)
                {
                    var options = new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                    options.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter());

                    var task = await response.Content.ReadFromJsonAsync<AudioTask>(options);
                    return new ApiResponse<AudioTask> { Data = task, IsSuccess = true };
                }

                return new ApiResponse<AudioTask> { IsSuccess = false, ErrorMessage = response.ReasonPhrase };
            }
            catch (Exception ex)
            {
                return new ApiResponse<AudioTask> { IsSuccess = false, ErrorMessage = ex.Message };
            }
        }
    }
}
