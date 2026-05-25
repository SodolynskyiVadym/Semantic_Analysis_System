using System;
using System.Collections.Generic;
using System.Text;

namespace ClientApp.Models
{
    public class AudioTaskUpdateRequest
    {
        public string Id { get; set; }
        public string FileName { get; set; }
        public AudioTaskStatus Status { get; set; }
        public List<TranscribeSegmentDto> Transcription { get; set; }
        public List<AnalysisSegmentDto> Analysis { get; set; }
        public List<string> Entities { get; set; }
    }

    public class TranscribeSegmentDto { public double Start { get; set; } public double End { get; set; } public double Confidence { get; set; } public string Text { get; set; } }
    public class AnalysisSegmentDto { public double Start { get; set; } public double End { get; set; } public string Word { get; set; } public string EntityGroup { get; set; } public double Score { get; set; } }
}
