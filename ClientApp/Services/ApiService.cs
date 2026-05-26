using ClientApp.Models;
using Microsoft.AspNetCore.Components.Forms;
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



        public async Task<ApiResponse<AudioTask>> UpdateTranscribeAudioTaskAsync(string id, AudioTaskUpdate request)
        {
            try
            {
                var json = System.Text.Json.JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PatchAsync($"{_url}/transcription/{id}", content);

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


        public async Task<ApiResponse<AudioTask>> UpdateAnalysisAudioTaskAsync(string id, AudioTaskUpdate request)
        {
            try
            {
                var json = System.Text.Json.JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PatchAsync($"{_url}/analysis/{id}", content);

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


        public async Task<ApiResponse<Boolean>> DeleteAudioTaskByID(string id)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"{_url}/{id}");
                if (response.IsSuccessStatusCode)
                {
                    return new ApiResponse<Boolean> { IsSuccess = true, StatusCode = (int)response.StatusCode };
                }
                else
                {
                    return new ApiResponse<Boolean> { IsSuccess = false, StatusCode = (int)response.StatusCode, ErrorMessage = response.ReasonPhrase };
                }
            }
            catch (Exception ex)
            {
                return new ApiResponse<Boolean> { IsSuccess = false, ErrorMessage = ex.Message };
            }
        }


        public async Task<ApiResponse<AudioTask>> UploadAudioTaskAsync(IBrowserFile file)
        {
            try
            {
                using var content = new MultipartFormDataContent();

                long maxFileSize = 1024 * 1024 * 50;

                var fileStreamContent = new StreamContent(file.OpenReadStream(maxAllowedSize: maxFileSize));

                fileStreamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(file.ContentType);

                content.Add(fileStreamContent, "file", file.Name);

                var response = await _httpClient.PostAsync($"{_url}", content);

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
