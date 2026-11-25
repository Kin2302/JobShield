import React, { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { samples } from './sampleFiles.js';
import { Detective } from './Narrator.jsx';
import './HomePage.css';

const kind = { job: 'Tin tuyển dụng', chat: 'Hội thoại tuyển dụng' };
const speaker = { cand: 'Ứng viên', rec: 'Bên tuyển dụng' };
const steps = [
  ['Dán nội dung', 'Dùng hồ sơ mẫu hoặc nhập tin tuyển dụng và hội thoại của bạn.'],
  ['Gửi kiểm tra', 'Thám tử Soi đọc hồ sơ trong khi hệ thống phân tích.'],
  ['Xem manh mối', 'Đối chiếu dấu hiệu với câu được đánh dấu trong văn bản gốc.'],
];

function SamplePreview({ sample, onReturn, onStart }) {
  const [line, setLine] = useState(0);
  const [reading, setReading] = useState(!window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const back = useRef(null);
  const stage = useRef(null);
  useLayoutEffect(() => {
    const desk = stage.current;
    function followLine() {
      const current = desk.querySelector('[aria-pressed="true"]');
      if (!current) return;
      const center = current.getBoundingClientRect().top - desk.getBoundingClientRect().top + current.offsetHeight / 2;
      const detective = desk.querySelector('aside');
      const offset = Math.min(desk.offsetHeight - detective.offsetHeight, center - detective.offsetHeight / 2);
      desk.style.setProperty('--reading-y', Math.max(0, offset) + 'px');
    }
    followLine();
    const observer = new ResizeObserver(followLine);
    observer.observe(desk);
    return () => observer.disconnect();
  }, [line]);
  useEffect(() => { back.current.focus({ preventScroll: true }); }, []);
  useEffect(() => {
    if (!reading) return;
    const timer = window.setTimeout(() => {
      if (line + 1 < sample.lines.length) setLine(line + 1);
      else setReading(false);
    }, 1600);
    return () => window.clearTimeout(timer);
  }, [sample, line, reading]);
  const rawText = sample.lines.map(item => item.who ? speaker[item.who] + ': ' + item.t : item.t).join('\n');
  return <article className="sample-preview">
    <button ref={back} className="secondary" onClick={onReturn}>← Trả về xấp hồ sơ</button>
    <div className="reading-stage" ref={stage}>
      <aside><p className="thought">{reading ? 'Để tôi đọc qua từng dòng…' : 'Bạn muốn kiểm tra hồ sơ này chứ?'}</p><Detective /></aside>
      <div className="sample-document"><small>{kind[sample.kind]}</small><h2>{sample.title}</h2><p>{sample.sub}</p>
        <div className={'sample-lines ' + sample.kind}>{sample.lines.map((item, i) =>
          <button key={i} className={item.who} aria-pressed={line === i} onClick={() => { setReading(false); setLine(i); }}>
            {item.who && <small>{speaker[item.who]}</small>}{item.t}
          </button>)}</div>
      </div>
    </div>
    <button className="primary" onClick={() => onStart(rawText, sample.title)}>Dùng hồ sơ này <span aria-hidden="true">→</span></button>
  </article>;
}

export default function HomePage({ onStart }) {
  const [active, setActive] = useState(null);
  const lastCard = useRef(null);
  const fan = useRef(null);
  useEffect(() => { if (!active && lastCard.current) fan.current?.querySelector('[data-id="' + lastCard.current + '"]')?.focus({ preventScroll: true }); }, [active]);
  return <div className="make-home page-shell">
    <section className="make-hero">
      <h1>Kiểm tra nội dung <em>tuyển dụng</em></h1>
      <p>Rút một hồ sơ từ xấp tin tuyển dụng và hội thoại, hoặc gửi nội dung của bạn để thám tử Soi tìm manh mối.</p>
      <button className="primary" onClick={() => onStart()}>Bắt đầu kiểm tra <span aria-hidden="true">→</span></button>
    </section>
    <section className="file-stage" aria-label="Xấp hồ sơ mẫu">
      {active ? <SamplePreview sample={active} onReturn={() => setActive(null)} onStart={onStart} />
        : <div className="file-fan" ref={fan}>{samples.map((s, i) => <button key={s.id} aria-label={'Rút ra: ' + kind[s.kind] + ' – ' + s.title}
          className="fan-paper" style={{ '--i': i, '--tilt': (i - 2.5) * 2.4 + 'deg', '--lift': Math.abs(i - 2.5) * 9 + 'px' }}
          onClick={() => { lastCard.current = s.id; setActive(s); }}
          data-id={s.id}>
          <small>{kind[s.kind]}</small><strong>{s.title}</strong><span>{s.sub}</span>
          <span className="paper-lines" aria-hidden="true">{[88,100,72,94,60].map(w => <i key={w} style={{width: w + '%'}} />)}</span>
          <b>Rút ra để điều tra →</b></button>)}</div>}
    </section>
    {!active && <p className="fan-caption">Chọn một hồ sơ trong xấp để rút ra</p>}
    <section className="how"><h2>Hoạt động trong 3 bước</h2><ol>{steps.map(([title, detail],i) =>
      <li key={title}><span className="how-icon" aria-hidden="true">{['▤','⌕','✓'][i]}</span><small>0{i+1}</small><h3>{title}</h3><p>{detail}</p></li>)}</ol>
      <button className="primary" onClick={() => onStart()}>Vào công cụ <span aria-hidden="true">→</span></button></section>
  </div>;
}
