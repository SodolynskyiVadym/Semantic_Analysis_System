using System.Text.Json.Serialization;

namespace ClientApp.Models
{
    public class AudioTaskUpdate
    {
        [JsonPropertyName("analysis")]
        public List<AnalysisSegment>? Analysis { get; set; }

        [JsonPropertyName("transcription")]
        public List<TranscribeSegment>? Transcription { get; set; }

        [JsonPropertyName("entities")]
        public List<string>? Entities { get; set; }
    }
}
