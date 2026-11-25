using JobShield.Application;
using JobShield.Infrastructure;
using Xunit;

namespace JobShield.Tests;

public sealed class LocalSentenceSplitterTests
{
    [Fact]
    public void SplitsMultiLinePostingAndPreservesNumbersUrlsEmailsAbbreviations()
    {
        const string input =
            "Địa điểm làm việc: văn phòng TP.HCM. Lương 500.000đ/ngày!\r\n" +
            "Gửi CV về hr@anphat.vn hoặc xem tại https://tuyen-dung.example.vn để biết chi tiết? Xin cảm ơn.";

        var split = LocalSentenceSplitter.Split(input);
        var prepared = SentencePreparation.Prepare(input, split);

        Assert.NotNull(prepared);
        Assert.Equal(4, prepared.Count);
        Assert.Equal("Địa điểm làm việc: văn phòng TP.HCM.", prepared[0].Text);
        Assert.Equal("Lương 500.000đ/ngày!", prepared[1].Text);
        Assert.Equal("Gửi CV về hr@anphat.vn hoặc xem tại https://tuyen-dung.example.vn để biết chi tiết?", prepared[2].Text);
        Assert.Equal("Xin cảm ơn.", prepared[3].Text);
        Assert.All(prepared, s =>
        {
            Assert.Equal("unknown", s.Type);
            Assert.Equal("unknown", s.Speaker);
            Assert.Equal(s.Text, input[s.Start..s.End]);
        });
    }

    [Fact]
    public void DetectsRecruiterAndApplicantTurnsAcrossSplitSentences()
    {
        const string input =
            "HR: Em cần đóng phí hồ sơ 500.000đ. Chuyển trước 17h nhé!\n" +
            "Ứng viên: Dạ phí này có hoàn lại không ạ?\n" +
            "Quản lý: Hoàn lại sau khi nhận việc.";

        var split = LocalSentenceSplitter.Split(input);
        var prepared = SentencePreparation.Prepare(input, split);

        Assert.NotNull(prepared);
        Assert.Equal(4, prepared.Count);
        Assert.Equal(("message", "recruiter"), (prepared[0].Type, prepared[0].Speaker));
        Assert.Equal(("message", "recruiter"), (prepared[1].Type, prepared[1].Speaker));
        Assert.Equal(("message", "applicant"), (prepared[2].Type, prepared[2].Speaker));
        Assert.Equal(("message", "recruiter"), (prepared[3].Type, prepared[3].Speaker));
    }

    [Fact]
    public async Task SplitServiceFallsBackToLocalWhenGroqIsNotConfigured()
    {
        var service = new SentenceSplitService();
        const string input = "Tuyển CTV tại nhà. Nộp cọc 300.000đ.";

        var (sentences, source) = await service.SplitAsync(input, CancellationToken.None);

        Assert.Equal("local", source);
        Assert.NotNull(sentences);
        Assert.Equal(2, sentences.Count);
        Assert.Equal("Tuyển CTV tại nhà.", sentences[0].Text);
        Assert.Equal("Nộp cọc 300.000đ.", sentences[1].Text);
    }
}
