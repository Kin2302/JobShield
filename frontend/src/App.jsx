import React, { useState } from 'react';

const samples = [
  ['Có yêu cầu phí', 'Tuyển nhân viên hỗ trợ khách hàng. Ứng viên cần nộp phí hồ sơ trước khi nhận việc.'],
  ['Phủ định thu phí', 'Ứng viên không cần đóng phí hồ sơ trước khi nhận việc.'],
  ['Tin không khớp mẫu', 'Tuyển nhân viên bán hàng bán thời gian. Phỏng vấn trực tiếp tại cửa hàng.'],
];

export default function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function updateText(value) {
    setText(value);
    setResult(null);
    setError('');
  }

  async function analyze(event) {
    event.preventDefault();
    setResult(null);
    setError('');
    if (!text.trim()) {
      setError('Bạn hãy nhập nội dung tin tuyển dụng trước khi phân tích.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
        signal: AbortSignal.timeout(15000),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.title || 'Không thể phân tích. Vui lòng thử lại.');
      }
      setResult(data);
    } catch (cause) {
      setError(cause.name === 'TimeoutError'
        ? 'Yêu cầu quá thời gian chờ. Vui lòng thử lại.'
        : cause instanceof TypeError || cause instanceof SyntaxError
          ? 'Không kết nối được hệ thống. Vui lòng kiểm tra các dịch vụ đang chạy.'
          : cause.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <a className="brand" href="/" aria-label="JobShield — Trang chủ">
          <svg viewBox="0 0 32 36" fill="none" aria-hidden="true">
            <path d="M16 2 29 7v10c0 8-6 13-13 17C9 30 3 25 3 17V7L16 2Z" stroke="currentColor" strokeWidth="2.5" />
            <path d="m10 17 4 4 8-9" stroke="currentColor" strokeWidth="2.5" />
          </svg>
          JobShield<span className="brand-dot">.</span>
        </a>
        <span className="checkpoint">W03 / HELLO WORLD</span>
      </header>

      <main>
        <section className="intro">
          <p className="eyebrow">THÊM MỘT BƯỚC KIỂM TRA TRƯỚC KHI ỨNG TUYỂN</p>
          <h1>Đọc kỹ tin tuyển dụng.<br /><span>Nhìn rõ dấu hiệu.</span></h1>
          <p className="intro-copy">Dán nội dung tin để kiểm tra yêu cầu phí trước khi nhận việc và xem đoạn văn bản khớp quy tắc.</p>
        </section>

        <div className="workspace">
          <section className="panel input-panel" aria-labelledby="input-title">
            <div className="panel-heading"><span className="step">01</span><h2 id="input-title">Nội dung cần kiểm tra</h2></div>
            <form onSubmit={analyze} noValidate>
              <label htmlFor="recruitment-text">Tin tuyển dụng</label>
              <textarea id="recruitment-text" value={text} disabled={loading}
                onChange={event => updateText(event.target.value)}
                aria-describedby="input-help" aria-invalid={Boolean(error)}
                placeholder="Dán hoặc nhập nội dung tin tuyển dụng tại đây…" />
              <div className="field-meta"><span id="input-help">Nội dung chỉ được xử lý cho yêu cầu này.</span><span>{text.length} ký tự</span></div>
              <p className="sample-label">Thử nhanh với nội dung mẫu</p>
              <div className="samples">{samples.map(([label, value]) => (
                <button type="button" key={label} disabled={loading} onClick={() => updateText(value)}>{label}</button>
              ))}</div>
              <button className="submit" type="submit" disabled={loading}>
                {loading ? 'Đang phân tích…' : 'Phân tích nội dung'}<span aria-hidden="true">→</span>
              </button>
              {error && <p className="error" role="alert">{error}</p>}
            </form>
          </section>

          <section className="panel result-panel" aria-labelledby="result-title" aria-busy={loading}>
            <div className="panel-heading"><span className="step">02</span><h2 id="result-title">Kết quả phân tích</h2></div>
            <div aria-live="polite" aria-atomic="true">
              {loading ? <div className="empty"><span className="status-icon">…</span><h3>Đang kiểm tra nội dung</h3><p>Vui lòng chờ kết quả phân tích.</p></div>
                : result ? <div className="result">
                  <span className={result.signals.length ? 'badge detected' : 'badge neutral'}>{result.signals.length ? 'CÓ DẤU HIỆU KHỚP QUY TẮC' : 'CHƯA PHÁT HIỆN THEO QUY TẮC'}</span>
                  <h3>{result.message}</h3>
                  {result.signals.map((signal, index) => <article className="signal" key={index}>
                    <h4>{signal.name}</h4><p className="quote-label">Đoạn trích trong nội dung bạn gửi</p>
                    <blockquote>{signal.evidence}</blockquote>
                  </article>)}
                  {!result.signals.length && <p className="result-note">Kết quả này không bảo đảm tin tuyển dụng an toàn. Bạn nên tiếp tục kiểm tra thông tin nhà tuyển dụng.</p>}
                  <p className="version">Bộ xử lý: {result.baseline_version}</p>
                </div>
                  : <div className="empty"><span className="status-icon" aria-hidden="true">⌕</span><h3>{error ? 'Chưa có kết quả phân tích' : 'Sẵn sàng kiểm tra'}</h3><p>{error ? 'Hãy xử lý lỗi ở phần nhập và thử lại.' : 'Nhập nội dung hoặc chọn một mẫu bên trái, sau đó bấm phân tích.'}</p></div>}
            </div>
          </section>
        </div>

        <aside className="scope"><span className="scope-label">PHẠM VI BẢN KHỞI ĐỘNG</span><p>Baseline kiểm tra hai mẫu yêu cầu nộp/đóng phí hồ sơ trước khi nhận việc và loại trừ phủ định đơn giản. Có thể bỏ sót hoặc nhận sai ngữ cảnh; kết quả hỗ trợ bạn xem xét nội dung.</p></aside>
      </main>
      <footer><span>JobShield · Đồ án chuyên ngành</span><span>React → ASP.NET Core → FastAPI</span></footer>
    </div>
  );
}
