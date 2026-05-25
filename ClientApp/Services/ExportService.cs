using System.Text.Json;
using Microsoft.JSInterop;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;
using ClientApp.Models; // Замініть на ваш неймспейс

namespace ClientApp.Services
{
    public class ExportService
    {
        private readonly IJSRuntime _jsRuntime;

        public ExportService(IJSRuntime jsRuntime)
        {
            _jsRuntime = jsRuntime;
            QuestPDF.Settings.License = LicenseType.Community;
        }

        // 1. Експорт сирого AudioTask у JSON
        public async Task ExportToJsonAsync(AudioTask task)
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };

            var jsonString = JsonSerializer.Serialize(task, options);
            var bytes = System.Text.Encoding.UTF8.GetBytes(jsonString);

            await DownloadFileAsync($"{task.FileName}_raw.json", "application/json", bytes);
        }

        public async Task ExportToPdfAsync(ViewAudioTask viewTask)
        {
            var document = Document.Create(container =>
            {
                container.Page(page =>
                {
                    page.Size(PageSizes.A4);
                    page.Margin(2, Unit.Centimetre);
                    page.PageColor(QuestPDF.Helpers.Colors.White);
                    page.DefaultTextStyle(x => x.FontSize(11).FontFamily(Fonts.Arial));

                    page.Header().Element(c => ComposeHeader(c, viewTask));
                    page.Content().Element(c => ComposeContent(c, viewTask));
                    page.Footer().AlignCenter().Text(x =>
                    {
                        x.Span("Сторінка ");
                        x.CurrentPageNumber();
                        x.Span(" із ");
                        x.TotalPages();
                    });
                });
            });

            var bytes = document.GeneratePdf();
            await DownloadFileAsync($"{viewTask.FileName}_report.pdf", "application/pdf", bytes);
        }

        private void ComposeHeader(QuestPDF.Infrastructure.IContainer container, ViewAudioTask task)
        {
            container.Row(row =>
            {
                row.RelativeItem().Column(column =>
                {
                    column.Item().Text($"Звіт транскрибації: {task.FileName}").FontSize(18).SemiBold().FontColor(QuestPDF.Helpers.Colors.Black);
                    column.Item().Text(text =>
                    {
                        text.Span("Дата створення: ").SemiBold();
                        text.Span(task.CreatedAt.ToString("dd.MM.yyyy HH:mm"));
                    });
                    column.Item().Text(text =>
                    {
                        text.Span("Статус обробки: ").SemiBold();
                        text.Span(task.Status.ToString());
                    });
                });
            });
        }

        private void ComposeContent(QuestPDF.Infrastructure.IContainer container, ViewAudioTask task)
        {
            container.PaddingVertical(1, Unit.Centimetre).Column(column =>
            {
                column.Spacing(10);

                if (task.Transcription == null || !task.Transcription.Any())
                {
                    column.Item().Text("Текст транскрибації відсутній.").Italic().FontColor(QuestPDF.Helpers.Colors.Grey.Medium);
                    return;
                }

                foreach (var segment in task.Transcription)
                {
                    column.Item().Row(row =>
                    {
                        row.ConstantItem(50).Text(FormatTime(segment.Start)).FontColor(QuestPDF.Helpers.Colors.Grey.Darken2).SemiBold();

                        row.RelativeItem().Text(text =>
                        {
                            foreach (var word in segment.Transcribe)
                            {
                                if (string.IsNullOrEmpty(word.EntityGroup))
                                {
                                    text.Span(word.Text + " ");
                                }
                                else
                                {
                                    text.Span(word.Text)
                                        .BackgroundColor(GetEntityColor(word.EntityGroup))
                                        .FontColor(QuestPDF.Helpers.Colors.White)
                                        .SemiBold();
                                    text.Span(" ");
                                }
                            }
                        });
                    });
                }
            });
        }

        private string GetEntityColor(string entityGroup)
        {
            return entityGroup switch
            {
                "LOCATION" => "#198754",          
                "PERSONNEL-ENEMY" => "#dc3545",    
                "EQUIPMENT-ENEMY" => "#dc3545",
                "PERSONNEL-FRIENDLY" => "#0d6efd", 
                "EQUIPMENT-FRIENDLY" => "#0d6efd",
                "QUANTITY" => "#6c757d",       
                _ => "#ced4da"
            };
        }

        private string FormatTime(double seconds)
        {
            return TimeSpan.FromSeconds(seconds).ToString(@"mm\:ss");
        }

        private async Task DownloadFileAsync(string fileName, string contentType, byte[] bytes)
        {
            var base64 = Convert.ToBase64String(bytes);
            await _jsRuntime.InvokeVoidAsync("blazorDownloadFile", fileName, contentType, base64);
        }
    }
}