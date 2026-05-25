using System;
using System.Collections.Generic;
using System.Text;

namespace ClientApp.Models
{
    public class ViewAudioTask
    {
        public string Id;
        public string FileName;
        public AudioTaskStatus Status;
        public DateTime CreatedAt;
        public List<AnalysisSegment>? Analysis = null;
        public List<ViewTranscribeSegment>? Transcription = null;
        public List<string>? Entities = null;
    }

    public class ViewTranscribeSegment
    {
        public double Start;
        public double End;
        public double Confidence;
        public List<Word>? Transcribe = null;
    }

    public class Word
    {
        public string Text;
        public string? EntityGroup;
    }
}
