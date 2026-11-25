import React, { useLayoutEffect, useRef, useState } from 'react';
import HomePage from './HomePage.jsx';
import DetectiveLoading from './DetectiveLoading.jsx';
import ResultTree from './ResultTree.jsx';

const feedbackForm = {
  formUrl: import.meta.env.VITE_FEEDBACK_FORM_URL,
  labelEntry: import.meta.env.VITE_FEEDBACK_LABEL_ENTRY,
  codesEntry: import.meta.env.VITE_FEEDBACK_CODES_ENTRY,
};

function feedbackUrl(label, findings, { formUrl, labelEntry, codesEntry }) {
  if (!['suspicious', 'not_detected'].includes(label)) return null;
  if (!/^entry\.\d+$/.test(labelEntry) ||
      !/^entry\.\d+$/.test(codesEntry) ||
      labelEntry === codesEntry) return null;

  const url = URL.canParse(formUrl) ? new URL(formUrl) : null;
  if (url?.origin !== 'https://docs.google.com' ||
      url.username || url.password ||
      !/^\/forms\/d\/e\/[\w-]+\/viewform$/.test(url.pathname)) return null;

  const codes = ['G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08'].filter(code =>
    findings.some(finding => finding.code === code)
  );

  url.search = new URLSearchParams({
    [labelEntry]: label === 'suspicious' ? 'Đáng ngờ' : 'Chưa phát hiện',
    [codesEntry]: codes.join(', ') || 'Không có mã dấu hiệu',
  }).toString();
  url.hash = '';
  return url.href;
}

function validAnalysis(result, text) {
  if (!['suspicious', 'not_detected'].includes(result?.label) ||
      !Array.isArray(result.sentences) || !Array.isArray(result.findings) ||
      (result.label === 'suspicious') !== (result.findings.length > 0)) return false;

  const ids = new Set();
  let previousEnd = 0;
  for (const sentence of result.sentences) {
    if (!sentence || typeof sentence.id !== 'string' || !sentence.id || ids.has(sentence.id) ||
        !Number.isInteger(sentence.start) || !Number.isInteger(sentence.end) ||
        sentence.start < previousEnd || sentence.end <= sentence.start || sentence.end > text.length ||
        text.slice(sentence.start, sentence.end) !== sentence.text) return false;
    ids.add(sentence.id);
    previousEnd = sentence.end;
  }
  return ids.size > 0 && result.findings.every(finding =>
    typeof finding?.code === 'string' && Array.isArray(finding.evidenceSentenceIds) &&
    finding.evidenceSentenceIds.length > 0 && finding.evidenceSentenceIds.every(id => ids.has(id)));
}

export default function App() {
  const [screen, setScreen] = useState('home');
  const [text, setText] = useState('');
  const [caseTitle, setCaseTitle] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const main = useRef(null);
  const previousScreen = useRef(screen);
  const pending = useRef(false);

  useLayoutEffect(() => {
    if (screen === previousScreen.current) return;
    previousScreen.current = screen;
    main.current.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }, [screen]);

  function openInput(sample = '', title = '') {
    setCaseTitle(title);
    setText(sample);
    setError('');
    setResult(null);
    setScreen('input');
  }

  async function analyze(event) {
    event.preventDefault();
    if (!text.trim() || pending.current) return;
    pending.current = true;
    setError('');
    setScreen('loading');
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
        signal: AbortSignal.timeout(150000),
      });
      if (!response.ok) throw new Error('Chưa thể phân tích nội dung. Bạn có thể thử lại.');
      const analysis = await response.json();
      if (!validAnalysis(analysis, text)) throw new Error('Dịch vụ trả về kết quả không hợp lệ.');
      setResult(analysis);
      setScreen('result');
    } catch (cause) {
      const message = cause.name === 'TimeoutError' ? 'Dịch vụ phản hồi quá lâu. Bạn có thể thử lại.'
        : cause instanceof TypeError || cause instanceof SyntaxError ? 'Chưa nhận được kết quả từ dịch vụ. Bạn có thể thử lại.'
        : cause.message;
      setError(message);
      setScreen('input');
    } finally {
      pending.current = false;
    }
  }

  const feedbackHref = result && feedbackUrl(result.label, result.findings, feedbackForm);
  return (
    <>
      <a href="#content" className="skip-link">Đến nội dung chính</a>
      <header className={screen === 'home' ? 'site-header' : 'site-header story-header'}>
        <div className="header-inner">
          <button className="brand" type="button" disabled={screen === 'loading'}
            onClick={() => setScreen('home')} aria-label="JobShield — Trang chủ">
            <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 3H4v4m12-4h4v4M4 17v4h4m8 0h4v-4"/><circle cx="11" cy="11" r="4"/><path d="m14 14 4 4"/></svg> JobShield
          </button>
          {screen === 'home' ? (
            <button className="header-action" type="button" onClick={() => openInput()}>Vào công cụ <span aria-hidden="true">↗</span></button>
          ) : (
            <div className="story-progress" aria-label="Tiến trình kiểm tra"><div aria-hidden="true">{['input', 'loading', 'result'].map((s, i, all) => <i key={s} data-lit={i <= all.indexOf(screen)} />)}</div>{({input: 'Hồ sơ đến tay', loading: 'Đang điều tra', result: 'Bảng manh mối'})[screen]}</div>
          )}
        </div>
      </header>
      <main id="content" tabIndex={-1} ref={main}>
        {screen === 'home' && <HomePage onStart={openInput} />}
        {screen === 'input' && (
          <section className="entry page-shell">
            <h1>Hồ sơ đến tay</h1><div className="case-desk"><aside className="desk-note">Ghi chú của Soi<strong>{caseTitle ? 'Hồ sơ đã đến. Bạn kiểm tra lại nội dung nhé.' : 'Dán hồ sơ lên tờ giấy này để tôi xem nhé.'}</strong></aside>
            <form onSubmit={analyze}>
              <label htmlFor="input">{caseTitle || 'Tin tuyển dụng hoặc đoạn hội thoại'}</label>
              <p id="input-hint">Nội dung có thể được gửi đến Groq để tách câu (hoặc tự động tách cục bộ khi dự phòng). Hãy che thông tin cá nhân trước khi gửi.</p>
              <textarea id="input" value={text} aria-describedby="input-hint" autoComplete="off"
                placeholder="Dán nội dung vào đây…" onChange={event => { setText(event.target.value); setError(''); }} />
              {error && <p className="input-error" role="alert">{error}</p>}
              <div className="entry-actions">
                <button className="secondary" type="button" onClick={() => setScreen('home')}>Về trang chủ</button>
                <button className="primary" disabled={!text.trim()}>{error ? 'Thử lại' : 'Kiểm tra'} <span aria-hidden="true">→</span></button>
              </div>
            </form></div>
          </section>
        )}
        {screen === 'loading' && <DetectiveLoading text={text} />}
        {screen === 'result' && (
          <div className="page-shell result-page">
            <ResultTree caseTitle={caseTitle} text={text} label={result.label}
              findings={result.findings} sentences={result.sentences}
              explanations={result.explanations} cases={result.cases} possibleNextSteps={result.possibleNextSteps} />
            <div className="result-actions">
              <button type="button" className="primary" onClick={() => openInput()}>Kiểm tra nội dung khác</button>
              {feedbackHref && <a href={feedbackHref} target="_blank" rel="noopener noreferrer">Góp ý kết quả ↗</a>}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
