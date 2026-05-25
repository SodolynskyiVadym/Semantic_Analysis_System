using ClientApp.Models;
using System;
using System.Collections.Generic;
using System.Text;

namespace ClientApp.Services
{
    public class TranscriptNormalizer
    {
        public static ViewAudioTask ToViewModel(AudioTask rawData)
        {
            var viewTask = new ViewAudioTask
            {
                Id = rawData.Id,
                FileName = rawData.FileName,
                Status = rawData.Status,
                CreatedAt = rawData.CreatedAt,
                Analysis = rawData.Analysis,
                Entities = rawData.Entities?.Select(e => e.ToString()).ToList(),
                Transcription = new List<ViewTranscribeSegment>()
            };

            if (rawData.Transcription == null || rawData.Transcription.Count == 0)
                return viewTask;

            int globalCharIndex = 0;

            foreach (var segment in rawData.Transcription)
            {
                var viewSegment = new ViewTranscribeSegment
                {
                    Start = segment.Start,
                    End = segment.End,
                    Confidence = segment.Confidence,
                    Transcribe = new List<Word>()
                };

                if (!string.IsNullOrEmpty(segment.Text))
                {
                    string[] words = segment.Text.Split(' ');
                    int localCharIndex = 0;

                    foreach (var w in words)
                    {
                        int wordStart = globalCharIndex + localCharIndex;
                        int wordEnd = wordStart + w.Length;

                        string? entityGroup = null;

                        if (rawData.Analysis != null)
                        {
                            var matchedEntity = rawData.Analysis.FirstOrDefault(a =>
                                (int)a.Start < wordEnd && (int)a.End > wordStart);

                            if (matchedEntity != null)
                            {
                                entityGroup = matchedEntity.EntityGroup.ToString();
                            }
                        }

                        viewSegment.Transcribe.Add(new Word
                        {
                            Text = w,
                            EntityGroup = entityGroup
                        });

                        localCharIndex += w.Length + 1;
                    }
                }

                viewTask.Transcription.Add(viewSegment);

                globalCharIndex += segment.Text.Length + 1;
            }

            return viewTask;
        }
    }
}
