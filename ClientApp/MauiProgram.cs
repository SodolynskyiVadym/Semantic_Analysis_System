using ClientApp.Services;
using Microsoft.Extensions.Logging;

namespace ClientApp
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                });

            string apiUrl = "http://localhost:8000";

            HttpClient httpClient = new HttpClient();


            builder.Services.AddMauiBlazorWebView();
            builder.Services.AddSingleton(sp => new ApiService($"{apiUrl}/tasks", httpClient));
            builder.Services.AddScoped<ExportService>();

#if DEBUG
            builder.Services.AddBlazorWebViewDeveloperTools();
    		builder.Logging.AddDebug();
#endif

            return builder.Build();
        }
    }
}
