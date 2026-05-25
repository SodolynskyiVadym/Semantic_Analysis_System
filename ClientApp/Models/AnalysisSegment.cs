using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace ClientApp.Models
{
    public record AnalysisSegment(
        [property: JsonPropertyName("start")] double Start,
        [property: JsonPropertyName("end")] double End,
        [property: JsonPropertyName("word")] string Word,
        [property: JsonPropertyName("score")] double Score,
        [property: JsonPropertyName("entity_group")] string EntityGroup
);
}
