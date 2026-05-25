using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace ClientApp.Models
{
    public record TranscribeSegment(
        [property: JsonPropertyName("start")] double Start,
        [property: JsonPropertyName("end")] double End,
        [property: JsonPropertyName("confidence")] double Confidence,
        [property: JsonPropertyName("text")] string Text
);
}
