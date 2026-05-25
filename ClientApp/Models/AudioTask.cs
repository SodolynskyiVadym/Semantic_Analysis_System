using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace ClientApp.Models
{
    public record AudioTask(
        [property: JsonPropertyName("id")] string Id,
        [property: JsonPropertyName("file_name")] string FileName,
        [property: JsonPropertyName("status")] AudioTaskStatus Status,
        [property: JsonPropertyName("created_at")] DateTime CreatedAt,
        [property: JsonPropertyName("analysis")] List<AnalysisSegment>? Analysis = null,
        [property: JsonPropertyName("transcription")] List<TranscribeSegment>? Transcription = null,
        [property: JsonPropertyName("entities")] List<string>? Entities = null
);
}
