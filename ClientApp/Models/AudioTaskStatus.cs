using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace ClientApp.Models
{
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum AudioTaskStatus
    {
        [JsonPropertyName("PENDING")]
        Pending,

        [JsonPropertyName("TRANSCRIBED")]
        Transcribed,

        [JsonPropertyName("COMPLETED")]
        Completed,

        [JsonPropertyName("FAILED")]
        Failed
    }
}
