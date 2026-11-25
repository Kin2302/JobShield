using System.Text;
using System.Text.RegularExpressions;

namespace JobShield.Application;

public static partial class PiiRedactor
{
    [GeneratedRegex(@"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", RegexOptions.CultureInvariant, 200)]
    private static partial Regex EmailRegex();

    [GeneratedRegex(@"(?<!\d)\d{12}(?!\d)", RegexOptions.CultureInvariant, 200)]
    private static partial Regex CitizenIdRegex();

    [GeneratedRegex(@"(?<!\d)(?:\+84|0)(?:3|5|7|8|9)(?:[\s.\-]?\d){8}(?!\d)", RegexOptions.CultureInvariant, 200)]
    private static partial Regex VietnamPhoneRegex();

    public static string RedactSameLength(string text)
    {
        if (string.IsNullOrEmpty(text))
        {
            return text;
        }

        var buffer = text.ToCharArray();

        foreach (Match match in EmailRegex().Matches(text))
        {
            MaskEmail(buffer, match.Index, match.Length);
        }

        foreach (Match match in CitizenIdRegex().Matches(text))
        {
            MaskKeepingPrefixDigits(buffer, match.Index, match.Length, keepDigits: 3);
        }

        foreach (Match match in VietnamPhoneRegex().Matches(text))
        {
            var keepDigits = text[match.Index] == '+' ? 4 : 3;
            MaskKeepingPrefixDigits(buffer, match.Index, match.Length, keepDigits);
        }

        return new string(buffer);
    }

    private static void MaskEmail(char[] buffer, int start, int length)
    {
        for (var i = 0; i < length; i++)
        {
            var c = buffer[start + i];
            if (c is not '@' and not '.')
            {
                buffer[start + i] = '*';
            }
        }
    }

    private static void MaskKeepingPrefixDigits(char[] buffer, int start, int length, int keepDigits)
    {
        var seenDigits = 0;
        for (var i = 0; i < length; i++)
        {
            var c = buffer[start + i];
            if (!char.IsDigit(c))
            {
                continue;
            }

            if (seenDigits < keepDigits)
            {
                seenDigits++;
            }
            else
            {
                buffer[start + i] = '*';
            }
        }
    }
}
